"""
S3 storage service for HUB3660 session recordings.

This service handles uploading session recordings to S3 and generating
time-limited signed URLs for secure access.
"""

import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class RecordingStorageService:
    """
    Service for managing session recording storage in AWS S3.
    
    Handles uploading recordings from Zoom to S3 and generating
    time-limited signed URLs for authorized access.
    """
    
    def __init__(self):
        """Initialize S3 client with AWS credentials."""
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.region = settings.AWS_S3_REGION_NAME
        self.s3_client = None
        self._initialized = False
        
        # Only initialize if credentials are available
        if all([
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            settings.AWS_STORAGE_BUCKET_NAME
        ]):
            self._initialize_s3_client()
    
    def _initialize_s3_client(self):
        """Initialize S3 client and test connection."""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.region
            )
            
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self._initialized = True
            logger.info(f"Successfully connected to S3 bucket: {self.bucket_name}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            self._initialized = False
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"S3 bucket '{self.bucket_name}' not found")
            elif error_code == '403':
                logger.error(f"Access denied to S3 bucket '{self.bucket_name}'")
            else:
                logger.error(f"S3 connection error: {e}")
            self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure S3 client is initialized before use."""
        if not self._initialized:
            if not all([
                settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY,
                settings.AWS_STORAGE_BUCKET_NAME
            ]):
                raise ImproperlyConfigured(
                    "AWS credentials and bucket name must be configured for recording storage"
                )
            self._initialize_s3_client()
            
        if not self._initialized:
            raise ImproperlyConfigured("Failed to initialize S3 client")
    
    def upload_recording_from_url(self, recording_url: str, session_id: int, 
                                course_id: int) -> str:
        """
        Download recording from Zoom URL and upload to S3.
        
        Args:
            recording_url: Zoom recording download URL
            session_id: Session ID for organizing files
            course_id: Course ID for organizing files
            
        Returns:
            str: S3 object key for the uploaded recording
            
        Raises:
            Exception: If upload fails
        """
        self._ensure_initialized()
        
        import requests
        from urllib.parse import urlparse
        
        try:
            # Generate S3 object key with organized structure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = self._get_file_extension_from_url(recording_url)
            s3_key = f"recordings/course_{course_id}/session_{session_id}_{timestamp}{file_extension}"
            
            logger.info(f"Downloading recording from Zoom: {recording_url}")
            
            # Download recording from Zoom with streaming
            response = requests.get(recording_url, stream=True, timeout=300)
            response.raise_for_status()
            
            # Get content length for progress tracking
            content_length = response.headers.get('content-length')
            if content_length:
                content_length = int(content_length)
                logger.info(f"Recording size: {content_length / (1024*1024):.2f} MB")
            
            # Upload to S3 with multipart upload for large files
            logger.info(f"Uploading recording to S3: {s3_key}")
            
            # Set metadata for the recording
            metadata = {
                'session-id': str(session_id),
                'course-id': str(course_id),
                'upload-timestamp': datetime.now().isoformat(),
                'source': 'zoom-recording'
            }
            
            # Upload with private ACL and metadata
            self.s3_client.upload_fileobj(
                response.raw,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ACL': 'private',
                    'Metadata': metadata,
                    'ContentType': self._get_content_type(file_extension),
                    'CacheControl': 'max-age=86400',  # 24 hours cache
                    'ContentDisposition': f'inline; filename="session_{session_id}_recording{file_extension}"'
                }
            )
            
            logger.info(f"Successfully uploaded recording to S3: {s3_key}")
            return s3_key
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download recording from Zoom: {e}")
            raise Exception(f"Failed to download recording: {str(e)}")
        except ClientError as e:
            logger.error(f"Failed to upload recording to S3: {e}")
            raise Exception(f"Failed to upload recording to S3: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error uploading recording: {e}")
            raise
    
    def generate_signed_url(self, s3_key: str, expiration_hours: int = 24) -> str:
        """
        Generate a time-limited signed URL for accessing a recording.
        
        Args:
            s3_key: S3 object key for the recording
            expiration_hours: Hours until URL expires (default 24)
            
        Returns:
            str: Signed URL for accessing the recording
            
        Raises:
            Exception: If URL generation fails
        """
        self._ensure_initialized()
        
        try:
            expiration_seconds = expiration_hours * 3600
            
            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration_seconds
            )
            
            logger.info(f"Generated signed URL for {s3_key}, expires in {expiration_hours} hours")
            return signed_url
            
        except ClientError as e:
            logger.error(f"Failed to generate signed URL for {s3_key}: {e}")
            raise Exception(f"Failed to generate signed URL: {str(e)}")
    
    def delete_recording(self, s3_key: str) -> bool:
        """
        Delete a recording from S3.
        
        Args:
            s3_key: S3 object key for the recording to delete
            
        Returns:
            bool: True if deletion was successful
        """
        self._ensure_initialized()
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"Successfully deleted recording: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete recording {s3_key}: {e}")
            return False
    
    def get_recording_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a recording stored in S3.
        
        Args:
            s3_key: S3 object key for the recording
            
        Returns:
            Dict containing recording metadata, or None if not found
        """
        self._ensure_initialized()
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                'size': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {}),
                'etag': response.get('ETag', '').strip('"')
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.warning(f"Recording not found in S3: {s3_key}")
                return None
            else:
                logger.error(f"Failed to get recording metadata for {s3_key}: {e}")
                return None
    
    def list_course_recordings(self, course_id: int) -> list:
        """
        List all recordings for a specific course.
        
        Args:
            course_id: Course ID to list recordings for
            
        Returns:
            List of recording objects with metadata
        """
        self._ensure_initialized()
        
        try:
            prefix = f"recordings/course_{course_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            recordings = []
            for obj in response.get('Contents', []):
                recordings.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"')
                })
            
            logger.info(f"Found {len(recordings)} recordings for course {course_id}")
            return recordings
            
        except ClientError as e:
            logger.error(f"Failed to list recordings for course {course_id}: {e}")
            return []
    
    def _get_file_extension_from_url(self, url: str) -> str:
        """Extract file extension from URL, defaulting to .mp4."""
        from urllib.parse import urlparse
        import os
        
        parsed_url = urlparse(url)
        path = parsed_url.path
        _, ext = os.path.splitext(path)
        
        # Default to .mp4 if no extension found
        return ext if ext else '.mp4'
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get MIME type for file extension."""
        content_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.wmv': 'video/x-ms-wmv',
            '.flv': 'video/x-flv',
            '.webm': 'video/webm',
            '.mkv': 'video/x-matroska'
        }
        
        return content_types.get(file_extension.lower(), 'video/mp4')


# Global instance
recording_storage = RecordingStorageService()
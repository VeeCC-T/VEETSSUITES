"""
Zoom API service for HUB3660 course management.

This service handles Zoom meeting creation, participant registration,
and webhook processing for session recordings.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import requests
import jwt
import time
from django.conf import settings
from django.utils import timezone as django_timezone
from .models import Session
from .storage import recording_storage

logger = logging.getLogger(__name__)


class ZoomService:
    """
    Service class for interacting with Zoom API.
    
    Handles meeting creation, participant registration, and webhook processing
    for HUB3660 course sessions.
    """
    
    BASE_URL = "https://api.zoom.us/v2"
    
    def __init__(self):
        self.api_key = settings.ZOOM_API_KEY
        self.api_secret = settings.ZOOM_API_SECRET
        self.webhook_secret = settings.ZOOM_WEBHOOK_SECRET
        
        if not all([self.api_key, self.api_secret]):
            logger.warning("Zoom API credentials not configured")
    
    def _generate_jwt_token(self) -> str:
        """
        Generate JWT token for Zoom API authentication.
        
        Returns:
            str: JWT token for API authentication
        """
        payload = {
            'iss': self.api_key,
            'exp': int(time.time() + 3600)  # Token expires in 1 hour
        }
        
        token = jwt.encode(payload, self.api_secret, algorithm='HS256')
        return token
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated request to Zoom API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request payload for POST/PUT requests
            
        Returns:
            Dict containing API response
            
        Raises:
            Exception: If API request fails
        """
        if not self.api_key or not self.api_secret:
            raise Exception("Zoom API credentials not configured")
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self._generate_jwt_token()}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Zoom API request failed: {e}")
            raise Exception(f"Zoom API request failed: {str(e)}")
    
    def create_meeting(self, session: Session) -> Dict[str, Any]:
        """
        Create a Zoom meeting for a course session.
        
        Args:
            session: Session instance to create meeting for
            
        Returns:
            Dict containing meeting details (id, join_url, etc.)
            
        Raises:
            Exception: If meeting creation fails
        """
        # Get the instructor's email (assuming they have a Zoom account)
        instructor_email = session.course.instructor.email
        
        meeting_data = {
            "topic": f"{session.course.title} - {session.title}",
            "type": 2,  # Scheduled meeting
            "start_time": session.scheduled_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration": 120,  # Default 2 hours
            "timezone": "UTC",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "watermark": False,
                "use_pmi": False,
                "approval_type": 0,  # Automatically approve
                "audio": "both",
                "auto_recording": "cloud",  # Enable cloud recording
                "enforce_login": False,
                "registrants_email_notification": True
            }
        }
        
        try:
            # Create meeting using instructor's email as user ID
            response = self._make_request('POST', f'/users/{instructor_email}/meetings', meeting_data)
            
            # Update session with Zoom meeting details
            session.zoom_meeting_id = str(response['id'])
            session.zoom_join_url = response['join_url']
            session.save(update_fields=['zoom_meeting_id', 'zoom_join_url'])
            
            logger.info(f"Created Zoom meeting {response['id']} for session {session.id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create Zoom meeting for session {session.id}: {e}")
            raise
    
    def register_participant(self, session: Session, user_email: str, user_name: str) -> Dict[str, Any]:
        """
        Register a participant for a Zoom meeting.
        
        Args:
            session: Session with Zoom meeting
            user_email: Participant's email address
            user_name: Participant's full name
            
        Returns:
            Dict containing registration details
            
        Raises:
            Exception: If registration fails
        """
        if not session.zoom_meeting_id:
            raise Exception("Session does not have a Zoom meeting ID")
        
        registration_data = {
            "email": user_email,
            "first_name": user_name.split()[0] if user_name else "Student",
            "last_name": " ".join(user_name.split()[1:]) if len(user_name.split()) > 1 else "",
            "auto_approve": True
        }
        
        try:
            response = self._make_request(
                'POST', 
                f'/meetings/{session.zoom_meeting_id}/registrants',
                registration_data
            )
            
            logger.info(f"Registered {user_email} for Zoom meeting {session.zoom_meeting_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to register {user_email} for meeting {session.zoom_meeting_id}: {e}")
            raise
    
    def get_meeting_recordings(self, meeting_id: str) -> Dict[str, Any]:
        """
        Get recordings for a completed meeting.
        
        Args:
            meeting_id: Zoom meeting ID
            
        Returns:
            Dict containing recording details
            
        Raises:
            Exception: If request fails
        """
        try:
            response = self._make_request('GET', f'/meetings/{meeting_id}/recordings')
            logger.info(f"Retrieved recordings for meeting {meeting_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get recordings for meeting {meeting_id}: {e}")
            raise
    
    def process_recording_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Process Zoom webhook for recording completion.
        
        Args:
            webhook_data: Webhook payload from Zoom
            
        Returns:
            bool: True if processed successfully
        """
        try:
            event = webhook_data.get('event')
            if event != 'recording.completed':
                logger.info(f"Ignoring webhook event: {event}")
                return True
            
            payload = webhook_data.get('payload', {})
            object_data = payload.get('object', {})
            meeting_id = str(object_data.get('id', ''))
            
            if not meeting_id:
                logger.error("No meeting ID in webhook payload")
                return False
            
            # Find session by meeting ID
            try:
                session = Session.objects.get(zoom_meeting_id=meeting_id)
            except Session.DoesNotExist:
                logger.error(f"No session found for meeting ID {meeting_id}")
                return False
            
            # Get recording files
            recording_files = object_data.get('recording_files', [])
            if not recording_files:
                logger.warning(f"No recording files for meeting {meeting_id}")
                return True
            
            # Find the main recording file (usually MP4)
            main_recording = None
            for file_data in recording_files:
                if file_data.get('file_type') == 'MP4' and file_data.get('recording_type') == 'shared_screen_with_speaker_view':
                    main_recording = file_data
                    break
            
            if not main_recording:
                # Fallback to first MP4 file
                for file_data in recording_files:
                    if file_data.get('file_type') == 'MP4':
                        main_recording = file_data
                        break
            
            if main_recording:
                download_url = main_recording.get('download_url')
                if download_url:
                    try:
                        # Upload recording to S3
                        s3_key = recording_storage.upload_recording_from_url(
                            download_url,
                            session.id,
                            session.course.id
                        )
                        
                        # Update session with S3 key
                        session.s3_recording_key = s3_key
                        session.recording_url = download_url  # Keep original URL as backup
                        session.save(update_fields=['s3_recording_key', 'recording_url'])
                        
                        logger.info(f"Updated session {session.id} with S3 recording key: {s3_key}")
                        
                    except Exception as e:
                        logger.error(f"Failed to upload recording to S3 for session {session.id}: {e}")
                        # Fallback to storing the original URL
                        session.recording_url = download_url
                        session.save(update_fields=['recording_url'])
                        logger.info(f"Stored original recording URL as fallback for session {session.id}")
                else:
                    logger.warning(f"No download URL in recording data for meeting {meeting_id}")
            else:
                logger.warning(f"No suitable recording file found for meeting {meeting_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process recording webhook: {e}")
            return False
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Zoom webhook signature.
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook headers
            
        Returns:
            bool: True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Zoom webhook secret not configured")
            return True  # Skip verification if not configured
        
        try:
            import hmac
            import hashlib
            
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {e}")
            return False


# Global instance
zoom_service = ZoomService()
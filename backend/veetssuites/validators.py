"""
Custom validators for enhanced security.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
    Custom password validator that enforces strong password requirements.
    """
    
    def validate(self, password, user=None):
        """
        Validate that the password meets security requirements.
        """
        errors = []
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append(_('Password must contain at least one uppercase letter.'))
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append(_('Password must contain at least one lowercase letter.'))
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            errors.append(_('Password must contain at least one digit.'))
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(_('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).'))
        
        # Check for common patterns
        if self._has_common_patterns(password):
            errors.append(_('Password contains common patterns that are not secure.'))
        
        # Check if password is too similar to common words
        if self._is_too_common(password):
            errors.append(_('Password is too common. Please choose a more unique password.'))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters including "
            "uppercase and lowercase letters, digits, and special characters."
        )
    
    def _has_common_patterns(self, password):
        """
        Check for common insecure patterns.
        """
        # Check for sequential characters
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            return True
        
        # Check for repeated characters (more than 2 in a row)
        if re.search(r'(.)\1{2,}', password):
            return True
        
        # Check for keyboard patterns
        keyboard_patterns = [
            'qwerty', 'asdf', 'zxcv', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
            '1234567890', '0987654321'
        ]
        
        password_lower = password.lower()
        for pattern in keyboard_patterns:
            if pattern in password_lower or pattern[::-1] in password_lower:
                return True
        
        return False
    
    def _is_too_common(self, password):
        """
        Check if password is in list of common passwords.
        """
        common_passwords = [
            'password', 'password123', 'admin', 'administrator', 'root',
            'user', 'guest', 'test', 'demo', 'welcome', 'login',
            'passw0rd', 'p@ssword', 'p@ssw0rd', '12345678', '87654321',
            'qwerty123', 'abc123', 'password1', 'password!', 'Password1',
            'Password123', 'Password!', 'letmein', 'monkey', 'dragon',
            'sunshine', 'princess', 'football', 'baseball', 'welcome123'
        ]
        
        return password.lower() in [pwd.lower() for pwd in common_passwords]


class EmailValidator:
    """
    Enhanced email validator with additional security checks.
    """
    
    def __init__(self):
        self.disposable_domains = [
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'tempmail.org', 'throwaway.email', 'temp-mail.org',
            'yopmail.com', 'maildrop.cc', 'sharklasers.com'
        ]
    
    def validate(self, email):
        """
        Validate email address with security checks.
        """
        errors = []
        
        # Basic format validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append(_('Enter a valid email address.'))
            return errors
        
        # Check for disposable email domains
        domain = email.split('@')[1].lower()
        if domain in self.disposable_domains:
            errors.append(_('Disposable email addresses are not allowed.'))
        
        # Check for suspicious patterns
        if self._has_suspicious_patterns(email):
            errors.append(_('Email address contains suspicious patterns.'))
        
        return errors
    
    def _has_suspicious_patterns(self, email):
        """
        Check for suspicious email patterns.
        """
        local_part = email.split('@')[0]
        
        # Check for excessive dots or special characters
        if local_part.count('.') > 3:
            return True
        
        # Check for suspicious character sequences
        suspicious_patterns = ['admin', 'test', 'noreply', 'no-reply', 'support']
        for pattern in suspicious_patterns:
            if pattern in local_part.lower():
                return True
        
        return False


class FileUploadValidator:
    """
    Validator for file uploads with security checks.
    """
    
    def __init__(self, allowed_extensions=None, max_size=None):
        self.allowed_extensions = allowed_extensions or ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        self.max_size = max_size or 10 * 1024 * 1024  # 10MB default
        
        # Dangerous file extensions that should never be allowed
        self.dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
            '.jar', '.php', '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl',
            '.sh', '.ps1', '.msi', '.deb', '.rpm', '.dmg', '.app'
        ]
    
    def validate(self, uploaded_file):
        """
        Validate uploaded file for security.
        """
        errors = []
        
        # Check file size
        if uploaded_file.size > self.max_size:
            errors.append(_(f'File size exceeds maximum allowed size of {self.max_size / (1024*1024):.1f}MB.'))
        
        # Check file extension
        file_extension = self._get_file_extension(uploaded_file.name)
        
        if file_extension.lower() in self.dangerous_extensions:
            errors.append(_('File type is not allowed for security reasons.'))
        
        if file_extension.lower() not in [ext.lower() for ext in self.allowed_extensions]:
            errors.append(_(f'File type {file_extension} is not allowed. Allowed types: {", ".join(self.allowed_extensions)}'))
        
        # Check for suspicious file names
        if self._has_suspicious_filename(uploaded_file.name):
            errors.append(_('File name contains suspicious characters.'))
        
        # Validate file content (basic check)
        if self._has_suspicious_content(uploaded_file):
            errors.append(_('File content appears to be suspicious.'))
        
        return errors
    
    def _get_file_extension(self, filename):
        """
        Get file extension from filename.
        """
        return '.' + filename.split('.')[-1] if '.' in filename else ''
    
    def _has_suspicious_filename(self, filename):
        """
        Check for suspicious characters in filename.
        """
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return True
        
        # Check for null bytes or control characters
        if '\x00' in filename or any(ord(c) < 32 for c in filename if c != '\t'):
            return True
        
        # Check for excessively long filenames
        if len(filename) > 255:
            return True
        
        return False
    
    def _has_suspicious_content(self, uploaded_file):
        """
        Basic check for suspicious file content.
        """
        try:
            # Read first 1024 bytes to check for executable signatures
            uploaded_file.seek(0)
            header = uploaded_file.read(1024)
            uploaded_file.seek(0)  # Reset file pointer
            
            # Check for common executable signatures
            executable_signatures = [
                b'MZ',  # Windows PE
                b'\x7fELF',  # Linux ELF
                b'\xca\xfe\xba\xbe',  # Java class file
                b'PK\x03\x04',  # ZIP (could contain executables)
            ]
            
            for signature in executable_signatures:
                if header.startswith(signature):
                    return True
            
            # Check for script content in supposedly safe files
            if b'<script' in header.lower() or b'javascript:' in header.lower():
                return True
            
        except Exception:
            # If we can't read the file, consider it suspicious
            return True
        
        return False


class InputSanitizer:
    """
    Utility class for sanitizing user input.
    """
    
    @staticmethod
    def sanitize_html(text):
        """
        Remove potentially dangerous HTML content.
        """
        if not text:
            return text
        
        # Remove script tags and their content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove dangerous attributes
        dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur']
        for attr in dangerous_attrs:
            text = re.sub(rf'{attr}\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        
        # Remove javascript: and data: URLs
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'data:', '', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def sanitize_sql(text):
        """
        Basic SQL injection prevention.
        """
        if not text:
            return text
        
        # Remove common SQL injection patterns
        dangerous_patterns = [
            r'union\s+select', r'drop\s+table', r'delete\s+from',
            r'insert\s+into', r'update\s+set', r'exec\s*\(',
            r'sp_executesql', r'xp_cmdshell', r'--', r'/\*', r'\*/',
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitize filename to prevent path traversal and other attacks.
        """
        if not filename:
            return filename
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove null bytes and control characters
        filename = ''.join(c for c in filename if ord(c) >= 32)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return filename
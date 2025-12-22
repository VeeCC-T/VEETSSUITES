from django.db import models
from django.conf import settings
from accounts.models import User


class Portfolio(models.Model):
    """
    Portfolio model for storing user CV/resume information.
    
    Stores the uploaded CV file and parsed content in JSON format.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='portfolio',
        help_text="The user who owns this portfolio"
    )
    cv_file = models.FileField(
        upload_to='portfolios/',
        help_text="Uploaded CV file (PDF format, max 10MB)"
    )
    parsed_content = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parsed CV content in structured JSON format"
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this portfolio is publicly accessible"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return f"Portfolio for {self.user.email}"

    def get_public_url(self):
        """Generate public URL for this portfolio"""
        return f"/portfolio/{self.user.id}/"

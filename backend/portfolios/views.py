from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from .models import Portfolio
from .serializers import (
    PortfolioSerializer,
    PortfolioCreateSerializer,
    PortfolioUpdateSerializer
)
from .services import parse_cv
from accounts.models import User


class PortfolioUploadView(generics.CreateAPIView):
    """
    POST /api/portfolio/upload/
    
    Upload a new CV file and create a portfolio.
    Requires authentication.
    """
    serializer_class = PortfolioCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        # Check if user already has a portfolio
        if hasattr(request.user, 'portfolio'):
            return Response(
                {"error": "Portfolio already exists. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create portfolio for the authenticated user
        portfolio = serializer.save(user=request.user)
        
        # Parse the CV content
        try:
            cv_file = portfolio.cv_file
            parsed_content = parse_cv(cv_file)
            portfolio.parsed_content = parsed_content
            portfolio.save()
        except Exception as e:
            # If parsing fails, log the error but don't fail the upload
            # The CV file is still stored, just without parsed content
            portfolio.parsed_content = {
                'error': f'Failed to parse CV: {str(e)}',
                'raw_text': ''
            }
            portfolio.save()
        
        # Return the created portfolio
        response_serializer = PortfolioSerializer(
            portfolio,
            context={'request': request}
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class PortfolioDetailView(generics.RetrieveAPIView):
    """
    GET /api/portfolio/{user_id}/
    
    Get portfolio data for a specific user.
    Public portfolios can be accessed without authentication.
    Private portfolios require authentication and ownership.
    """
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        portfolio = get_object_or_404(Portfolio, user=user)

        # Check if portfolio is public or if user is the owner
        if not portfolio.is_public:
            if not self.request.user.is_authenticated:
                self.permission_denied(
                    self.request,
                    message="This portfolio is private. Please log in."
                )
            if self.request.user != portfolio.user:
                self.permission_denied(
                    self.request,
                    message="You do not have permission to view this portfolio."
                )

        return portfolio


class PortfolioUpdateView(generics.UpdateAPIView):
    """
    PUT /api/portfolio/{user_id}/
    
    Update an existing portfolio.
    Requires authentication and ownership.
    """
    serializer_class = PortfolioUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        portfolio = get_object_or_404(Portfolio, user=user)

        # Check if user is the owner
        if self.request.user != portfolio.user:
            self.permission_denied(
                self.request,
                message="You do not have permission to update this portfolio."
            )

        return portfolio

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Check if CV file was updated
        cv_file_updated = 'cv_file' in request.data
        
        # Save the updated portfolio
        portfolio = serializer.save()
        
        # If CV file was updated, parse it
        if cv_file_updated:
            try:
                cv_file = portfolio.cv_file
                parsed_content = parse_cv(cv_file)
                portfolio.parsed_content = parsed_content
                portfolio.save()
            except Exception as e:
                # If parsing fails, log the error but don't fail the update
                portfolio.parsed_content = {
                    'error': f'Failed to parse CV: {str(e)}',
                    'raw_text': ''
                }
                portfolio.save()
        
        # Return the updated portfolio
        response_serializer = PortfolioSerializer(
            portfolio,
            context={'request': request}
        )
        return Response(response_serializer.data)


class PortfolioDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/portfolio/{user_id}/
    
    Delete a portfolio.
    Requires authentication and ownership.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        portfolio = get_object_or_404(Portfolio, user=user)

        # Check if user is the owner
        if self.request.user != portfolio.user:
            self.permission_denied(
                self.request,
                message="You do not have permission to delete this portfolio."
            )

        return portfolio

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Delete the CV file from storage
        if instance.cv_file:
            try:
                instance.cv_file.delete(save=False)
            except Exception:
                # If file deletion fails, continue with portfolio deletion
                # The file will be orphaned but the database record will be removed
                pass
        
        # Delete the portfolio
        instance.delete()
        
        return Response(
            {"message": "Portfolio deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class MyPortfolioView(generics.RetrieveAPIView):
    """
    GET /api/portfolio/me/
    
    Get the authenticated user's portfolio.
    Requires authentication.
    """
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        portfolio = get_object_or_404(Portfolio, user=self.request.user)
        return portfolio

# Portfolio Subsite Backend Implementation

## Overview

This document describes the implementation of the Portfolio subsite backend for the VEETSSUITES platform. The Portfolio module allows users to upload their CV/resume in PDF format, which is then parsed and stored in a structured format.

## Implementation Summary

### Task 8.1: Portfolio Model and API ✓

**Completed Components:**

1. **Django App**: Created `portfolios` app
2. **Portfolio Model** (`portfolios/models.py`):
   - OneToOne relationship with User
   - FileField for CV storage
   - JSONField for parsed content
   - Boolean flag for public/private access
   - Timestamps for creation and updates

3. **Serializers** (`portfolios/serializers.py`):
   - `PortfolioSerializer`: Full portfolio data serialization
   - `PortfolioCreateSerializer`: Simplified creation
   - `PortfolioUpdateSerializer`: Update operations
   - File validation (PDF only, max 10MB)

4. **API Endpoints** (`portfolios/views.py`):
   - `POST /api/portfolio/upload/` - Upload new CV
   - `GET /api/portfolio/me/` - Get authenticated user's portfolio
   - `GET /api/portfolio/{user_id}/` - Get portfolio by user ID (public or owned)
   - `PUT /api/portfolio/{user_id}/update/` - Update portfolio
   - `DELETE /api/portfolio/{user_id}/delete/` - Delete portfolio

5. **S3 Storage Configuration**:
   - Integrated `django-storages` for S3 support
   - Falls back to local storage for development
   - Configured in `settings.py` with environment variables

6. **Admin Interface** (`portfolios/admin.py`):
   - Portfolio management in Django admin
   - Read-only parsed content display
   - Search and filter capabilities

### Task 8.2: CV Parsing Functionality ✓

**Completed Components:**

1. **CV Parser Service** (`portfolios/services.py`):
   - `CVParserService` class for PDF text extraction
   - Uses PyPDF2 for PDF reading
   - Extracts structured content:
     - Raw text
     - Contact information (email, phone, LinkedIn, GitHub)
     - Sections (Experience, Education, Skills, etc.)
     - Skills list
     - Education entries
     - Work experience

2. **Parsing Features**:
   - Email extraction using regex
   - Phone number extraction (multiple formats)
   - Social media profile detection
   - Section header recognition
   - Skill extraction
   - Education and experience parsing

3. **Integration with Views**:
   - Automatic parsing on upload
   - Re-parsing on CV update
   - Graceful error handling (stores error in parsed_content)

4. **Testing** (`portfolios/tests.py`):
   - 9 comprehensive test cases
   - All tests passing
   - Coverage includes:
     - Authentication requirements
     - File upload validation
     - Public/private access control
     - CRUD operations
     - Permission checks

## API Endpoints

### Upload Portfolio
```
POST /api/portfolio/upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- cv_file: PDF file (required, max 10MB)
- is_public: boolean (optional, default: false)

Response: 201 Created
{
  "id": 1,
  "user": {...},
  "cv_file": "url",
  "cv_file_url": "full_url",
  "parsed_content": {...},
  "is_public": true,
  "public_url": "/portfolio/1/",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Get My Portfolio
```
GET /api/portfolio/me/
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "user": {...},
  "cv_file_url": "url",
  "parsed_content": {...},
  "is_public": true,
  ...
}
```

### Get Portfolio by User ID
```
GET /api/portfolio/{user_id}/
Authorization: Bearer <token> (optional for public portfolios)

Response: 200 OK
{
  "id": 1,
  "user": {...},
  "cv_file_url": "url",
  "parsed_content": {...},
  ...
}
```

### Update Portfolio
```
PUT /api/portfolio/{user_id}/update/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- cv_file: PDF file (optional)
- is_public: boolean (optional)

Response: 200 OK
{
  "id": 1,
  "user": {...},
  "cv_file_url": "url",
  "parsed_content": {...},
  ...
}
```

### Delete Portfolio
```
DELETE /api/portfolio/{user_id}/delete/
Authorization: Bearer <token>

Response: 204 No Content
{
  "message": "Portfolio deleted successfully"
}
```

## Parsed Content Structure

The `parsed_content` JSONField contains:

```json
{
  "raw_text": "Full extracted text from PDF",
  "sections": {
    "Experience": "Work experience content...",
    "Education": "Education content...",
    "Skills": "Skills content..."
  },
  "contact_info": {
    "email": "user@example.com",
    "phone": "+1234567890",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username"
  },
  "skills": ["Python", "Django", "React", ...],
  "education": [
    {"degree": "Bachelor of Science in Computer Science"}
  ],
  "experience": [
    {"description": "Software Engineer at Company..."}
  ]
}
```

## Access Control

1. **Upload**: Requires authentication
2. **View Public Portfolio**: No authentication required
3. **View Private Portfolio**: Requires authentication and ownership
4. **Update**: Requires authentication and ownership
5. **Delete**: Requires authentication and ownership

## File Storage

- **Development**: Local file storage in `media/portfolios/`
- **Production**: AWS S3 storage (when credentials configured)
- **File Naming**: Automatic unique naming to prevent conflicts
- **File Validation**: 
  - PDF format only
  - Maximum size: 10MB

## Database Schema

```sql
CREATE TABLE portfolios_portfolio (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT UNIQUE NOT NULL,
    cv_file VARCHAR(100) NOT NULL,
    parsed_content JSON NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Testing

All tests passing (9/9):
- ✓ Upload portfolio (authenticated)
- ✓ Upload portfolio (unauthenticated - fails)
- ✓ Upload duplicate portfolio (fails)
- ✓ Get public portfolio (no auth required)
- ✓ Get private portfolio (auth required)
- ✓ Update portfolio (owner only)
- ✓ Update portfolio (unauthorized - fails)
- ✓ Delete portfolio (owner only)
- ✓ Get my portfolio (authenticated)

## Requirements Validation

### Requirement 3.1 ✓
"WHEN a user uploads a CV file in PDF format THEN the Portfolio Subsite SHALL store the file and extract text content for display"
- ✓ PDF upload implemented
- ✓ File storage configured (local + S3)
- ✓ Text extraction using PyPDF2
- ✓ Structured content parsing

### Requirement 3.2 ✓
"WHEN a user views their portfolio page THEN the Frontend Application SHALL display the parsed CV content in a structured format"
- ✓ API returns parsed_content in structured JSON
- ✓ Sections, contact info, skills, education, experience extracted

### Requirement 3.3 ✓
"WHEN a visitor accesses a public portfolio URL THEN the Frontend Application SHALL display the portfolio without requiring authentication"
- ✓ Public portfolios accessible without auth
- ✓ Private portfolios require authentication

### Requirement 3.4 ✓
"WHEN a user updates their CV THEN the Portfolio Subsite SHALL replace the previous version and update the display"
- ✓ Update endpoint implemented
- ✓ CV re-parsing on update
- ✓ Previous file replaced

### Requirement 3.5 ✓
"THE Portfolio Subsite SHALL support CV files up to 10MB in size"
- ✓ File size validation (10MB limit)
- ✓ Validation in serializer

## Dependencies Added

- `django-storages>=1.14.0` - S3 storage backend
- `PyPDF2>=3.0.0` - PDF parsing (already in requirements)

## Configuration

Environment variables in `.env`:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
AWS_S3_REGION_NAME=us-east-1
```

## Next Steps

The Portfolio backend is complete and ready for frontend integration. The frontend should:

1. Create portfolio upload component with drag-and-drop
2. Display parsed CV content in structured format
3. Implement public portfolio view
4. Add edit/delete functionality

## Notes

- PyPDF2 shows a deprecation warning suggesting migration to `pypdf`. This can be addressed in a future update.
- CV parsing is basic and can be enhanced with more sophisticated NLP techniques
- Consider adding support for other file formats (DOCX) in future iterations

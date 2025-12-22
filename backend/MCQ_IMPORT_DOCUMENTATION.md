# MCQ Import Functionality Documentation

## Overview

The PHARMXAM system includes a comprehensive MCQ (Multiple Choice Question) import functionality that allows administrators to bulk import questions from CSV or JSON files. This feature is essential for quickly populating the question database with exam content.

## Features

### ✅ Implemented Features

1. **CSV Import Support**
   - Import questions from CSV files with proper validation
   - Supports all required question fields
   - Handles malformed CSV gracefully with error messages

2. **JSON Import Support**
   - Import questions from JSON files with structured data
   - Validates JSON format and structure
   - Provides detailed error messages for invalid JSON

3. **Admin-Only Access**
   - Only users with admin role can import questions
   - Proper permission checking and error handling
   - Non-admin users receive 403 Forbidden response

4. **File Validation**
   - Validates file type (only CSV and JSON allowed)
   - Checks file size (maximum 10MB)
   - Provides clear error messages for invalid files

5. **Data Validation**
   - Validates question format and required fields
   - Ensures correct answer options (A, B, C, D)
   - Validates difficulty levels (easy, medium, hard)
   - Handles missing or invalid data gracefully

6. **Bulk Creation**
   - Uses Django's `bulk_create` for efficient database operations
   - Returns count of successfully imported questions
   - Handles duplicate questions appropriately

## API Endpoint

### Import Questions
- **URL:** `/api/pharmxam/questions/import_questions/`
- **Method:** `POST`
- **Authentication:** Required (Admin only)
- **Content-Type:** `multipart/form-data`

#### Request Parameters
- `file`: The CSV or JSON file containing questions

#### Response Format
```json
{
    "message": "Successfully imported 25 questions.",
    "imported_count": 25
}
```

#### Error Response
```json
{
    "error": "Failed to import questions: [error details]"
}
```

## File Formats

### CSV Format
The CSV file must include the following columns in order:
- `text`: Question text
- `option_a`: Option A text
- `option_b`: Option B text
- `option_c`: Option C text
- `option_d`: Option D text
- `correct_answer`: Correct answer (A, B, C, or D)
- `category`: Question category (e.g., "Pharmacology", "Clinical Pharmacy")
- `difficulty`: Difficulty level (easy, medium, or hard)

#### CSV Example
```csv
text,option_a,option_b,option_c,option_d,correct_answer,category,difficulty
"What is aspirin used for?","Pain relief","Antibiotics","Antiviral","Antifungal","A","Pharmacology","easy"
"Which organ metabolizes drugs?","Heart","Liver","Kidney","Lung","B","Pharmacokinetics","medium"
```

### JSON Format
The JSON file should contain an array of question objects with the following structure:

```json
[
  {
    "text": "What is the half-life of a drug?",
    "option_a": "Time to reach steady state",
    "option_b": "Time for 50% elimination",
    "option_c": "Time for complete elimination",
    "option_d": "Time for absorption",
    "correct_answer": "B",
    "category": "Pharmacokinetics",
    "difficulty": "medium"
  }
]
```

## Usage Examples

### Using cURL
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@questions.csv" \
  http://localhost:8000/api/pharmxam/questions/import_questions/
```

### Using Python requests
```python
import requests

url = "http://localhost:8000/api/pharmxam/questions/import_questions/"
headers = {"Authorization": "Bearer YOUR_ADMIN_TOKEN"}
files = {"file": open("questions.csv", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

## Error Handling

The import functionality provides comprehensive error handling:

1. **File Type Validation**
   - Only CSV and JSON files are accepted
   - Returns 400 Bad Request for invalid file types

2. **File Size Validation**
   - Maximum file size is 10MB
   - Returns 400 Bad Request for oversized files

3. **Permission Validation**
   - Only admin users can import questions
   - Returns 403 Forbidden for non-admin users

4. **Data Format Validation**
   - Validates CSV headers and JSON structure
   - Returns 400 Bad Request with detailed error messages

5. **Database Errors**
   - Handles database constraint violations
   - Provides meaningful error messages

## Testing

The MCQ import functionality is thoroughly tested with:

1. **Unit Tests**
   - CSV import success scenarios
   - JSON import success scenarios
   - File validation tests
   - Permission validation tests
   - Error handling tests

2. **Integration Tests**
   - End-to-end import workflows
   - Database integrity checks
   - API response validation

3. **Sample Data**
   - Sample CSV and JSON files for testing
   - Management command for loading sample questions

## Management Commands

### Load Sample Questions
```bash
python manage.py load_sample_questions
```
This command loads 15 sample pharmacy questions for testing and development purposes.

## Security Considerations

1. **Authentication Required**
   - All import operations require valid authentication
   - JWT tokens are validated for each request

2. **Admin-Only Access**
   - Only users with admin role can import questions
   - Role-based access control is enforced

3. **File Size Limits**
   - Maximum file size of 10MB prevents abuse
   - Protects against memory exhaustion attacks

4. **Input Validation**
   - All input data is validated before database insertion
   - SQL injection protection through Django ORM

5. **Error Information**
   - Error messages don't expose sensitive system information
   - Appropriate HTTP status codes are returned

## Performance Considerations

1. **Bulk Operations**
   - Uses Django's `bulk_create` for efficient database insertion
   - Minimizes database round trips

2. **Memory Management**
   - Processes files in memory with size limits
   - Efficient CSV and JSON parsing

3. **Transaction Safety**
   - Import operations are wrapped in database transactions
   - Ensures data consistency on errors

## Future Enhancements

Potential improvements for the MCQ import functionality:

1. **Excel Support**
   - Add support for .xlsx files
   - Handle multiple worksheets

2. **Batch Processing**
   - Process very large files in batches
   - Progress tracking for long imports

3. **Duplicate Detection**
   - Advanced duplicate question detection
   - Options for handling duplicates (skip, update, error)

4. **Import History**
   - Track import operations and results
   - Audit trail for question sources

5. **Validation Rules**
   - Configurable validation rules
   - Custom category and difficulty validation

## Conclusion

The MCQ import functionality provides a robust, secure, and efficient way for administrators to populate the PHARMXAM question database. With comprehensive validation, error handling, and testing, it ensures data integrity while providing a smooth user experience.
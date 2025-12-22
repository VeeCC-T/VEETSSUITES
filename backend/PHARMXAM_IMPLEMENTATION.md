# PHARMXAM Backend Implementation

## Overview

The PHARMXAM backend provides a comprehensive examination system for pharmacy students to practice multiple-choice questions (MCQs). The system supports question management, exam sessions, answer tracking, and performance analytics.

## Models

### Question Model
- **Purpose**: Stores individual MCQ questions with four options and correct answer
- **Fields**:
  - `text`: Question content
  - `option_a`, `option_b`, `option_c`, `option_d`: Answer options
  - `correct_answer`: Correct option (A, B, C, or D)
  - `category`: Question category (e.g., Pharmacology, Clinical Pharmacy)
  - `difficulty`: Easy, Medium, or Hard
  - `created_at`, `updated_at`: Timestamps

### ExamAttempt Model
- **Purpose**: Tracks a student's exam session
- **Fields**:
  - `student`: Foreign key to User model
  - `questions`: Many-to-many relationship with Question through ExamAnswer
  - `score`: Number of correct answers
  - `total_questions`: Total questions in the exam
  - `status`: in_progress, completed, or abandoned
  - `started_at`, `completed_at`: Timestamps

### ExamAnswer Model
- **Purpose**: Records student's answer to a specific question
- **Fields**:
  - `attempt`: Foreign key to ExamAttempt
  - `question`: Foreign key to Question
  - `selected_answer`: Student's chosen option (A, B, C, or D)
  - `is_correct`: Automatically calculated based on correct answer
  - `answered_at`: Timestamp

## API Endpoints

### Questions Management
- `GET /api/pharmxam/questions/` - List questions (filtered by category/difficulty)
- `POST /api/pharmxam/questions/` - Create question (admin only)
- `GET /api/pharmxam/questions/{id}/` - Get specific question
- `PUT /api/pharmxam/questions/{id}/` - Update question (admin only)
- `DELETE /api/pharmxam/questions/{id}/` - Delete question (admin only)
- `POST /api/pharmxam/questions/import_questions/` - Import questions from CSV/JSON (admin only)

### Exam Management
- `POST /api/pharmxam/attempts/start_exam/` - Start new exam with randomized questions
- `GET /api/pharmxam/attempts/` - List user's exam attempts
- `GET /api/pharmxam/attempts/{id}/` - Get exam attempt details
- `POST /api/pharmxam/attempts/{id}/submit_answer/` - Submit answer to question
- `POST /api/pharmxam/attempts/{id}/complete_exam/` - Complete exam and calculate score
- `GET /api/pharmxam/attempts/{id}/review/` - Review completed exam with correct answers
- `GET /api/pharmxam/attempts/history/` - Get user's completed exam history
- `GET /api/pharmxam/attempts/stats/` - Get exam statistics (admin only)

## Key Features

### 1. Question Randomization
- Questions are randomly selected and ordered for each exam
- Supports filtering by category and difficulty
- Configurable number of questions per exam

### 2. Immediate Feedback
- Students receive immediate feedback after submitting each answer
- Shows correct/incorrect status and the correct answer
- Tracks performance in real-time

### 3. Score Calculation
- Automatic score calculation based on correct answers
- Percentage score calculation
- Performance breakdown by category and difficulty

### 4. Question Import
- Support for CSV and JSON file formats
- Bulk import functionality for administrators
- Validation of question format and data integrity

### 5. Exam Review
- Students can review completed exams
- Shows all questions with selected and correct answers
- Visual indicators for correct/incorrect responses

### 6. Analytics and Statistics
- Admin dashboard with exam statistics
- Performance breakdown by category and difficulty
- Average scores and completion rates

## Usage Examples

### Starting an Exam
```python
POST /api/pharmxam/attempts/start_exam/
{
    "category": "Pharmacology",
    "difficulty": "medium",
    "num_questions": 20
}
```

### Submitting an Answer
```python
POST /api/pharmxam/attempts/1/submit_answer/
{
    "question_id": 5,
    "selected_answer": "B"
}
```

### Completing an Exam
```python
POST /api/pharmxam/attempts/1/complete_exam/
```

### Importing Questions (CSV format)
```csv
text,option_a,option_b,option_c,option_d,correct_answer,category,difficulty
"What is aspirin's mechanism?","COX-1 only","COX-2 only","Both COX-1 and COX-2","Neither","C","Pharmacology","medium"
```

## Testing

The implementation includes comprehensive tests covering:
- Model creation and validation
- Score calculation logic
- API endpoint functionality
- Question import functionality
- Permission and access control

Run tests with:
```bash
python manage.py test exams
```

## Sample Data

Load sample questions for testing:
```bash
python manage.py load_sample_questions
```

This creates 15 sample pharmacy questions across different categories and difficulty levels.

## Admin Interface

The Django admin interface provides:
- Question management with preview and filtering
- Exam attempt monitoring with score visualization
- Answer tracking with correctness indicators
- Bulk actions for exam management

Access at: `/admin/exams/`

## Security Features

- Role-based access control (students can only access their own exams)
- Admin-only question management
- Input validation and sanitization
- Secure file upload for question import
- Protection against duplicate submissions

## Performance Considerations

- Database indexes on frequently queried fields
- Efficient query optimization with select_related
- Bulk operations for question import
- Pagination for large result sets

## Future Enhancements

- Timed exams with automatic submission
- Question difficulty adjustment based on performance
- Detailed analytics and reporting
- Integration with learning management systems
- Mobile app support
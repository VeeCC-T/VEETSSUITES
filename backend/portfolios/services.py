"""
CV Parsing Service

This module provides functionality to extract and parse text content from PDF CV files.
"""

import re
from PyPDF2 import PdfReader
from io import BytesIO


class CVParserService:
    """
    Service for parsing CV/resume PDF files.
    
    Extracts text content and structures it into sections.
    """

    def __init__(self, file):
        """
        Initialize the parser with a file.
        
        Args:
            file: Django UploadedFile or file-like object
        """
        self.file = file

    def extract_text(self):
        """
        Extract raw text from PDF file.
        
        Returns:
            str: Extracted text content
        """
        try:
            # Read the PDF file
            if hasattr(self.file, 'read'):
                # If it's a file-like object, read it into BytesIO
                pdf_content = self.file.read()
                # Reset file pointer for potential re-reading
                if hasattr(self.file, 'seek'):
                    self.file.seek(0)
                pdf_file = BytesIO(pdf_content)
            else:
                pdf_file = self.file

            # Create PDF reader
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")

    def parse_content(self):
        """
        Parse CV content into structured format.
        
        Returns:
            dict: Structured CV content with sections
        """
        # Extract raw text
        raw_text = self.extract_text()
        
        # Initialize structured content
        structured_content = {
            'raw_text': raw_text,
            'sections': {},
            'contact_info': {},
            'skills': [],
            'education': [],
            'experience': [],
        }

        # Parse contact information
        structured_content['contact_info'] = self._extract_contact_info(raw_text)
        
        # Parse sections
        structured_content['sections'] = self._extract_sections(raw_text)
        
        # Parse skills
        structured_content['skills'] = self._extract_skills(raw_text)
        
        # Parse education
        structured_content['education'] = self._extract_education(raw_text)
        
        # Parse experience
        structured_content['experience'] = self._extract_experience(raw_text)
        
        return structured_content

    def _extract_contact_info(self, text):
        """
        Extract contact information from CV text.
        
        Args:
            text (str): Raw CV text
            
        Returns:
            dict: Contact information
        """
        contact_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone numbers (various formats)
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = phones[0].strip()
        
        # Extract LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact_info['linkedin'] = linkedin.group(0)
        
        # Extract GitHub URL
        github_pattern = r'github\.com/[\w-]+'
        github = re.search(github_pattern, text, re.IGNORECASE)
        if github:
            contact_info['github'] = github.group(0)
        
        return contact_info

    def _extract_sections(self, text):
        """
        Extract major sections from CV text.
        
        Args:
            text (str): Raw CV text
            
        Returns:
            dict: Sections with their content
        """
        sections = {}
        
        # Common section headers
        section_patterns = [
            r'(?i)(summary|profile|objective)',
            r'(?i)(experience|employment|work history)',
            r'(?i)(education|academic)',
            r'(?i)(skills|technical skills|competencies)',
            r'(?i)(certifications|certificates)',
            r'(?i)(projects)',
            r'(?i)(awards|achievements|honors)',
            r'(?i)(publications)',
            r'(?i)(languages)',
        ]
        
        # Split text into lines
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern, line):
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = line
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections

    def _extract_skills(self, text):
        """
        Extract skills from CV text.
        
        Args:
            text (str): Raw CV text
            
        Returns:
            list: List of skills
        """
        skills = []
        
        # Look for skills section
        skills_pattern = r'(?i)skills?:?\s*(.+?)(?=\n\n|\n[A-Z]|$)'
        skills_match = re.search(skills_pattern, text, re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            # Split by common delimiters
            skill_items = re.split(r'[,;•\n]', skills_text)
            skills = [s.strip() for s in skill_items if s.strip()]
        
        return skills

    def _extract_education(self, text):
        """
        Extract education information from CV text.
        
        Args:
            text (str): Raw CV text
            
        Returns:
            list: List of education entries
        """
        education = []
        
        # Look for education section
        education_pattern = r'(?i)education:?\s*(.+?)(?=\n\n[A-Z]|experience|skills|$)'
        education_match = re.search(education_pattern, text, re.DOTALL)
        
        if education_match:
            education_text = education_match.group(1)
            
            # Look for degree patterns
            degree_pattern = r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.|MBA|Ph\.D\.)[^\n]*'
            degrees = re.findall(degree_pattern, education_text, re.IGNORECASE)
            
            for degree in degrees:
                education.append({
                    'degree': degree.strip()
                })
        
        return education

    def _extract_experience(self, text):
        """
        Extract work experience from CV text.
        
        Args:
            text (str): Raw CV text
            
        Returns:
            list: List of experience entries
        """
        experience = []
        
        # Look for experience section
        experience_pattern = r'(?i)(experience|employment|work history):?\s*(.+?)(?=\n\n[A-Z]|education|skills|$)'
        experience_match = re.search(experience_pattern, text, re.DOTALL)
        
        if experience_match:
            experience_text = experience_match.group(2)
            
            # Split by common job entry patterns (dates, company names, etc.)
            # This is a simplified approach - real-world parsing would be more sophisticated
            job_entries = re.split(r'\n(?=[A-Z][a-z]+ \d{4}|\d{4})', experience_text)
            
            for entry in job_entries:
                entry = entry.strip()
                if entry:
                    experience.append({
                        'description': entry
                    })
        
        return experience


def parse_cv(file):
    """
    Convenience function to parse a CV file.
    
    Args:
        file: Django UploadedFile or file-like object
        
    Returns:
        dict: Structured CV content
    """
    parser = CVParserService(file)
    return parser.parse_content()

# MyMCP Resume Builder

An intelligent resume builder that combines a JSON-based resume editor with AI assistance to help you create, format, and optimize professional resumes.

## Overview

MyMCP Resume Builder allows you to create and manage your resumes in a structured JSON format, while providing AI-powered suggestions to improve content and formatting. The system includes both a Python backend service for resume processing and a React-based web interface.

## Features

### Core Features
- **JSON-Based Resume Editor**: Edit your resume using a structured JSON format with syntax highlighting and validation
- **Live Preview**: See changes to your resume in real-time with a professional layout
- **PDF Export**: Generate a professionally formatted PDF of your resume
- **Multiple Resume Versions**: Create and manage multiple versions of your resume for different job applications
- **Auto-Save**: Changes are automatically saved to prevent data loss

### AI Assistant
- **AI-Powered Resume Improvements**: Get suggestions to enhance your resume content
- **Resume Analysis**: Receive feedback on your resume's strengths and weaknesses
- **Job-Specific Tailoring**: Customize your resume for specific job postings
- **Format Optimization**: Ensure your resume follows best practices for formatting

### Advanced Features
- **Context Uploads**: Upload job descriptions or other context files to improve AI assistance
- **Bold Text Formatting**: Highlight important information using Markdown-style bold formatting
- **Coursework Section**: Include relevant coursework in education entries
- **Structured Skills Format**: Organize skills by category for better readability

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+ and npm/yarn
- Internet connectivity for AI features

### Backend Setup
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/MyMCP-Resume.git
   cd MyMCP-Resume
   ```

2. Create a Python virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```
   python resume.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

## Usage

### Creating Your First Resume

1. Start with a sample template or create a new resume from scratch
2. Fill in your personal information, education, experience, projects, and skills
3. Use the AI assistant to request improvements or suggestions
4. Export your resume as a PDF when finished

### Using the AI Assistant

1. Type your question or request in the chat box
2. The AI will analyze your resume and provide suggestions
3. Review suggestions in the diff viewer
4. Apply or reject changes as needed

### Managing Multiple Versions

1. Create different versions for different job applications
2. Switch between versions using the sidebar
3. Duplicate and modify existing resumes for new applications
4. Each version is saved separately with its own history

### Resume JSON Structure

```json
{
  "name": "Your Name",
  "location": "City, State",
  "phone": "123-456-7890",
  "email": "your.email@example.com",
  "website": "yourwebsite.com",
  "technicalSkills": [
    "Languages: JavaScript, Python, Java",
    "Tools: Git, Docker, AWS"
  ],
  "education": [
    {
      "institution": "University Name",
      "location": "University City, State",
      "graduationDate": "Month Year",
      "degree": "Degree Name",
      "coursework": ["Relevant Course 1", "Relevant Course 2"]
    }
  ],
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "location": "Company City, State",
      "dateRange": "Start Date - End Date",
      "bullets": [
        "Accomplishment or responsibility description",
        "Another accomplishment with quantifiable results"
      ]
    }
  ],
  "projects": [
    {
      "name": "Project Name (Technology Stack)",
      "dateRange": "Month Year - Month Year",
      "bullets": [
        "Description of project purpose and your role",
        "Technical details and achievements"
      ]
    }
  ],
  "publications": [
    {
      "title": "Publication Title",
      "citation": "Journal/Conference, Year",
      "bullets": [
        "Brief description of publication",
        "Impact or significance"
      ]
    }
  ]
}
```

## Formatting Guidelines

### Bold Text
- Bold text is created by surrounding text with double asterisks: `**bold text**`
- Project names should have the title bolded but not technologies in parentheses
- Publication titles should be completely bolded
- Experience bullet points typically don't use bolding unless specifically emphasizing metrics
- Institution names in education may be bolded

### Resume Sections
- **Personal Information**: Always include name, location, phone, and email
- **Education**: List degrees in reverse chronological order, with optional coursework
- **Technical Skills**: Group by category (Languages, Frameworks, Tools, etc.)
- **Experience**: Focus on accomplishments with quantifiable results
- **Projects**: Highlight technical complexity and problem-solving
- **Publications**: Include formal citations and brief descriptions

## Architecture

The application consists of:

1. **Python Backend**:
   - FastMCP server for AI interactions
   - PDF generation and text processing
   - Resume validation and formatting

2. **React Frontend**:
   - Monaco code editor for JSON editing
   - MUI components for UI
   - Resume preview and formatting
   - AI chat interface

## Technologies Used

- **Backend**: Python, FastMCP, PyPDF2, python-docx
- **Frontend**: React, TypeScript, Material-UI, Monaco Editor
- **PDF Generation**: html2canvas, jsPDF
- **AI Integration**: OpenAI API

## License

[MIT License](LICENSE)

## Acknowledgments

- The project uses the [FastMCP](https://github.com/fastmcp) framework for AI interactions
- Resume templates inspired by best practices in professional resume design

# MyMCP Resume Builder

A personal project leveraging Model Context Protocol (MCP) servers to create an intelligent resume builder that helps me optimize my job applications through structured JSON and automated PDF generation.

## Overview

I built MyMCP Resume Builder to experiment with Model Context Protocol servers while creating a useful tool for my job hunt. The system is essentially a well-crafted prompt combined with tools that allow LLMs to intelligently modify resumes through a structured JSON format, then export them to PDF using a hand-crafted Cornell-style HTML template.

The core concept is simple but powerful: maintain your resume as a structured data object (JSON) that can be easily manipulated by AI systems, while ensuring consistent, professional formatting through a purpose-built HTML-to-PDF converter.

## How It Works

1. Your resume data is stored as a structured JSON object
2. You interact with the AI through natural language prompts
3. The AI can read, analyze, and suggest modifications to your resume JSON
4. Once satisfied, the JSON is converted to a professionally formatted PDF using a custom Cornell-style template

## Using with MCP-Compatible Applications

This tool works with any application that supports Model Context Protocol (MCP), allowing you to leverage AI assistance for resume optimization. For the best experience:

1. Use an MCP-compatible application with good HTML rendering support
2. Choose faster models like Gemini 2.0 Flash for real-time interactions
3. The HTML-to-PDF conversion works across platforms thanks to html2pdf.js

## User Context

You can customize the AI's understanding of your background and preferences by adding a `context.txt` file in the user context folder. This file should contain:

- Your career objectives and target roles
- Industry-specific terminology relevant to your field
- Preferences for resume style and emphasis
- Special formatting requirements

The AI will use this context to provide more tailored recommendations when helping you optimize your resume content and structure.

## Resume JSON Structure

The resume is stored in a standardized JSON format that captures all the essential elements:

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

## Formatting Features

- **Bold Text**: Use double asterisks for emphasis: `**bold text**` 
- **Cornell-Style Layout**: Clean, academic formatting inspired by Cornell University's resume templates
- **PDF Export**: High-quality, consistent PDF output regardless of device or browser
- **Responsive Design**: Proper spacing and layout that maintains professionalism

## Why This Approach?

1. **Separation of Content and Presentation**: By keeping resume data in JSON, I can focus on content quality while ensuring consistent formatting
2. **AI-Friendly Structure**: The structured format makes it easy for LLMs to understand and modify specific parts of the resume
3. **Version Control**: JSON files can be easily tracked with version control systems
4. **Tailored Applications**: I can quickly create job-specific versions by modifying the JSON and regenerating the PDF

This project demonstrates how LLMs can be effective tools for personal productivity when given the right interfaces and data structures to work with. It's a practical exploration of AI-assisted content creation within a controlled, structured environment.

import os
import json
import io
import PyPDF2
from docx import Document
from mcp.server.fastmcp import FastMCP

# Define directories
RESUME_DIR = "resumes"
USER_CONTEXT_DIR = "user_context"  # Directory for user context files

# Ensure directories exist
for directory in [RESUME_DIR, USER_CONTEXT_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Initialize FastMCP
mcp = FastMCP("Resume-MCP-Server")

# Text extraction constants
MAX_FILE_SIZE_BYTES = 2_000_000  # ~2 MB
TEXT_EXTENSIONS = {
    ".txt", ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".htm", ".css",
    ".scss", ".c", ".cpp", ".h", ".hpp", ".java", ".cs", ".json", ".xml",
    ".yaml", ".yml", ".md", ".sh", ".rb", ".go", ".rs", ".php"
}

# Resume validation function
def validate_resume_json(resume_data):
    """
    Validates that the resume JSON has the correct format according to ResumeBuilder requirements.
    
    Args:
        resume_data: Dictionary or JSON string containing resume data
    
    Returns:
        tuple: (is_valid, error_message)
            - is_valid (bool): True if the resume is valid, False otherwise
            - error_message (str): Description of the validation error if any, empty string if valid
    """
    # If a string is provided, try to parse it as JSON
    if isinstance(resume_data, str):
        try:
            resume_data = json.loads(resume_data)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
    
    # Check if resume_data is a dictionary
    if not isinstance(resume_data, dict):
        return False, "Resume data must be a JSON object (dictionary)"
    
    # Required fields for a valid resume
    required_fields = ['name', 'location', 'phone', 'email']
    
    # Check all required fields are present
    for field in required_fields:
        if field not in resume_data:
            return False, f"Missing required field: '{field}'"
        
        # Check that required fields are strings and not empty
        if not isinstance(resume_data[field], str) or not resume_data[field].strip():
            return False, f"Field '{field}' must be a non-empty string"
    
    # Validate optional array fields
    array_fields = {
        'technicalSkills': str,
        'education': dict,
        'experience': dict,
        'projects': dict,
        'publications': dict
    }
    
    for field, expected_type in array_fields.items():
        if field in resume_data:
            if not isinstance(resume_data[field], list):
                return False, f"Field '{field}' must be an array"
            
            # Check array elements
            for i, item in enumerate(resume_data[field]):
                if not isinstance(item, expected_type):
                    return False, f"Item {i} in '{field}' must be a {expected_type.__name__}"
    
    # Validate education structure
    if 'education' in resume_data:
        education_required = ['institution', 'location', 'graduationDate', 'degree']
        for i, edu in enumerate(resume_data['education']):
            for field in education_required:
                if field not in edu:
                    return False, f"Education item {i} is missing required field: '{field}'"
            
            # Validate coursework if present
            if 'coursework' in edu:
                if not isinstance(edu['coursework'], list):
                    return False, f"'coursework' in education item {i} must be an array"
                
                # Check that all coursework items are strings
                for j, course in enumerate(edu['coursework']):
                    if not isinstance(course, str):
                        return False, f"Course {j} in education item {i} must be a string"
    
    # Validate experience structure
    if 'experience' in resume_data:
        experience_required = ['title', 'company', 'location', 'dateRange']
        for i, exp in enumerate(resume_data['experience']):
            for field in experience_required:
                if field not in exp:
                    return False, f"Experience item {i} is missing required field: '{field}'"
            
            # Check bullets field
            if 'bullets' in exp and not isinstance(exp['bullets'], list):
                return False, f"'bullets' in experience item {i} must be an array"
            
            # Validate all bullets are strings if they exist
            if 'bullets' in exp and isinstance(exp['bullets'], list):
                for j, bullet in enumerate(exp['bullets']):
                    if not isinstance(bullet, str):
                        return False, f"Bullet {j} in experience item {i} must be a string"
    
    # Validate projects structure
    if 'projects' in resume_data:
        project_required = ['name', 'dateRange']
        for i, proj in enumerate(resume_data['projects']):
            for field in project_required:
                if field not in proj:
                    return False, f"Project item {i} is missing required field: '{field}'"
            
            # Check bullets field
            if 'bullets' in proj and not isinstance(proj['bullets'], list):
                return False, f"'bullets' in project item {i} must be an array"
            
            # Validate all bullets are strings if they exist
            if 'bullets' in proj and isinstance(proj['bullets'], list):
                for j, bullet in enumerate(proj['bullets']):
                    if not isinstance(bullet, str):
                        return False, f"Bullet {j} in project item {i} must be a string"
    
    # Validate publications structure
    if 'publications' in resume_data:
        publication_required = ['title', 'citation']
        for i, pub in enumerate(resume_data['publications']):
            for field in publication_required:
                if field not in pub:
                    return False, f"Publication item {i} is missing required field: '{field}'"
            
            # Check bullets field
            if 'bullets' in pub and not isinstance(pub['bullets'], list):
                return False, f"'bullets' in publication item {i} must be an array"
            
            # Validate all bullets are strings if they exist
            if 'bullets' in pub and isinstance(pub['bullets'], list):
                for j, bullet in enumerate(pub['bullets']):
                    if not isinstance(bullet, str):
                        return False, f"Bullet {j} in publication item {i} must be a string"
    
    # If all checks pass, the resume is valid
    return True, ""

# Text extraction functions
def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read().strip()
        except:
            return None

def extract_docx_text(file_path):
    document = Document(file_path)
    full_text = []
    for para in document.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_pdf_text(file_path):
    text = []
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page_text = reader.pages[page_num].extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def extract_text_from_file(file_path):
    """Extract text from various file types"""
    if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
        return f"File too large: {file_path}"
    
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    try:
        if file_extension in TEXT_EXTENSIONS:
            return read_text_file(file_path)
        elif file_extension == ".pdf":
            return extract_pdf_text(file_path)
        elif file_extension == ".docx":
            return extract_docx_text(file_path)
        else:
            return None
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def build_user_context():
    """Read user context directly from context.txt file"""
    context_file_path = os.path.join(USER_CONTEXT_DIR, "context.txt")
    
    # If the file doesn't exist, return empty context
    if not os.path.exists(context_file_path):
        return ""
    
    # Read the file content directly
    try:
        with open(context_file_path, 'r', encoding='utf-8') as f:
            context = f.read().strip()
    except UnicodeDecodeError:
        try:
            with open(context_file_path, 'r', encoding='latin-1') as f:
                context = f.read().strip()
        except Exception as e:
            print(f"Error reading context file: {str(e)}")
            context = ""
    except Exception as e:
        print(f"Error reading context file: {str(e)}")
        context = ""
    
    return context

# Initialize sample context files if directory is empty
def initialize_sample_context():
    if not os.listdir(USER_CONTEXT_DIR):
        # Create sample context file
        sample_context = """
John Doe is an experienced software engineer with expertise in Python, JavaScript, and cloud computing.

SKILLS:
Python
JavaScript
Cloud Computing
React
Node.js
SQL
Docker

CAREER GOALS:
Looking to transition into a leadership role in software engineering.

TARGET POSITIONS:
Senior Software Engineer
Tech Lead
Engineering Manager
"""
        with open(os.path.join(USER_CONTEXT_DIR, "context.txt"), "w") as f:
            f.write(sample_context.strip())

initialize_sample_context()

# --- Tool Implementations ---

@mcp.tool()
def compile_resume(json_input):
    """Validate a JSON resume and compile it into a single HTML file if valid
    
    This tool first validates if the JSON resume meets all requirements, then
    generates an HTML representation matching what the ResumeBuilder component displays.
    
    Args:
        json_input: A resume in JSON format (string or dictionary)
        
    Returns:
        A dictionary containing:
        - valid (bool): Whether the JSON is valid
        - message (str): Validation message if invalid
        - html (str): The compiled HTML if valid
    """
    try:
        # Handle input as either a string or dictionary
        if isinstance(json_input, str):
            # Parse string into dictionary if it's a string
            resume_data = json.loads(json_input)
        elif isinstance(json_input, dict):
            # Use the dictionary directly
            resume_data = json_input
        else:
            return {
                "valid": False,
                "message": f"Input must be a JSON string or dictionary, got {type(json_input)}",
                "html": None
            }
        
        # Validate the resume data
        is_valid, error_message = validate_resume_json(resume_data)
        
        if not is_valid:
            return {
                "valid": False,
                "message": f"JSON fails resume validation: {error_message}",
                "html": None
            }
        
        # If valid, compile the HTML
        html = generate_resume_html(resume_data)
        
        return {
            "valid": True,
            "message": "Resume compiled successfully",
            "html": html
        }
            
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "message": f"Invalid JSON format: {str(e)}",
            "html": None
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error compiling resume: {str(e)}",
            "html": None
        }

def generate_resume_html(resume_data):
    """Generate HTML for a resume that matches the ResumeBuilder component output"""
    # Start building HTML
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume</title>
    <style>
        body {
            font-family: "EB Garamond", "Garamond", serif;
            font-size: 10pt;
            line-height: 1;
            color: #000000;
            margin: 0;
            padding: 0.5in;
            width: 8.5in;
            height: 11in;
            box-sizing: border-box;
        }
        
        .resume {
            width: 100%;
            height: 100%;
        }
        
        /* Header */
        .header {
            text-align: center;
            padding-bottom: 4px;
            margin-bottom: 8px;
        }
        
        .header h1 {
            margin: 0;
            font-size: 16pt;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .contact-info {
            margin: 3px 0;
            font-size: 10pt;
            line-height: 1;
        }
        
        .contact-info span {
            margin: 0 5px;
        }
        
        .contact-info span:first-child {
            margin-left: 0;
        }
        
        .contact-info span:last-child {
            margin-right: 0;
        }
        
        /* Section */
        .section {
            margin-bottom: 10px;
        }
        
        .section h2 {
            text-transform: uppercase;
            border-bottom: 1px solid #000000;
            padding-bottom: 3px;
            margin-bottom: 6px;
            margin-top: 0;
            font-size: 10pt;
            letter-spacing: 0.5px;
            font-weight: 600;
        }
        
        /* Lists */
        ul {
            margin: 0;
            padding-left: 32px;
            list-style-type: disc;
            font-size: 10.5pt;
        }
        
        li {
            margin-bottom: 3px;
            line-height: 1;
            padding-left: 24px;
            text-indent: -24px;
        }
        
        strong {
            font-weight: 600;
        }
        
        /* Technical skills */
        .skills-container {
            display: grid;
            grid-template-columns: max-content 1fr;
            grid-gap: 2px 120px;
            width: 100%;
        }
        
        .skill-category-title {
            font-weight: 600;
            padding-right: 5px;
        }
        
        .skill-items {
            padding-left: 0;
        }
        
        /* Jobs, projects, publications */
        .job-title, .project-title, .publication-title {
            font-weight: normal;
            font-size: 10pt;
        }
        
        .date-range {
            float: right;
        }
        
        /* Education */
        .education-item {
            margin-bottom: 10px;
        }
        
        .coursework {
            margin-top: 3px;
            margin-bottom: 0;
        }
        
        /* Experience */
        .experience-item {
            margin-bottom: 12px;
        }
        
        /* Projects */
        .project-item {
            margin-bottom: 12px;
        }
        
        .project-subtitle {
            margin-top: 3px;
            margin-bottom: 3px;
        }
        
        /* Publications */
        .publication-item {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="resume">
"""
    
    # Add header section
    html += f"""
        <div class="header">
            <h1>{resume_data.get('name', '')}</h1>
            <p class="contact-info">
                <span>{resume_data.get('location', '')}</span> | <span>{resume_data.get('phone', '')}</span> | <span>{resume_data.get('email', '')}</span>
            </p>
            {f'<p style="margin: 2px 0; font-size: 10pt; line-height: 1">{resume_data.get("website", "")}</p>' if resume_data.get('website') else ''}
        </div>
"""
    
    # Add education section
    if 'education' in resume_data and resume_data['education']:
        html += """
        <div class="section">
            <h2>EDUCATION</h2>
            <div id="educationList">
"""
        for edu in resume_data['education']:
            html += f"""
                <div class="education-item">
                    <p>
                        <strong>{parse_bullet_text_html(edu.get('institution', ''))}</strong>, {parse_bullet_text_html(edu.get('location', ''))}
                        <span class="date-range">{parse_bullet_text_html(edu.get('graduationDate', ''))}</span><br>
                        {parse_bullet_text_html(edu.get('degree', ''))}{f" | GPA: {edu.get('gpa')}" if edu.get('gpa') else ""}
                    </p>
"""
            if 'coursework' in edu and edu['coursework']:
                html += f"""
                    <p class="coursework">
                        Relevant Coursework: {', '.join([parse_bullet_text_html(course) for course in edu['coursework']])}
                    </p>
"""
            html += """
                </div>
"""
        html += """
            </div>
        </div>
"""
    
    # Add technical skills section
    if 'technicalSkills' in resume_data and resume_data['technicalSkills']:
        html += """
        <div class="section">
            <h2>TECHNICAL SKILLS</h2>
            <div id="technicalSkillsList" class="skills-container">
"""
        # Group skills by category
        skills_by_category = {}
        for skill in resume_data['technicalSkills']:
            parts = skill.split(':')
            if len(parts) == 2:
                category = parts[0].strip()
                items = [item.strip() for item in parts[1].split(',')]
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].extend(items)
            else:
                if 'Other' not in skills_by_category:
                    skills_by_category['Other'] = []
                skills_by_category['Other'].append(skill)
        
        for category, skills in skills_by_category.items():
            html += f"""
                <div class="skill-category-title">{category}:</div>
                <div class="skill-items">{', '.join(skills)}</div>
"""
        html += """
            </div>
        </div>
"""
    
    # Add experience section
    if 'experience' in resume_data and resume_data['experience']:
        html += """
        <div class="section">
            <h2>EXPERIENCE</h2>
            <div id="experienceList">
"""
        for job in resume_data['experience']:
            html += f"""
                <div class="experience-item">
                    <p>
                        <strong>{parse_bullet_text_html(job.get('company', ''))}</strong>, <span class="job-title">{parse_bullet_text_html(job.get('title', ''))}</span>, {parse_bullet_text_html(job.get('location', ''))}
                        <span class="date-range">{parse_bullet_text_html(job.get('dateRange', ''))}</span>
                    </p>
"""
            if 'bullets' in job and job['bullets']:
                html += """
                    <ul>
"""
                for bullet in job['bullets']:
                    html += f"""
                        <li>{parse_bullet_text_html(bullet)}</li>
"""
                html += """
                    </ul>
"""
            html += """
                </div>
"""
        html += """
            </div>
        </div>
"""
    
    # Add projects section
    if 'projects' in resume_data and resume_data['projects']:
        html += """
        <div class="section">
            <h2>PROJECTS</h2>
            <div id="projectsList">
"""
        for project in resume_data['projects']:
            html += f"""
                <div class="project-item">
                    <p>
                        <span class="project-title">{parse_bullet_text_html(project.get('name', ''))}</span>
                        <span class="date-range">{parse_bullet_text_html(project.get('dateRange', ''))}</span>
                    </p>
"""
            if 'bullets' in project and project['bullets']:
                # First bullet becomes subtitle
                if project['bullets']:
                    html += f"""
                    <p class="project-subtitle">{parse_bullet_text_html(project['bullets'][0])}</p>
"""
                # Remaining bullets as list
                if len(project['bullets']) > 1:
                    html += """
                    <ul>
"""
                    for bullet in project['bullets'][1:]:
                        html += f"""
                        <li>{parse_bullet_text_html(bullet)}</li>
"""
                    html += """
                    </ul>
"""
            html += """
                </div>
"""
        html += """
            </div>
        </div>
"""
    
    # Add publications section
    if 'publications' in resume_data and resume_data['publications']:
        html += """
        <div class="section">
            <h2>PUBLICATIONS</h2>
            <div id="publicationsList">
"""
        for pub in resume_data['publications']:
            html += f"""
                <div class="publication-item">
                    <p>
                        <span class="publication-title">{parse_bullet_text_html(pub.get('title', ''))}</span>, {parse_bullet_text_html(pub.get('citation', ''))}
                    </p>
"""
            if 'bullets' in pub and pub['bullets']:
                html += """
                    <ul>
"""
                for bullet in pub['bullets']:
                    html += f"""
                        <li>{parse_bullet_text_html(bullet)}</li>
"""
                html += """
                    </ul>
"""
            html += """
                </div>
"""
        html += """
            </div>
        </div>
"""
    
    # Close HTML tags
    html += """
    </div>
</body>
</html>
"""
    
    return html

def parse_bullet_text_html(text):
    """Parse text with bold formatting (text inside ** will be bolded)"""
    if not isinstance(text, str):
        return str(text)
    
    if '**' not in text:
        return text
    
    # Replace **text** with <strong>text</strong>
    parts = []
    is_bold = False
    current_part = ""
    i = 0
    
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] == '**':
            # Add the current part to the result
            if current_part:
                parts.append(f"<strong>{current_part}</strong>" if is_bold else current_part)
                current_part = ""
            
            # Toggle bold state
            is_bold = not is_bold
            i += 2
        else:
            current_part += text[i]
            i += 1
    
    # Add the last part
    if current_part:
        parts.append(f"<strong>{current_part}</strong>" if is_bold else current_part)
    
    return "".join(parts)

@mcp.tool()
def get_user_context():
    """Retrieve context information for the user from context.txt file"""
    context = build_user_context()
    
    if not context:
        return {"error": "No user context found. Please create a context.txt file in the user_context directory."}
    
    return {"context": context}

# --- Prompt Implementation ---

@mcp.prompt()
def resume_edit_prompt(resume_json: str = None, instructions: str = None):
    """Create a prompt for editing a resume"""
    system_instructions = """
You are an AI assistant specifically designed to help users improve their résumés. 
Your task is to analyze the user's resume (provided as JSON) and respond to their questions or requests to modify the resume.

IMPORTANT: Instead of using tools to modify a resume, simply return the corrected resume in valid JSON format.

When suggesting modifications:
1. Analyze the user's instructions and the provided resume JSON
2. Provide the corrected/modified resume JSON directly in your response as a code block
3. After modifying the resume, ALWAYS use the compile_resume tool to validate and compile the updated JSON
4. Include both the JSON and the compiled HTML in your response to the user
5. Explain what changes you made and why they improve the resume

IMPORTANT: Your workflow should be:
1. Show the corrected JSON in a properly formatted code block:

```json
{
  "name": "John Doe",
  "location": "San Francisco, CA",
  "phone": "123-456-7890",
  "email": "john@example.com",
  "website": "johnportfolio.com",
  "technicalSkills": ["Languages: JavaScript, Python", "Frameworks: React, Node.js"],
  "experience": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Company",
      "location": "San Francisco, CA",
      "dateRange": "Jan 2020 - Present",
      "bullets": ["Led **cross-functional team of 5 engineers** to deliver project **2 weeks ahead of schedule**", "Reduced API response time by 30%"]
    }
  ],
  "education": [
    {
      "institution": "University of Example",
      "location": "Example City",
      "graduationDate": "May 2019",
      "degree": "B.S. in Computer Science",
      "coursework": ["Data Structures", "Algorithms", "Machine Learning", "Web Development", "Database Systems"]
    }
  ]
}
```

2. Use the compile_resume tool to validate and generate HTML from your JSON
3. Show the compiled HTML to the user, prefacing it with a statement like "Here's how your resume will look:"

RESUME VALIDATION RULES:
To ensure the resume will compile correctly, your JSON MUST follow these rules:

1. Required fields - these MUST exist and be non-empty strings:
   - name
   - location
   - phone
   - email

2. Optional fields must use correct types:
   - website: string
   - technicalSkills: array of strings
   - education: array of objects
   - experience: array of objects
   - projects: array of objects
   - publications: array of objects

3. Each section must follow this structure:
   - education items require: institution, location, graduationDate, degree (all strings)
   - education items may include: coursework (array of strings) for relevant courses
   - experience items require: title, company, location, dateRange (all strings)
   - experience items may include: bullets (array of strings)
   - projects items require: name, dateRange (strings)
   - projects items may include: bullets (array of strings)
   - publications items require: title, citation (strings)
   - publications items may include: bullets (array of strings)

4. TEXT FORMATTING - Bold Text:
   - You can bold portions of text by surrounding them with double asterisks: **text to bold**
   - Bold formatting works in any string field, particularly useful in:
     - Experience bullet points to emphasize achievements and metrics
     - Project descriptions to highlight technologies or outcomes
     - Institution names, degrees, job titles, or company names to emphasize important elements
     - Coursework to highlight particularly relevant courses for a position
   - Example: "Increased system performance by **40%** through optimized database queries"
   - Example: "Implemented **React** and **Node.js** for a full-stack web application"
   - Use bold text strategically to highlight key information, particularly numbers, metrics, technologies, and specific achievements

Any deviation from these rules will cause validation to fail and the resume won't compile.
"""
    
    prompt = system_instructions
    
    # Add available tools information
    tools_info = """
AVAILABLE TOOLS:

1. 'get_user_context' to fetch background information about the user
2. 'compile_resume' to validate and compile the JSON resume into HTML

WHEN TO USE THE COMPILE_RESUME TOOL:
Always use the compile_resume tool after making any changes to the resume JSON. This tool:
1. Validates the JSON resume format
2. Generates a complete HTML resume that's ready for viewing or printing
3. Returns both validation status and the HTML output

Pass the entire updated JSON to this tool. Then show the user both the JSON and the HTML output.
"""
    prompt += tools_info
    
    # Include user context information directly
    user_context = build_user_context()
    if user_context:
        context_info = f"""
USER CONTEXT:
{user_context}
"""
        prompt += context_info
    
    # Add current resume content if provided
    if resume_json:
        try:
            # Try to load and format the content nicely if it's JSON
            parsed_content = json.loads(resume_json)
            formatted_content = json.dumps(parsed_content, indent=2)
            prompt += f"""
CURRENT RESUME CONTENT:
{formatted_content}
"""
        except json.JSONDecodeError:
            # If it's not valid JSON, just include it as is
            prompt += f"""
CURRENT RESUME CONTENT (note: this is not valid JSON):
{resume_json}
"""
    
    # Add user instructions if provided
    if instructions:
        prompt += f"""
USER INSTRUCTIONS:
{instructions}
"""
    
    return prompt

if __name__ == "__main__":
    mcp.run()

import os
import json
import io
import PyPDF2
from docx import Document
from mcp.server.fastmcp import FastMCP
from resume_compiler import validate_resume_json, compile_resume

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
        sample_context = """NO CONTEXT
"""
        with open(os.path.join(USER_CONTEXT_DIR, "context.txt"), "w") as f:
            f.write(sample_context.strip())

initialize_sample_context()

# --- Tool Implementations ---

@mcp.tool()
def validate_json(json_input):
    """Validate if a JSON string or dictionary is properly formatted and meets resume requirements"""
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
                "message": f"Input must be a JSON string or dictionary, got {type(json_input)}"
            }
        
        # Then check if it meets resume requirements
        is_valid, error_message = validate_resume_json(resume_data)
        
        if is_valid:
            return {
                "valid": True,
                "message": "JSON is properly formatted and meets resume requirements."
            }
        else:
            return {
                "valid": False,
                "message": f"JSON fails resume validation: {error_message}"
            }
            
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "message": f"Invalid JSON format: {str(e)}"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error validating JSON: {str(e)}"
        }

@mcp.tool()
def compile_resume_tool(json_input):
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
    # Use the imported compile_resume function from resume_compiler.py
    return compile_resume(json_input)

@mcp.tool()
def get_user_context():
    """Retrieve context information for the user from context.txt file"""
    context = build_user_context()
    
    if not context:
        return {"error": "No user context found. Please create a context.txt file in the user_context directory."}
    
    return {"context": context}

# --- Prompt Implementation ---

@mcp.prompt()
def resume_edit_prompt():
    """Create a prompt for editing a resume"""
    system_instructions = """
You are an AI assistant specifically designed to help users improve their résumés. 
Your task is to analyze the user's resume (provided as JSON) and respond to their questions or requests to modify the resume.

IMPORTANT ETHICAL GUIDELINES:
1. NEVER make up or fabricate information about the user
2. ONLY use information that is explicitly provided in the user context or resume JSON
3. If you need additional information about the user's background, experiences, or goals, ASK THE USER directly
4. Do not make assumptions about the user's education, work history, skills, or accomplishments
5. When providing suggestions, clearly indicate when you are recommending potential content versus using confirmed information

IMPORTANT: Instead of using tools to modify a resume, simply return the corrected resume in valid JSON format.

When suggesting modifications:
1. Analyze the user's instructions and the provided resume JSON
2. Provide the corrected/modified resume JSON directly in your response as a code block
3. Make sure the returned JSON is properly formatted and valid
4. Explain what changes you made and why they improve the resume

IMPORTANT: Your response should include the complete, valid JSON in a properly formatted code block like this:

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
      "bullets": ["Led cross-functional team of 5 engineers to deliver project 2 weeks ahead of schedule", "Reduced API response time by 30%"]
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
  ],
  "projects": [
    {
      "name": "**Database Optimization Tool** (Python, SQL)",
      "dateRange": "Jan 2021 - Mar 2021",
      "bullets": ["Developed an automated database optimization system", "Improved query performance by 40%"]
    }
  ],
  "publications": [
    {
      "title": "**Machine Learning Applications in Healthcare**",
      "citation": "Journal of Medical Informatics, 2022",
      "bullets": ["Explored applications of ML in diagnostic procedures", "Reviewed 50+ case studies"]
    }
  ]
}
```

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
   - UNLESS THE USER SPECIFIES OTHERWISE, follow these formatting guidelines:
     - Project names: Bold the project title but NOT the technologies in parentheses
       Example: "**Database Optimization Tool** (Python, SQL)"
     - Publication titles: Bold the entire title
       Example: "**Machine Learning Applications in Healthcare**"
     - Bullet points: Generally NO bolding in bullet points
     - Experience: Company names may be bolded, but bullet points typically are not
     - Education: Institution names may be bolded
   - For special emphasis (when specifically requested):
     - Experience bullet points may bold metrics/achievements: "Increased sales by **40%**"
     - Technical skills may bold specific critical technologies
   - Only use bold formatting when it serves a clear purpose for readability or emphasis

Any deviation from these rules will cause validation to fail and the resume won't compile.

ADDITIONAL FEATURES:
You can also compile the resume to HTML format using the compile_resume_tool tool. This will generate a formatted HTML preview of how the resume will look when printed. ONLY use this feature when the user explicitly requests to see the formatted resume, and ALWAYS ask before compiling to HTML.

If you're having trouble with the JSON formatting, you can use the validate_json tool to check if your JSON is properly formatted, ONLY USE IF THE USER EXPLICITLY REQUESTS IT
"""
    
    prompt = system_instructions
    
    # Add available tools information
    tools_info = """
AVAILABLE TOOLS:

1. 'get_user_context' to fetch background information about the user
2. 'validate_json' to check if your JSON is properly formatted, ONLY USE IF THE USER EXPLICITLY REQUESTS IT
3. 'compile_resume_tool' to generate an HTML preview of the resume, ONLY USE WHEN EXPLICITLY REQUESTED BY THE USER (ask first before using)
"""
    prompt += tools_info
    
    # Include user context information directly
    user_context = build_user_context()
    if user_context:
        context_info = f"""
USER CONTEXT (ONLY use information explicitly provided here, DO NOT make up additional details):
{user_context}
"""
        prompt += context_info
    
    return prompt

if __name__ == "__main__":
    mcp.run()

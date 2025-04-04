import json
import os

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
    if 'education' in resume_data and resume_data['education']:
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
    if 'experience' in resume_data and resume_data['experience']:
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
    if 'projects' in resume_data and resume_data['projects']:
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
    if 'publications' in resume_data and resume_data['publications']:
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
    <!-- Include html2pdf.js for PDF conversion -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        @page {
            size: letter;  /* 8.5in x 11in */
            margin: 0.5in;
        }
        
        body {
            font-family: "EB Garamond", "Garamond", "Times New Roman", serif;
            font-size: 10pt;
            line-height: 1.2;
            color: #000000;
            margin: 0;
            padding: 20px;
            width: 100%;
            box-sizing: border-box;
            background-color: #f0f0f0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .container {
            width: 100%;
            max-width: 1000px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }
        
        .resume-wrapper {
            width: 8.5in;
            height: 11in;
            background: white;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            padding: 0.5in;
            box-sizing: border-box;
            position: relative;
        }
        
        .resume {
            width: 7.5in;
            margin: 0 auto;
            padding: 0;
            background-color: white;
            overflow: auto;
            height: 100%;
        }
        
        .actions {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .download-btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            transition: background-color 0.3s;
        }
        
        .download-btn:hover {
            background-color: #45a049;
        }
        
        .pdf-notice {
            font-size: 14px;
            color: #555;
            text-align: center;
            margin-top: 5px;
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
            line-height: 1.2;
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
            page-break-inside: avoid;
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
            padding-left: 16px;
            list-style-type: disc;
            font-size: 10pt;
        }
        
        li {
            margin-bottom: 1px;
            line-height: 1.2;
            padding-left: 4px;
        }
        
        strong {
            font-weight: 600;
        }
        
        /* Technical skills */
        .skills-container {
            display: grid;
            grid-template-columns: max-content 1fr;
            grid-gap: 2px 20px;
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
            margin-bottom: 8px;
            page-break-inside: avoid;
        }
        
        .coursework {
            margin-top: 0;
            margin-bottom: 4px;
            font-size: 9pt;
        }
        
        /* Experience */
        .experience-item {
            margin-bottom: 4px;
            page-break-inside: avoid;
        }
        
        /* Projects */
        .project-item {
            margin-bottom: 6px;
            page-break-inside: avoid;
        }
        
        .project-subtitle {
            margin-top: 1px;
            margin-bottom: 1px;
        }
        
        /* Publications */
        .publication-item {
            margin-bottom: 4px;
            page-break-inside: avoid;
        }
        
        /* Print specific styles */
        @media print {
            body {
                padding: 0;
                background-color: white;
            }
            
            .container, .actions, .download-btn, .print-btn {
                display: none;
            }
            
            .resume-wrapper {
                box-shadow: none;
                padding: 0;
                margin: 0;
                width: 100%;
                height: auto;
            }
            
            html, body {
                width: 8.5in;
                height: 11in;
                margin: 0;
                padding: 0.5in;
            }
            
            .resume {
                width: 100%;
                margin: 0;
                padding: 0;
            }
            
            /* Avoid page breaks inside elements */
            p, h2, h3 {
                page-break-inside: avoid;
            }
            
            /* Ensure sections start on a new page only if needed */
            .section {
                page-break-before: auto;
            }
            
            /* Force page breaks where necessary */
            .page-break {
                page-break-before: always;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="actions">
            <button class="download-btn" onclick="downloadPDF()">Download PDF</button>
            <p class="pdf-notice">For best results, please download as PDF</p>
        </div>
        
        <div class="resume-wrapper" id="resume-content">
            <div class="resume">
"""
    
    # Add header section
    html += f"""
                <div class="header">
                    <h1>{resume_data.get('name', '')}</h1>
                    <p class="contact-info">
                        <span>{resume_data.get('location', '')}</span> | <span>{resume_data.get('phone', '')}</span> | <span>{resume_data.get('email', '')}</span>
                    </p>
                    {f'<p style="margin: 2px 0; font-size: 10pt; line-height: 1.2">{resume_data.get("website", "")}</p>' if resume_data.get('website') else ''}
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
                            <p style="margin-bottom: 0; margin-top: 0;">
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
                            <p style="margin-bottom: 0; margin-top: 0;">
                                <strong>{parse_bullet_text_html(job.get('company', ''))}</strong>, <span class="job-title">{parse_bullet_text_html(job.get('title', ''))}</span>, {parse_bullet_text_html(job.get('location', ''))}
                                <span class="date-range">{parse_bullet_text_html(job.get('dateRange', ''))}</span>
                            </p>
"""
            if 'bullets' in job and job['bullets']:
                html += """
                            <ul style="margin-top: 0;">
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
                            <p style="margin-bottom: 0; margin-top: 0;">
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
                            <ul style="margin-top: 0;">
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
                            <p style="margin-bottom: 0; margin-top: 0;">
                                <span class="publication-title">{parse_bullet_text_html(pub.get('title', ''))}</span>, {parse_bullet_text_html(pub.get('citation', ''))}
                            </p>
"""
            if 'bullets' in pub and pub['bullets']:
                html += """
                            <ul style="margin-top: 0;">
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
    
    # Close HTML tags and add JavaScript for PDF conversion
    html += """
            </div>
        </div>
    </div>
    
    <script>
        function downloadPDF() {
            // Get the resume content element
            const element = document.getElementById('resume-content');
            
            // Options for html2pdf
            const options = {
                margin: 0,
                filename: 'resume.pdf',
                image: { type: 'jpeg', quality: 1 },
                html2canvas: { scale: 2, useCORS: true },
                jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            
            // Generate and save the PDF
            html2pdf().set(options).from(element).save();
        }
    </script>
</body>
</html>
"""
    
    return html

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

if __name__ == "__main__":
    # Test resume data
    test_resume = {
        "name": "ZACHARY DECKER",
        "location": "New York, NY",
        "phone": "714-475-8849",
        "email": "zad25@cornell.edu",
        "website": "https://zacharydecker.com",
        "technicalSkills": [
            "Languages: Python, C++, JavaScript, Java, TypeScript, SQL, C, Scala, Scheme, HTML/CSS",
            "Frameworks & Tools: PyTorch, ROS, TensorFlow, OpenCV, Git, Verilog, AWS Amplify, LangChain",
            "OS: Linux, Windows, UNIX",
            "Other: Test-Driven Development, CI/CD, Agile, Firmware, Soldering, Circuit Design"
        ],
        "education": [
            {
                "institution": "Cornell Tech (Cornell University)",
                "location": "New York, NY",
                "graduationDate": "Expected May 2025",
                "degree": "Master of Engineering in Computer Science | GPA: 4.0",
                "coursework": ["Startup Studio", "Deep Learning", "NLP", "Machine Learning Productization"]
            },
            {
                "institution": "Rose-Hulman Institute of Technology",
                "location": "Terre Haute, IN",
                "graduationDate": "May 2024",
                "degree": "Bachelor of Science in Computer Science and Software Engineering | GPA: 3.71",
                "coursework": ["Deep Learning", "Computer Vision", "Linear Algebra", "Computer Architecture", "Philosophy of Mind", "Optimization Methods", "Operating Systems", "Bio-Inspired AI", "Algorithms", "Software Design"]
            }
        ],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "DEKA Research & Development",
                "location": "Manchester, NH",
                "dateRange": "Fall 2022 – Spring 2024",
                "bullets": [
                    "Designed & implemented real-time localization and mapping algorithms in C++ using ROS",
                    "Achieved 10x speedup in map refresh rates",
                    "Integrated terrain mapping with broader robotics pipeline in collaboration with path planning and controls teams",
                    "Authored technical documentation and presented findings at company-wide engineering reviews",
                    "Mentored junior engineers in advanced algorithmic approaches to robotics challenges"
                ]
            },
            {
                "title": "Research Intern",
                "company": "AON Devices",
                "location": "Irvine, CA",
                "dateRange": "Summer 2022",
                "bullets": [
                    "Researched transformer-based motion/speech recognition models for wearable devices",
                    "Built robust data pipelines and gained hands-on experience with circuit-level integration"
                ]
            }
        ],
        "projects": [
            {
                "name": "**Organize My Life** (React Native, AWS Amplify)",
                "dateRange": "Fall 2023 – Spring 2024",
                "bullets": [
                    "Cross-platform mobile file organization app",
                    "Built serverless backend, CI/CD pipelines, and deployed scalable storage",
                    "Implemented secure user authentication and file encryption",
                    "Achieved 99.9% uptime through robust error handling and monitoring"
                ]
            },
            {
                "name": "**Soccer Game Reconstruction** (YOLO, PyTorch, Matlab)",
                "dateRange": "Spring 2023",
                "bullets": [
                    "Reconstructed 3D player movements from 2D video",
                    "Applied homography to transform visual data into tactical insights",
                    "Achieved 95% accuracy in player detection and tracking",
                    "Developed custom visualization tools for coaches to analyze game patterns"
                ]
            },
            {
                "name": "**Workout Tracker** (React)",
                "dateRange": "Summer 2022",
                "bullets": [
                    "Led development of custom fitness app",
                    "Taught teammates modern frontend frameworks",
                    "Implemented offline functionality using local storage",
                    "Reduced load times by 60% through code optimization"
                ]
            }
        ],
        "publications": [
            {
                "title": "**Evolution of Developmental Strategies in NK Fitness Landscapes**",
                "citation": "Ashworth, J., Lee, Y., Shen, J., Kim, E., Decker, Z., & Yoder, J. (2022). ALIFE 2022: The Conference on Artificial Life, 59.",
                "bullets": [
                    "Simulated organism development using NK landscapes and genotype-encoded timing strategies",
                    "Showed sensitive periods emerge naturally in evolved developmental strategies"
                ]
            }
        ]
    }
    
    # Compile the resume
    result = compile_resume(test_resume)
    
    if result["valid"]:
        # Define the output directory and file path
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_file = os.path.join(output_dir, "zachary_decker_resume.html")
        
        # Write the HTML to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result["html"])
        
        print(f"Resume compiled successfully and saved to {output_file}")
    else:
        print(f"Failed to compile resume: {result['message']}") 
#!/usr/bin/env python3
"""
UC Berkeley Four Year Plan Generator - Flask Backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
import logging
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Gemini AI via environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini model initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
else:
    logger.warning("GEMINI_API_KEY not set. AI features will be disabled.")

app = Flask(__name__)
CORS(app)

# Global variables
courses_df = None
majors_data = {}

def load_course_data():
    """Load course data from CSV"""
    global courses_df
    try:
        csv_path = os.path.join('..', 'courses-report.2025-09-04 (7).csv')
        if os.path.exists(csv_path):
            courses_df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(courses_df)} courses from CSV")
        else:
            courses_df = create_sample_course_data()
            logger.info("Created sample course data")
    except Exception as e:
        logger.error(f"Error loading course data: {e}")
        courses_df = create_sample_course_data()

def create_sample_course_data():
    """Create sample course data"""
    sample_courses = [
        {
            'Subject': 'COMPSCI',
            'Course Number': '61A',
            'Department(s)': 'Computer Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'The Structure and Interpretation of Computer Programs'
        },
        {
            'Subject': 'COMPSCI',
            'Course Number': '61B',
            'Department(s)': 'Computer Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Data Structures'
        },
        {
            'Subject': 'MATH',
            'Course Number': '1A',
            'Department(s)': 'Mathematics',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring, Summer',
            'Course Description': 'Calculus'
        },
        {
            'Subject': 'MATH',
            'Course Number': '1B',
            'Department(s)': 'Mathematics',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring, Summer',
            'Course Description': 'Calculus'
        },
        {
            'Subject': 'PHYSICS',
            'Course Number': '7A',
            'Department(s)': 'Physics',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Physics for Scientists and Engineers'
        },
        {
            'Subject': 'ENGLISH',
            'Course Number': '1A',
            'Department(s)': 'English',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring, Summer',
            'Course Description': 'Reading and Composition'
        }
    ]
    return pd.DataFrame(sample_courses)

def load_majors_data():
    """Load majors and their requirements"""
    global majors_data
    
    # Create a comprehensive list of all UC Berkeley majors
    all_majors = [
        # College of Letters and Science - Arts and Humanities
        "Ancient Greek and Roman Studies", "Art History", "Art Practice", "Celtic Studies", 
        "Comparative Literature", "Dutch Studies", "East Asian Languages and Cultures",
        "English", "Film and Media", "French", "German", "Italian Studies",
        "Middle Eastern Languages and Cultures", "Music", "Near Eastern Civilizations",
        "Philosophy", "Rhetoric", "Scandinavian", "Slavic", "South and Southeast Asian Studies",
        "Spanish and Portuguese", "Theater, Dance, and Performance Studies",
        
        # College of Letters and Science - Biological Sciences
        "Integrative Biology", "Molecular and Cell Biology", "Neuroscience", "Public Health",
        "Robinson Life Science, Business, and Entrepreneurship Program",
        
        # College of Letters and Science - Interdisciplinary Studies
        "American Studies", "Interdisciplinary Studies", "Legal Studies", "Media Studies",
        
        # College of Letters and Science - Mathematical and Physical Sciences
        "Analytics", "Astrophysics", "Chemistry", "Earth and Planetary Science",
        "Mathematics", "Physics",
        
        # College of Letters and Science - Social Sciences
        "African American Studies", "Anthropology", "Asian American and Asian Diaspora Studies",
        "Chicano Studies", "Chicanx Latinx Studies", "Cognitive Science", "Economics",
        "Educational Sciences", "Ethnic Studies", "Gender and Women's Studies", "Geography",
        "Global Studies", "History", "Linguistics", "Native American Studies",
        "Political Economy", "Political Science", "Psychology", "Social Welfare", "Sociology",
        
        # College of Computing, Data Science, and Society
        "Computer Science", "Data Science", "Statistics",
        
        # College of Chemistry
        "Chemical Biology", "Chemical Engineering",
        
        # College of Engineering
        "Aerospace Engineering", "Bioengineering", "Civil Engineering",
        "Electrical and Computer Engineering", "Environmental Engineering Sciences",
        "Energy Engineering", "Engineering Mathematics and Statistics", "Engineering Physics",
        "Environmental Engineering Science", "Industrial Engineering and Operations Research",
        "Materials Science and Engineering", "Mechanical Engineering", "Nuclear Engineering",
        
        # College of Environmental Design
        "Architecture", "Landscape Architecture", "Sustainable Environmental Design", "Urban Studies",
        
        # Rausser College of Natural Resources
        "Conservation and Resource Studies", "Ecosystem Management and Forestry",
        "Environmental Economics and Policy", "Environmental Sciences", "Genetics and Plant Biology",
        "Microbial Biology", "Molecular Environmental Biology", "Nutrition & Metabolic Biology",
        "Society and Environment",
        
        # Haas School of Business
        "Business Administration"
    ]
    
    # Create a basic structure for all majors
    majors_data = {}
    for major in all_majors:
        # Determine college based on major name
        if major in ["Computer Science", "Data Science", "Statistics"]:
            college = "College of Computing, Data Science, and Society"
        elif major in ["Chemical Biology", "Chemical Engineering"]:
            college = "College of Chemistry"
        elif major in ["Aerospace Engineering", "Bioengineering", "Civil Engineering", 
                      "Electrical and Computer Engineering", "Environmental Engineering Sciences",
                      "Energy Engineering", "Engineering Mathematics and Statistics", "Engineering Physics",
                      "Environmental Engineering Science", "Industrial Engineering and Operations Research",
                      "Materials Science and Engineering", "Mechanical Engineering", "Nuclear Engineering"]:
            college = "College of Engineering"
        elif major in ["Architecture", "Landscape Architecture", "Sustainable Environmental Design", "Urban Studies"]:
            college = "College of Environmental Design"
        elif major in ["Conservation and Resource Studies", "Ecosystem Management and Forestry",
                      "Environmental Economics and Policy", "Environmental Sciences", "Genetics and Plant Biology",
                      "Microbial Biology", "Molecular Environmental Biology", "Nutrition & Metabolic Biology",
                      "Society and Environment"]:
            college = "Rausser College of Natural Resources"
        elif major == "Business Administration":
            college = "Haas School of Business"
        else:
            college = "College of Letters and Science"
        
        # Create basic requirements structure for each major
        majors_data[major] = {
            'college': college,
            'total_units': 120,
            'requirements': {
                'lower_division': [
                    {
                        'name': 'Core Requirements',
                        'courses': ['MATH 1A', 'ENGLISH 1A'],
                        'units': 8,
                        'description': 'Core mathematics and composition courses'
                    }
                ],
                'upper_division': [
                    {
                        'name': 'Major Requirements',
                        'courses': [f'{major.upper().replace(" ", "")[:8]} 100', f'{major.upper().replace(" ", "")[:8]} 101'],
                        'units': 8,
                        'description': f'Upper division {major} courses'
                    }
                ],
                'breadth': [
                    {
                        'name': 'General Education',
                        'courses': ['HISTORY 1A', 'PHYSICS 7A'],
                        'units': 8,
                        'description': 'Breadth requirements'
                    }
                ]
            }
        }
    
    # Add detailed requirements for some popular majors
    detailed_majors = {
        'Computer Science': {
            'college': 'College of Engineering',
            'total_units': 120,
            'requirements': {
                'lower_division': [
                    {
                        'name': 'Programming Fundamentals',
                        'courses': ['COMPSCI 61A', 'COMPSCI 61B'],
                        'units': 8,
                        'description': 'Core programming courses'
                    },
                    {
                        'name': 'Mathematics',
                        'courses': ['MATH 1A', 'MATH 1B'],
                        'units': 8,
                        'description': 'Calculus sequence'
                    }
                ],
                'upper_division': [
                    {
                        'name': 'Advanced Computer Science',
                        'courses': ['COMPSCI 170', 'COMPSCI 188'],
                        'units': 8,
                        'description': 'Upper division CS courses'
                    }
                ],
                'breadth': [
                    {
                        'name': 'Humanities',
                        'courses': ['ENGLISH 1A'],
                        'units': 4,
                        'description': 'Humanities breadth requirement'
                    }
                ]
            }
        },
        'Data Science': {
            'college': 'College of Computing, Data Science, and Society',
            'total_units': 120,
            'requirements': {
                'lower_division': [
                    {
                        'name': 'Programming Fundamentals',
                        'courses': ['COMPSCI 61A', 'COMPSCI 61B'],
                        'units': 8,
                        'description': 'Core programming courses'
                    },
                    {
                        'name': 'Mathematics',
                        'courses': ['MATH 1A', 'MATH 1B'],
                        'units': 8,
                        'description': 'Calculus sequence'
                    }
                ],
                'upper_division': [
                    {
                        'name': 'Data Science Core',
                        'courses': ['DATA 100', 'DATA 102'],
                        'units': 8,
                        'description': 'Core data science courses'
                    }
                ],
                'breadth': [
                    {
                        'name': 'Humanities',
                        'courses': ['ENGLISH 1A'],
                        'units': 4,
                        'description': 'Humanities breadth requirement'
                    }
                ]
            }
        }
    }
    
    # Override with detailed requirements for specific majors
    for major, details in detailed_majors.items():
        if major in majors_data:
            majors_data[major] = details

def get_course_info(subject, course_number):
    """Get course information from the dataset"""
    if courses_df is None:
        return None
    
    course = courses_df[
        (courses_df['Subject'] == subject) & 
        (courses_df['Course Number'] == course_number)
    ]
    
    if len(course) > 0:
        return course.iloc[0].to_dict()
    return None

def generate_four_year_plan_with_ai(major, graduation_year, preferences=None):
    """Generate a four-year plan using Google Gemini AI"""
    try:
        # Get available courses from our dataset
        available_courses = []
        if courses_df is not None:
            for _, course in courses_df.iterrows():
                available_courses.append({
                    'subject': course['Subject'],
                    'number': course['Course Number'],
                    'title': course['Course Description'],
                    'units': course['Credits - Units - Minimum Units'],
                    'terms': course['Terms Offered']
                })
        
        # Get completed courses and current year from preferences
        completed_courses = preferences.get('completed_courses', [])
        current_year = preferences.get('current_year', graduation_year - 4)
        
        # Create prompt for Gemini AI
        prompt = f"""
        You are an academic advisor at UC Berkeley. Generate a comprehensive 4-year academic plan for a student majoring in {major} who wants to graduate in {graduation_semester} {graduation_year}.

        Student Information:
        - Current Academic Year: {current_year}
        - Graduation Target: {graduation_semester} {graduation_year}
        - Completed Courses: {completed_courses if completed_courses else 'None'}
        - Available courses: {available_courses[:20]}  # Limit to first 20 for context

        Requirements:
        1. Create a semester-by-semester plan ending in {graduation_semester} {graduation_year}
        2. Include 12-16 units per semester (typical Berkeley load)
        3. Balance lower division and upper division courses appropriately
        4. Include prerequisites and course sequences
        5. Add breadth requirements and electives
        6. Consider course availability by term (Fall/Spring/Summer)
        7. DO NOT include courses already completed: {completed_courses}
        8. Start from current year {current_year} and plan forward to {graduation_semester} {graduation_year}
        9. Ensure the final semester is {graduation_semester} {graduation_year}

        Return the plan as a JSON structure with this format:
        {{
            "major": "{major}",
            "college": "College Name",
            "graduation_year": {graduation_year},
            "graduation_semester": "{graduation_semester}",
            "total_units": 120,
            "semesters": [
                {{
                    "year": 2024,
                    "term": "Fall",
                    "courses": [
                        {{
                            "subject": "MATH",
                            "number": "1A",
                            "title": "Calculus",
                            "units": 4,
                            "requirement_type": "lower_division",
                            "requirement_name": "Mathematics"
                        }}
                    ],
                    "units": 16
                }}
            ],
            "ai_recommendations": "Personalized advice and tips based on completed courses and current progress, targeting graduation in {graduation_semester} {graduation_year}"
        }}

        Focus on creating a realistic, well-balanced academic plan that follows UC Berkeley's requirements and best practices, taking into account the student's current progress and graduation timeline.
        """
        
        # Generate plan using Gemini AI
        response = model.generate_content(prompt)
        
        # Parse the AI response
        import json
        try:
            # Extract JSON from the response
            response_text = response.text
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            plan = json.loads(json_str)
            logger.info(f"Generated AI-powered plan for {major}")
            return plan
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing AI response: {e}")
            # Fallback to basic plan generation
            return generate_basic_four_year_plan(major, graduation_year, preferences)
            
    except Exception as e:
        logger.error(f"Error generating AI plan: {e}")
        # Fallback to basic plan generation
        return generate_basic_four_year_plan(major, graduation_year, preferences)

def generate_basic_four_year_plan(major, graduation_year, preferences=None):
    """Generate a basic four-year plan (fallback method)"""
    if major not in majors_data:
        return None
    
    major_info = majors_data[major]
    start_year = graduation_year - 4
    
    # Create 8 semesters (4 years)
    semesters = []
    for year in range(start_year, graduation_year):
        for term in ['Fall', 'Spring']:
            semesters.append({
                'year': year,
                'term': term,
                'courses': [],
                'units': 0
            })
    
    # Distribute requirements across semesters
    plan = {
        'major': major,
        'college': major_info['college'],
        'graduation_year': graduation_year,
        'total_units': major_info['total_units'],
        'semesters': semesters,
        'requirements': major_info['requirements'],
        'ai_recommendations': 'Basic plan generated - AI features coming soon!'
    }
    
    # Add courses to semesters (simplified distribution)
    semester_idx = 0
    for req_type, requirements in major_info['requirements'].items():
        for req in requirements:
            for course in req['courses']:
                if semester_idx < len(semesters):
                    course_info = get_course_info(course.split()[0], course.split()[1])
                    if course_info:
                        semesters[semester_idx]['courses'].append({
                            'subject': course_info['Subject'],
                            'number': course_info['Course Number'],
                            'title': course_info['Course Description'],
                            'units': course_info['Credits - Units - Minimum Units'],
                            'requirement_type': req_type,
                            'requirement_name': req['name']
                        })
                        semesters[semester_idx]['units'] += course_info['Credits - Units - Minimum Units']
                        semester_idx += 1
    
    return plan

def generate_four_year_plan(major, graduation_year, preferences=None):
    """Generate a four-year plan (wrapper function)"""
    return generate_four_year_plan_with_ai(major, graduation_year, preferences)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Berkeley Four Year Plan Generator is running"})

@app.route('/api/majors', methods=['GET'])
def get_majors():
    """Get list of available majors"""
    return jsonify(list(majors_data.keys()))

@app.route('/api/major/<major_name>', methods=['GET'])
def get_major_details(major_name):
    """Get details for a specific major"""
    if major_name not in majors_data:
        return jsonify({"error": "Major not found"}), 404
    
    return jsonify(majors_data[major_name])

@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    """Generate a four-year plan"""
    try:
        data = request.get_json()
        major = data.get('major')
        graduation_year = data.get('graduation_year')
        graduation_semester = data.get('graduation_semester', 'Spring')
        current_year = data.get('current_year', graduation_year - 4)
        completed_courses = data.get('completed_courses', [])
        preferences = data.get('preferences', {})
        
        if not major or not graduation_year:
            return jsonify({"error": "Major and graduation year are required"}), 400
        
        # Add completed courses to preferences
        preferences['completed_courses'] = completed_courses
        preferences['current_year'] = current_year
        
        plan = generate_four_year_plan(major, graduation_year, preferences)
        if not plan:
            return jsonify({"error": "Failed to generate plan"}), 500
        
        return jsonify(plan)
    
    except Exception as e:
        logger.error(f"Error generating plan: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/course-options', methods=['POST'])
def get_course_options():
    """Get course options for a specific requirement"""
    try:
        data = request.get_json()
        major = data.get('major')
        requirement_type = data.get('requirement_type')
        requirement_name = data.get('requirement_name')
        
        if not all([major, requirement_type, requirement_name]):
            return jsonify({"error": "Missing required parameters"}), 400
        
        if major not in majors_data:
            return jsonify({"error": "Major not found"}), 404
        
        major_info = majors_data[major]
        if requirement_type not in major_info['requirements']:
            return jsonify({"error": "Requirement type not found"}), 404
        
        # Find the specific requirement
        requirement = None
        for req in major_info['requirements'][requirement_type]:
            if req['name'] == requirement_name:
                requirement = req
                break
        
        if not requirement:
            return jsonify({"error": "Requirement not found"}), 404
        
        # Get alternative courses that could fulfill this requirement
        options = []
        for course in requirement['courses']:
            course_info = get_course_info(course.split()[0], course.split()[1])
            if course_info:
                options.append({
                    'subject': course_info['Subject'],
                    'number': course_info['Course Number'],
                    'title': course_info['Course Description'],
                    'units': course_info['Credits - Units - Minimum Units'],
                    'terms_offered': course_info['Terms Offered'],
                    'department': course_info['Department(s)']
                })
        
        return jsonify({
            'requirement_name': requirement_name,
            'requirement_type': requirement_type,
            'options': options
        })
    
    except Exception as e:
        logger.error(f"Error getting course options: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/search-courses', methods=['POST'])
def search_courses():
    """Search for courses by partial name or number"""
    try:
        data = request.get_json()
        query = data.get('query', '').upper().strip()
        
        if not query or len(query) < 2:
            return jsonify({"courses": []})
        
        # Search through course data
        matching_courses = []
        for course in courses_data:
            course_code = f"{course['Subject']} {course['Course Number']}"
            course_title = course['Course Description']
            
            # Check if query matches course code or title
            if (query in course_code or 
                query in course_title.upper() or
                course_code.startswith(query)):
                
                matching_courses.append({
                    'code': course_code,
                    'title': course_title,
                    'units': course['Credits - Units - Minimum Units'],
                    'terms': course['Terms Offered']
                })
                
                # Limit results to 10 for performance
                if len(matching_courses) >= 10:
                    break
        
        return jsonify({"courses": matching_courses})
    
    except Exception as e:
        logger.error(f"Error searching courses: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/ai-suggestions', methods=['POST'])
def get_ai_suggestions():
    """Get AI-powered course suggestions for a specific semester"""
    try:
        data = request.get_json()
        major = data.get('major')
        semester = data.get('semester')
        current_courses = data.get('current_courses', [])
        
        if not major or not semester:
            return jsonify({"error": "Major and semester are required"}), 400
        
        # Create prompt for AI suggestions
        prompt = f"""
        As a UC Berkeley academic advisor, suggest 3-5 additional courses for a {major} major in {semester['term']} {semester['year']}.
        
        Current courses: {current_courses}
        
        Consider:
        1. Prerequisites and course sequences
        2. Workload balance (aim for 12-16 units total)
        3. Course availability in {semester['term']}
        4. Breadth requirements
        5. Major requirements
        
        Return suggestions as JSON:
        {{
            "suggestions": [
                {{
                    "subject": "COURSE",
                    "number": "123",
                    "title": "Course Title",
                    "units": 4,
                    "reason": "Why this course is recommended"
                }}
            ],
            "advice": "General academic advice for this semester"
        }}
        """
        
        # Get AI suggestions
        response = model.generate_content(prompt)
        
        # Parse response
        import json
        try:
            response_text = response.text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            suggestions = json.loads(json_str)
            return jsonify(suggestions)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing AI suggestions: {e}")
            return jsonify({
                "suggestions": [],
                "advice": "AI suggestions temporarily unavailable. Please try again later."
            })
    
    except Exception as e:
        logger.error(f"Error getting AI suggestions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Load data on startup
    load_course_data()
    load_majors_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

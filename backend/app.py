#!/usr/bin/env python3
"""
UC Berkeley Four Year Plan Generator - Flask Backend
Uses LangChain RAG with Google Gemini for intelligent schedule generation
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime, timezone
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Secret key for sessions
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-me')

# Configure CORS for production domains
import re

def cors_origin_callback(origin):
    """Check if origin is allowed - supports Vercel preview URLs"""
    if not origin:
        return False

    allowed_patterns = [
        r'^https://berkeleyfouryearplan\.com$',
        r'^https://www\.berkeleyfouryearplan\.com$',
        r'^http://localhost:\d+$',
        r'^https://.*\.vercel\.app$',  # All Vercel preview/prod URLs
    ]

    for pattern in allowed_patterns:
        if re.match(pattern, origin):
            return True

    # Check additional origins from env
    extra_origins = os.getenv('ALLOWED_ORIGINS', '')
    if extra_origins:
        for o in extra_origins.split(','):
            if origin == o.strip():
                return True

    return False

# Enable CORS with credentials for frontend
CORS(app,
     origins=cors_origin_callback,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Configure session cookies for production
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None' if os.getenv('FLASK_ENV') == 'production' else 'Lax'

# Global variables
courses_df = None
majors_data = {}
rag_pipeline = None
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'berkeley_planner')
mongo_client: MongoClient | None = None
db = None

def init_db():
    global mongo_client, db
    try:
        mongo_client = MongoClient(MONGODB_URI)
        db = mongo_client[MONGO_DB_NAME]
        # indexes
        db.users.create_index([('email', ASCENDING)], unique=True)
        db.schedules.create_index([('user_id', ASCENDING), ('updated_at', ASCENDING)])
        logger.info("MongoDB initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise

def load_course_data():
    """Load course data from CSV"""
    global courses_df
    try:
        # Check multiple locations for CSV (production vs development)
        csv_paths = [
            'courses-data.csv',  # Production (Docker)
            os.path.join('..', 'courses-report.2025-09-04 (7).csv'),  # Development
            'courses-report.2025-09-04 (7).csv',  # Alternative location
        ]

        csv_path = None
        for path in csv_paths:
            if os.path.exists(path):
                csv_path = path
                break

        if csv_path:
            courses_df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(courses_df)} courses from {csv_path}")
        else:
            courses_df = create_sample_course_data()
            logger.info("Created sample course data (no CSV found)")
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
            'Subject': 'COMPSCI',
            'Course Number': '61C',
            'Department(s)': 'Computer Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Great Ideas in Computer Architecture (Machine Structures)'
        },
        {
            'Subject': 'COMPSCI',
            'Course Number': '70',
            'Department(s)': 'Computer Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Discrete Mathematics and Probability Theory'
        },
        {
            'Subject': 'COMPSCI',
            'Course Number': '170',
            'Department(s)': 'Computer Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Efficient Algorithms and Intractable Problems'
        },
        {
            'Subject': 'COMPSCI',
            'Course Number': '188',
            'Department(s)': 'Computer Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Introduction to Artificial Intelligence'
        },
        {
            'Subject': 'COMPSCI',
            'Course Number': '189',
            'Department(s)': 'Computer Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Introduction to Machine Learning'
        },
        {
            'Subject': 'DATA',
            'Course Number': '8',
            'Department(s)': 'Data Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Foundations of Data Science'
        },
        {
            'Subject': 'DATA',
            'Course Number': '100',
            'Department(s)': 'Data Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Principles and Techniques of Data Science'
        },
        {
            'Subject': 'DATA',
            'Course Number': '102',
            'Department(s)': 'Data Science',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Data, Inference, and Decisions'
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
            'Subject': 'MATH',
            'Course Number': '53',
            'Department(s)': 'Mathematics',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Multivariable Calculus'
        },
        {
            'Subject': 'MATH',
            'Course Number': '54',
            'Department(s)': 'Mathematics',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Linear Algebra and Differential Equations'
        },
        {
            'Subject': 'EECS',
            'Course Number': '16A',
            'Department(s)': 'Electrical Engineering and Computer Sciences',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Designing Information Devices and Systems I'
        },
        {
            'Subject': 'EECS',
            'Course Number': '16B',
            'Department(s)': 'Electrical Engineering and Computer Sciences',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Designing Information Devices and Systems II'
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
            'Subject': 'PHYSICS',
            'Course Number': '7B',
            'Department(s)': 'Physics',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Physics for Scientists and Engineers'
        },
        {
            'Subject': 'ENGLISH',
            'Course Number': 'R1A',
            'Department(s)': 'English',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring, Summer',
            'Course Description': 'Reading and Composition'
        },
        {
            'Subject': 'ENGLISH',
            'Course Number': 'R1B',
            'Department(s)': 'English',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring, Summer',
            'Course Description': 'Reading and Composition'
        },
        {
            'Subject': 'STAT',
            'Course Number': '20',
            'Department(s)': 'Statistics',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Introduction to Probability and Statistics'
        },
        {
            'Subject': 'STAT',
            'Course Number': '134',
            'Department(s)': 'Statistics',
            'Credits - Units - Minimum Units': 4,
            'Terms Offered': 'Fall, Spring',
            'Course Description': 'Concepts of Probability'
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
                        'courses': ['MATH 1A', 'ENGLISH R1A'],
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

    # Add detailed requirements for popular majors
    detailed_majors = {
        'Computer Science': {
            'college': 'College of Computing, Data Science, and Society',
            'total_units': 120,
            'requirements': {
                'lower_division': [
                    {
                        'name': 'Programming Fundamentals',
                        'courses': ['COMPSCI 61A', 'COMPSCI 61B', 'COMPSCI 61C'],
                        'units': 12,
                        'description': 'Core programming and systems courses'
                    },
                    {
                        'name': 'Discrete Mathematics',
                        'courses': ['COMPSCI 70'],
                        'units': 4,
                        'description': 'Discrete mathematics and probability'
                    },
                    {
                        'name': 'Mathematics',
                        'courses': ['MATH 1A', 'MATH 1B', 'MATH 53', 'MATH 54'],
                        'units': 16,
                        'description': 'Calculus and linear algebra sequence'
                    },
                    {
                        'name': 'Circuits',
                        'courses': ['EECS 16A', 'EECS 16B'],
                        'units': 8,
                        'description': 'Electrical engineering fundamentals'
                    }
                ],
                'upper_division': [
                    {
                        'name': 'Core Upper Division',
                        'courses': ['COMPSCI 170', 'COMPSCI 188', 'COMPSCI 189'],
                        'units': 12,
                        'description': 'Algorithms, AI, and ML courses'
                    }
                ],
                'breadth': [
                    {
                        'name': 'Reading and Composition',
                        'courses': ['ENGLISH R1A', 'ENGLISH R1B'],
                        'units': 8,
                        'description': 'Writing requirements'
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
                        'name': 'Data Science Foundations',
                        'courses': ['DATA 8', 'COMPSCI 61A', 'COMPSCI 61B'],
                        'units': 12,
                        'description': 'Foundational programming and data science'
                    },
                    {
                        'name': 'Mathematics',
                        'courses': ['MATH 1A', 'MATH 1B', 'MATH 53', 'MATH 54'],
                        'units': 16,
                        'description': 'Calculus and linear algebra'
                    },
                    {
                        'name': 'Statistics',
                        'courses': ['STAT 20', 'STAT 134'],
                        'units': 8,
                        'description': 'Probability and statistics'
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
                        'name': 'Reading and Composition',
                        'courses': ['ENGLISH R1A', 'ENGLISH R1B'],
                        'units': 8,
                        'description': 'Writing requirements'
                    }
                ]
            }
        },
        'Electrical and Computer Engineering': {
            'college': 'College of Engineering',
            'total_units': 120,
            'requirements': {
                'lower_division': [
                    {
                        'name': 'Programming',
                        'courses': ['COMPSCI 61A', 'COMPSCI 61B', 'COMPSCI 61C'],
                        'units': 12,
                        'description': 'Programming fundamentals'
                    },
                    {
                        'name': 'Circuits and Signals',
                        'courses': ['EECS 16A', 'EECS 16B'],
                        'units': 8,
                        'description': 'Circuits and signal processing'
                    },
                    {
                        'name': 'Mathematics',
                        'courses': ['MATH 1A', 'MATH 1B', 'MATH 53', 'MATH 54'],
                        'units': 16,
                        'description': 'Calculus and linear algebra'
                    },
                    {
                        'name': 'Physics',
                        'courses': ['PHYSICS 7A', 'PHYSICS 7B'],
                        'units': 8,
                        'description': 'Physics for engineers'
                    }
                ],
                'upper_division': [
                    {
                        'name': 'Core Technical',
                        'courses': ['COMPSCI 170', 'COMPSCI 188'],
                        'units': 8,
                        'description': 'Upper division technical courses'
                    }
                ],
                'breadth': [
                    {
                        'name': 'Reading and Composition',
                        'courses': ['ENGLISH R1A', 'ENGLISH R1B'],
                        'units': 8,
                        'description': 'Writing requirements'
                    }
                ]
            }
        }
    }

    # Override with detailed requirements for specific majors
    for major, details in detailed_majors.items():
        if major in majors_data:
            majors_data[major] = details

def init_rag_pipeline():
    """Initialize the RAG pipeline for schedule generation"""
    global rag_pipeline

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set. RAG features will be disabled.")
        return

    try:
        from rag_pipeline import initialize_rag_pipeline
        rag_pipeline = initialize_rag_pipeline(GEMINI_API_KEY, courses_df, majors_data)
        logger.info("RAG Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        logger.warning("Falling back to basic schedule generation")

def get_course_info(subject, course_number):
    """Get course information from the dataset"""
    if courses_df is None:
        return None

    course = courses_df[
        (courses_df['Subject'] == subject) &
        (courses_df['Course Number'] == str(course_number))
    ]

    if len(course) > 0:
        return course.iloc[0].to_dict()
    return None

def generate_four_year_plan(major, graduation_year, preferences=None, graduation_semester='Spring'):
    """Generate a four-year plan using RAG pipeline"""
    global rag_pipeline

    if rag_pipeline is not None:
        try:
            # Extract preferences
            preferences = preferences or {}
            completed_courses = preferences.get('completed_courses', [])
            current_year = preferences.get('current_year', graduation_year - 4)

            # Use RAG pipeline for generation
            plan = rag_pipeline.generate_schedule(
                major=major,
                graduation_year=graduation_year,
                graduation_semester=graduation_semester,
                current_year=current_year,
                completed_courses=completed_courses,
                preferences=preferences
            )
            return plan
        except Exception as e:
            logger.error(f"RAG pipeline error: {e}")
            # Fall back to basic generation

    # Fallback: basic plan generation
    return generate_basic_four_year_plan(major, graduation_year, preferences, graduation_semester)

def generate_basic_four_year_plan(major, graduation_year, preferences=None, graduation_semester='Spring'):
    """Generate a basic four-year plan (fallback method)"""
    if major not in majors_data:
        return None

    major_info = majors_data[major]
    start_year = graduation_year - 4

    # Get completed courses from preferences
    preferences = preferences or {}
    completed_courses = set(preferences.get('completed_courses', []))
    current_year = preferences.get('current_year', start_year)

    # Create semesters from current year to graduation
    semesters = []
    for year in range(current_year, graduation_year + 1):
        for term in ['Fall', 'Spring']:
            # Stop at graduation semester
            if year == graduation_year:
                if graduation_semester == 'Fall' and term == 'Spring':
                    break
                if graduation_semester == 'Spring' and term == 'Fall':
                    semesters.append({
                        'year': year,
                        'term': term,
                        'courses': [],
                        'units': 0
                    })
                    break
            semesters.append({
                'year': year,
                'term': term,
                'courses': [],
                'units': 0
            })

    # Build the plan
    plan = {
        'major': major,
        'college': major_info['college'],
        'graduation_year': graduation_year,
        'graduation_semester': graduation_semester,
        'total_units': major_info['total_units'],
        'semesters': semesters,
        'requirements': major_info['requirements'],
        'ai_recommendations': 'Basic plan generated. For AI-powered recommendations, ensure GEMINI_API_KEY is configured.'
    }

    # Add courses to semesters (simplified distribution)
    semester_idx = 0
    for req_type, requirements in major_info['requirements'].items():
        for req in requirements:
            for course in req['courses']:
                if course in completed_courses:
                    continue  # Skip completed courses

                if semester_idx < len(semesters):
                    parts = course.split()
                    if len(parts) >= 2:
                        course_info = get_course_info(parts[0], parts[1])
                        if course_info:
                            semesters[semester_idx]['courses'].append({
                                'subject': course_info['Subject'],
                                'number': str(course_info['Course Number']),
                                'title': course_info['Course Description'],
                                'units': int(course_info.get('Credits - Units - Minimum Units', 4)),
                                'requirement_type': req_type,
                                'requirement_name': req['name']
                            })
                            semesters[semester_idx]['units'] += int(course_info.get('Credits - Units - Minimum Units', 4))

                            # Move to next semester if current has 16+ units
                            if semesters[semester_idx]['units'] >= 16:
                                semester_idx += 1

    return plan

# ---------------------- HEALTH CHECK ----------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Berkeley Four Year Plan Generator is running",
        "rag_enabled": rag_pipeline is not None,
        "courses_loaded": courses_df is not None and len(courses_df) > 0,
        "majors_loaded": len(majors_data) > 0,
        "db_connected": db is not None
    })

# ---------------------- AUTH ENDPOINTS ----------------------
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup"""
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    password_hash = generate_password_hash(password)
    now = datetime.now(timezone.utc).isoformat()

    try:
        result = db.users.insert_one({
            'email': email,
            'password_hash': password_hash,
            'created_at': now
        })
    except DuplicateKeyError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"error": "Failed to create account"}), 500

    user_id = str(result.inserted_id)
    session['user_id'] = user_id
    session['email'] = email

    logger.info(f"User signed up: {email}")
    return jsonify({"id": user_id, "email": email})

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = db.users.find_one({'email': email})
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({"error": "Invalid credentials"}), 401

        session['user_id'] = str(user['_id'])
        session['email'] = email

        logger.info(f"User logged in: {email}")
        return jsonify({"id": session['user_id'], "email": email})
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    email = session.get('email', 'unknown')
    session.clear()
    logger.info(f"User logged out: {email}")
    return jsonify({"ok": True})

@app.route('/api/auth/me', methods=['GET'])
def me():
    """Get current user"""
    if 'user_id' not in session:
        return jsonify({"user": None})
    return jsonify({"user": {"id": session['user_id'], "email": session.get('email')}})

# ---------------------- SCHEDULES ENDPOINTS ----------------------
@app.route('/api/schedules', methods=['GET', 'POST'])
def schedules():
    """Get all schedules or create a new one"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']

    if request.method == 'GET':
        try:
            rows = list(db.schedules.find({'user_id': user_id}).sort('updated_at', -1))
            return jsonify([
                {
                    "id": str(r['_id']),
                    "name": r['name'],
                    "data": r['data'],
                    "created_at": r['created_at'],
                    "updated_at": r['updated_at']
                }
                for r in rows
            ])
        except Exception as e:
            logger.error(f"Error fetching schedules: {e}")
            return jsonify({"error": "Failed to fetch schedules"}), 500
    else:
        try:
            body = request.get_json() or {}
            name = (body.get('name') or 'My Plan').strip()
            data = body.get('data')

            if not data:
                return jsonify({"error": "Missing schedule data"}), 400

            now = datetime.now(timezone.utc).isoformat()
            result = db.schedules.insert_one({
                'user_id': user_id,
                'name': name,
                'data': data,
                'created_at': now,
                'updated_at': now
            })

            logger.info(f"Schedule created for user {session.get('email')}: {name}")
            return jsonify({"id": str(result.inserted_id), "name": name}), 201
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return jsonify({"error": "Failed to create schedule"}), 500

@app.route('/api/schedules/<schedule_id>', methods=['GET', 'PUT', 'DELETE'])
def schedule_detail(schedule_id: str):
    """Get, update, or delete a specific schedule"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']

    try:
        oid = ObjectId(schedule_id)
    except Exception:
        return jsonify({"error": "Invalid id"}), 400

    if request.method == 'GET':
        try:
            row = db.schedules.find_one({'_id': oid, 'user_id': user_id})
            if not row:
                return jsonify({"error": "Not found"}), 404
            return jsonify({
                "id": str(row['_id']),
                "name": row['name'],
                "data": row['data'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at']
            })
        except Exception as e:
            logger.error(f"Error fetching schedule: {e}")
            return jsonify({"error": "Failed to fetch schedule"}), 500

    elif request.method == 'PUT':
        try:
            body = request.get_json() or {}
            name = (body.get('name') or '').strip()
            data = body.get('data')
            now = datetime.now(timezone.utc).isoformat()

            update = {'updated_at': now}
            if name:
                update['name'] = name
            if data is not None:
                update['data'] = data

            result = db.schedules.update_one(
                {'_id': oid, 'user_id': user_id},
                {'$set': update}
            )

            if result.matched_count == 0:
                return jsonify({"error": "Not found"}), 404

            logger.info(f"Schedule updated: {schedule_id}")
            return jsonify({"ok": True})
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            return jsonify({"error": "Failed to update schedule"}), 500
    else:
        try:
            result = db.schedules.delete_one({'_id': oid, 'user_id': user_id})
            if result.deleted_count == 0:
                return jsonify({"error": "Not found"}), 404
            logger.info(f"Schedule deleted: {schedule_id}")
            return jsonify({"ok": True})
        except Exception as e:
            logger.error(f"Error deleting schedule: {e}")
            return jsonify({"error": "Failed to delete schedule"}), 500

# ---------------------- MAJORS ENDPOINTS ----------------------
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

# ---------------------- PLAN GENERATION ----------------------
@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    """Generate a four-year plan"""
    try:
        data = request.get_json()
        major = data.get('major')
        graduation_year = data.get('graduation_year')
        graduation_semester = data.get('graduation_semester', 'Spring')
        current_year = data.get('current_year', graduation_year - 4 if graduation_year else None)
        completed_courses = data.get('completed_courses', [])
        preferences = data.get('preferences', {})

        if not major or not graduation_year:
            return jsonify({"error": "Major and graduation year are required"}), 400

        # Add completed courses and current year to preferences
        preferences['completed_courses'] = completed_courses
        preferences['current_year'] = current_year

        logger.info(f"Generating plan for {major}, graduating {graduation_semester} {graduation_year}")

        plan = generate_four_year_plan(major, graduation_year, preferences, graduation_semester)
        if not plan:
            return jsonify({"error": "Failed to generate plan. Major may not be supported."}), 500

        return jsonify(plan)

    except Exception as e:
        logger.error(f"Error generating plan: {e}", exc_info=True)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# ---------------------- COURSE OPTIONS ----------------------
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
            parts = course.split()
            if len(parts) >= 2:
                course_info = get_course_info(parts[0], parts[1])
                if course_info:
                    options.append({
                        'subject': course_info['Subject'],
                        'number': str(course_info['Course Number']),
                        'title': course_info['Course Description'],
                        'units': int(course_info.get('Credits - Units - Minimum Units', 4)),
                        'terms_offered': course_info.get('Terms Offered', 'Fall, Spring'),
                        'department': course_info.get('Department(s)', '')
                    })

        return jsonify({
            'requirement_name': requirement_name,
            'requirement_type': requirement_type,
            'options': options
        })

    except Exception as e:
        logger.error(f"Error getting course options: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# ---------------------- COURSE SEARCH ----------------------
@app.route('/api/search-courses', methods=['POST'])
def search_courses():
    """Search for courses by partial name or number"""
    try:
        data = request.get_json()
        query = data.get('query', '').upper().strip()

        if not query or len(query) < 2:
            return jsonify({"courses": []})

        # Try RAG-based search first
        if rag_pipeline is not None:
            try:
                results = rag_pipeline.search_courses(query, limit=10)
                if results:
                    return jsonify({"courses": results})
            except Exception as e:
                logger.warning(f"RAG search failed, falling back to basic: {e}")

        # Fallback to basic search
        if courses_df is None:
            return jsonify({"courses": []})

        matching_courses = []
        for _, course in courses_df.iterrows():
            course_code = f"{course['Subject']} {course['Course Number']}"
            course_title = str(course['Course Description'])

            if (query in course_code or
                query in course_title.upper() or
                course_code.startswith(query)):

                matching_courses.append({
                    'code': course_code,
                    'title': course_title,
                    'units': int(course.get('Credits - Units - Minimum Units', 4)),
                    'terms': course.get('Terms Offered', 'Fall, Spring')
                })

                if len(matching_courses) >= 10:
                    break

        return jsonify({"courses": matching_courses})

    except Exception as e:
        logger.error(f"Error searching courses: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# ---------------------- AI SUGGESTIONS ----------------------
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

        # Use RAG pipeline for suggestions
        if rag_pipeline is not None:
            try:
                suggestions = rag_pipeline.get_ai_suggestions(major, semester, current_courses)
                return jsonify(suggestions)
            except Exception as e:
                logger.error(f"RAG suggestions failed: {e}")

        # Fallback response
        return jsonify({
            "suggestions": [],
            "advice": "AI suggestions are currently unavailable. Please ensure GEMINI_API_KEY is configured."
        })

    except Exception as e:
        logger.error(f"Error getting AI suggestions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    # Initialize components on startup
    init_db()
    load_course_data()
    load_majors_data()
    init_rag_pipeline()

    logger.info("Starting Berkeley Four Year Plan Generator API")
    app.run(debug=True, host='0.0.0.0', port=5000)

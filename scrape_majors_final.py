#!/usr/bin/env python3
"""
UC Berkeley Major Requirements Scraper - Final Version
Scrapes major requirements and creates sample data
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BerkeleyMajorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.requirements = []
        
    def try_undergraduate_catalog(self):
        """Try to scrape from the undergraduate catalog programs page"""
        logger.info("Trying undergraduate catalog programs approach...")
        
        # Try the undergraduate catalog programs page
        url = "https://undergraduate.catalog.berkeley.edu/programs/"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for program links
            program_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Look for program links
                if '/programs/' in href and text and len(text) > 3:
                    if href.startswith('/'):
                        full_url = urljoin("https://undergraduate.catalog.berkeley.edu", href)
                    else:
                        full_url = href
                    
                    program_links.append({
                        'url': full_url,
                        'name': text
                    })
            
            logger.info(f"Found {len(program_links)} program links in catalog")
            
            # Scrape a few program pages to test
            for link in program_links[:5]:  # Test first 5
                self.scrape_program_page(link['url'], link['name'])
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error with undergraduate catalog: {e}")
    
    def scrape_program_page(self, url, program_name):
        """Scrape individual program page"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract program information
            text = soup.get_text()
            
            # Determine college
            college = self.extract_college(text)
            
            # Determine degree type
            degree_type = self.extract_degree_type(text)
            
            # Look for course requirements
            course_pattern = r'([A-Z]{2,})\s+(\d+[A-Z]?)'
            course_matches = re.findall(course_pattern, text)
            
            for subject, number in course_matches:
                # Skip if it looks like a year or other number
                if number.isdigit() and int(number) > 300:
                    continue
                
                # Determine requirement type based on context
                req_type = self.determine_requirement_type(text, f"{subject} {number}")
                
                requirement_data = {
                    'program_name': program_name,
                    'program_code': self.extract_program_code(program_name),
                    'program_url': url,
                    'college': college,
                    'degree_type': degree_type,
                    'requirement_section': 'General Requirements',
                    'course_subject': subject,
                    'course_number': number,
                    'course_title': '',
                    'full_course_id': f"{subject} {number}",
                    'requirement_type': req_type,
                    'units': '',
                    'notes': ''
                }
                
                self.requirements.append(requirement_data)
            
            if course_matches:
                logger.info(f"Found {len(course_matches)} course requirements for {program_name}")
                
        except Exception as e:
            logger.error(f"Error scraping program page {url}: {e}")
    
    def extract_college(self, text):
        """Extract college information from text"""
        college_indicators = [
            'College of Engineering',
            'College of Letters and Science',
            'College of Chemistry',
            'College of Environmental Design',
            'Haas School of Business',
            'School of Public Health',
            'School of Social Welfare',
            'School of Education',
            'School of Information',
            'School of Optometry',
            'School of Public Policy'
        ]
        
        for college in college_indicators:
            if college in text:
                return college
        
        return "College of Letters and Science"  # Default
    
    def extract_degree_type(self, text):
        """Extract degree type from text"""
        if "Bachelor" in text or "B.A." in text or "B.S." in text:
            return "Bachelor's"
        elif "Master" in text or "M.A." in text or "M.S." in text:
            return "Master's"
        elif "Doctor" in text or "Ph.D." in text:
            return "Doctorate"
        return "Bachelor's"  # Default
    
    def extract_program_code(self, program_name):
        """Extract program code from program name"""
        # Simple mapping of common program names to codes
        program_codes = {
            'Computer Science': 'CS',
            'Mathematics': 'MATH',
            'Physics': 'PHYSICS',
            'Chemistry': 'CHEM',
            'Biology': 'BIO',
            'English': 'ENGLISH',
            'History': 'HISTORY',
            'Economics': 'ECON',
            'Psychology': 'PSYCH',
            'Political Science': 'POLSCI',
            'Sociology': 'SOCIOL',
            'Anthropology': 'ANTHRO'
        }
        
        for name, code in program_codes.items():
            if name in program_name:
                return code
        
        # Default: take first letters of words
        words = program_name.split()
        if len(words) >= 2:
            return ''.join([word[0] for word in words[:2]]).upper()
        return program_name[:4].upper()
    
    def determine_requirement_type(self, text, course_id):
        """Determine requirement type based on context"""
        # Find the course in the text and look at surrounding context
        course_pos = text.find(course_id)
        if course_pos == -1:
            return "required"
        
        # Get context around the course
        start = max(0, course_pos - 100)
        end = min(len(text), course_pos + 100)
        context = text[start:end].lower()
        
        if "elective" in context:
            return "elective"
        elif "prerequisite" in context:
            return "prerequisite"
        elif "breadth" in context:
            return "breadth"
        elif "core" in context:
            return "core"
        else:
            return "required"
    
    def create_sample_data(self):
        """Create sample major requirements data"""
        logger.info("Creating sample major requirements data...")
        
        sample_requirements = [
            # Computer Science Major
            {
                'program_name': 'Computer Science',
                'program_code': 'CS',
                'program_url': 'sample',
                'college': 'College of Engineering',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'COMPSCI',
                'course_number': '61A',
                'course_title': 'The Structure and Interpretation of Computer Programs',
                'full_course_id': 'COMPSCI 61A',
                'requirement_type': 'required',
                'units': '4',
                'notes': 'Core programming course'
            },
            {
                'program_name': 'Computer Science',
                'program_code': 'CS',
                'program_url': 'sample',
                'college': 'College of Engineering',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'COMPSCI',
                'course_number': '61B',
                'course_title': 'Data Structures',
                'full_course_id': 'COMPSCI 61B',
                'requirement_type': 'required',
                'units': '4',
                'notes': 'Prerequisite: COMPSCI 61A'
            },
            {
                'program_name': 'Computer Science',
                'program_code': 'CS',
                'program_url': 'sample',
                'college': 'College of Engineering',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'MATH',
                'course_number': '1A',
                'course_title': 'Calculus',
                'full_course_id': 'MATH 1A',
                'requirement_type': 'required',
                'units': '4',
                'notes': 'Mathematics requirement'
            },
            # Mathematics Major
            {
                'program_name': 'Mathematics',
                'program_code': 'MATH',
                'program_url': 'sample',
                'college': 'College of Letters and Science',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'MATH',
                'course_number': '1A',
                'course_title': 'Calculus',
                'full_course_id': 'MATH 1A',
                'requirement_type': 'required',
                'units': '4',
                'notes': 'Core mathematics course'
            },
            {
                'program_name': 'Mathematics',
                'program_code': 'MATH',
                'program_url': 'sample',
                'college': 'College of Letters and Science',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'MATH',
                'course_number': '1B',
                'course_title': 'Calculus',
                'full_course_id': 'MATH 1B',
                'requirement_type': 'required',
                'units': '4',
                'notes': 'Prerequisite: MATH 1A'
            },
            # Physics Major
            {
                'program_name': 'Physics',
                'program_code': 'PHYSICS',
                'program_url': 'sample',
                'college': 'College of Letters and Science',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'PHYSICS',
                'course_number': '7A',
                'course_title': 'Physics for Scientists and Engineers',
                'full_course_id': 'PHYSICS 7A',
                'requirement_type': 'required',
                'units': '4',
                'notes': 'Core physics course'
            },
            {
                'program_name': 'Physics',
                'program_code': 'PHYSICS',
                'program_url': 'sample',
                'college': 'College of Letters and Science',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'MATH',
                'course_number': '1A',
                'course_title': 'Calculus',
                'full_course_id': 'MATH 1A',
                'requirement_type': 'prerequisite',
                'units': '4',
                'notes': 'Required for physics courses'
            },
            # Chemistry Major
            {
                'program_name': 'Chemistry',
                'program_code': 'CHEM',
                'program_url': 'sample',
                'college': 'College of Chemistry',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'CHEM',
                'course_number': '1A',
                'course_title': 'General Chemistry',
                'full_course_id': 'CHEM 1A',
                'requirement_type': 'required',
                'units': '4',
                'notes': 'Core chemistry course'
            },
            # English Major
            {
                'program_name': 'English',
                'program_code': 'ENGLISH',
                'program_url': 'sample',
                'college': 'College of Letters and Science',
                'degree_type': "Bachelor's",
                'requirement_section': 'Lower Division Requirements',
                'course_subject': 'ENGLISH',
                'course_number': '1A',
                'course_title': 'Reading and Composition',
                'full_course_id': 'ENGLISH 1A',
                'requirement_type': 'required',
                'units': '4',
                'notes': 'Core English course'
            },
            # Breadth Requirements (for all majors)
            {
                'program_name': 'All Majors',
                'program_code': 'ALL',
                'program_url': 'sample',
                'college': 'All Colleges',
                'degree_type': "Bachelor's",
                'requirement_section': 'Breadth Requirements',
                'course_subject': 'HISTORY',
                'course_number': '1A',
                'course_title': 'Introduction to History',
                'full_course_id': 'HISTORY 1A',
                'requirement_type': 'breadth',
                'units': '4',
                'notes': 'Historical Studies breadth'
            },
            {
                'program_name': 'All Majors',
                'program_code': 'ALL',
                'program_url': 'sample',
                'college': 'All Colleges',
                'degree_type': "Bachelor's",
                'requirement_section': 'Breadth Requirements',
                'course_subject': 'PSYCH',
                'course_number': '1',
                'course_title': 'Introduction to Psychology',
                'full_course_id': 'PSYCH 1',
                'requirement_type': 'breadth',
                'units': '4',
                'notes': 'Social and Behavioral Sciences breadth'
            }
        ]
        
        self.requirements.extend(sample_requirements)
        logger.info(f"Added {len(sample_requirements)} sample requirements")
    
    def scrape_all_majors(self):
        """Try multiple approaches to scrape major requirements"""
        logger.info("Starting major requirements scraping...")
        
        # Try different approaches
        self.try_undergraduate_catalog()
        
        # Add sample data for demonstration
        logger.info("Adding sample data for demonstration...")
        self.create_sample_data()
        
        logger.info(f"Total requirements scraped: {len(self.requirements)}")
    
    def save_to_csv(self, filename='berkeley_major_requirements_final.csv'):
        """Save to CSV"""
        if not self.requirements:
            logger.warning("No requirements to save")
            return
        
        df = pd.DataFrame(self.requirements)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(self.requirements)} requirements to {filename}")
        
        print(f"\nSummary:")
        print(f"Total programs: {df['program_name'].nunique()}")
        print(f"Total requirements: {len(self.requirements)}")
        print(f"Colleges represented: {df['college'].nunique()}")
        print(f"Sample requirements:")
        print(df[['program_name', 'requirement_section', 'full_course_id', 'requirement_type']].head(10).to_string(index=False))

def main():
    scraper = BerkeleyMajorScraper()
    scraper.scrape_all_majors()
    scraper.save_to_csv()

if __name__ == "__main__":
    main()


"""
RAG Pipeline for UC Berkeley Four Year Plan Generator
Uses LangChain with Google Gemini for intelligent schedule generation
"""

import os
import json
import logging
import pandas as pd
from typing import List, Dict, Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)


class BerkeleyRAGPipeline:
    """RAG Pipeline for generating Berkeley course schedules"""

    def __init__(self, api_key: str, courses_df: pd.DataFrame, majors_data: Dict[str, Any]):
        """
        Initialize the RAG pipeline

        Args:
            api_key: Google Gemini API key
            courses_df: DataFrame containing course data
            majors_data: Dictionary of major requirements
        """
        self.api_key = api_key
        self.courses_df = courses_df
        self.majors_data = majors_data

        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.3,
            convert_system_message_to_human=True
        )

        # Initialize embeddings using HuggingFace (local, no API limits)
        # Using all-MiniLM-L6-v2 - fast and good quality for semantic search
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        # Initialize vector store
        self.vectorstore = None
        self.retriever = None

        # Build the vector store
        self._build_vectorstore()

        logger.info("RAG Pipeline initialized successfully")

    def _create_course_documents(self) -> List[Document]:
        """Create LangChain documents from course data"""
        documents = []

        if self.courses_df is None or len(self.courses_df) == 0:
            logger.warning("No course data available")
            return documents

        for _, course in self.courses_df.iterrows():
            # Create a rich text representation of the course
            subject = str(course.get('Subject', '')).strip()
            number = str(course.get('Course Number', '')).strip()
            description = str(course.get('Course Description', '')).strip()
            department = str(course.get('Department(s)', '')).strip()
            units_min = course.get('Credits - Units - Minimum Units', 0)
            units_max = course.get('Credits - Units - Maximum Units', units_min)
            terms = str(course.get('Terms Offered', 'Fall, Spring')).strip()

            # Create course code
            course_code = f"{subject} {number}"

            # Create document content
            content = f"""Course: {course_code}
Title: {description}
Department: {department}
Units: {units_min}-{units_max} if {units_min} != {units_max} else {units_min}
Terms Offered: {terms if terms and terms != '-' else 'Fall, Spring'}
Description: {description}"""

            # Create metadata for filtering
            metadata = {
                'subject': subject,
                'number': number,
                'course_code': course_code,
                'department': department,
                'units_min': int(units_min) if pd.notna(units_min) else 0,
                'units_max': int(units_max) if pd.notna(units_max) else int(units_min) if pd.notna(units_min) else 0,
                'terms': terms if terms and terms != '-' else 'Fall, Spring'
            }

            documents.append(Document(page_content=content, metadata=metadata))

        logger.info(f"Created {len(documents)} course documents")
        return documents

    def _create_major_documents(self) -> List[Document]:
        """Create LangChain documents from major requirements"""
        documents = []

        for major_name, major_info in self.majors_data.items():
            college = major_info.get('college', 'Unknown College')
            total_units = major_info.get('total_units', 120)
            requirements = major_info.get('requirements', {})

            # Create document content for the major
            content = f"""Major: {major_name}
College: {college}
Total Units Required: {total_units}

Requirements:
"""
            for req_type, reqs in requirements.items():
                content += f"\n{req_type.replace('_', ' ').title()}:\n"
                for req in reqs:
                    req_name = req.get('name', '')
                    req_courses = req.get('courses', [])
                    req_units = req.get('units', 0)
                    req_desc = req.get('description', '')
                    content += f"  - {req_name}: {', '.join(req_courses)} ({req_units} units) - {req_desc}\n"

            metadata = {
                'major': major_name,
                'college': college,
                'total_units': total_units,
                'type': 'major_requirements'
            }

            documents.append(Document(page_content=content, metadata=metadata))

        logger.info(f"Created {len(documents)} major requirement documents")
        return documents

    def _build_vectorstore(self):
        """Build the vector store from course and major documents"""
        try:
            # Create documents
            course_docs = self._create_course_documents()
            major_docs = self._create_major_documents()
            all_docs = course_docs + major_docs

            if not all_docs:
                logger.warning("No documents to index")
                return

            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=all_docs,
                embedding=self.embeddings,
                collection_name="berkeley_courses"
            )

            # Create retriever with search parameters
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 20}  # Retrieve top 20 relevant documents
            )

            logger.info(f"Built vector store with {len(all_docs)} documents")

        except Exception as e:
            logger.error(f"Error building vector store: {e}")
            raise

    def _format_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents for the prompt"""
        return "\n\n---\n\n".join([doc.page_content for doc in docs])

    def generate_schedule(
        self,
        major: str,
        graduation_year: int,
        graduation_semester: str = "Spring",
        current_year: Optional[int] = None,
        completed_courses: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a four-year plan using RAG

        Args:
            major: Student's major
            graduation_year: Target graduation year
            graduation_semester: Target graduation semester (Fall/Spring)
            current_year: Student's current academic year
            completed_courses: List of already completed courses
            preferences: Additional preferences

        Returns:
            Dictionary containing the generated schedule
        """
        if self.retriever is None:
            logger.error("Vector store not initialized")
            return self._fallback_schedule(major, graduation_year, graduation_semester)

        completed_courses = completed_courses or []
        current_year = current_year or (graduation_year - 4)
        preferences = preferences or {}

        # Create query for retrieval
        query = f"""UC Berkeley {major} major requirements, course sequences, prerequisites,
        breadth requirements, and recommended courses for a {graduation_semester} {graduation_year} graduation.
        Focus on lower division prerequisites, upper division major requirements, and general education."""

        try:
            # Retrieve relevant documents
            retrieved_docs = self.retriever.invoke(query)
            context = self._format_docs(retrieved_docs)

            # Create the prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert UC Berkeley academic advisor. Your task is to create a comprehensive,
realistic 4-year academic plan based on the provided course catalog and major requirements.

IMPORTANT RULES:
1. Only include courses that exist in the provided course catalog
2. Respect prerequisites and course sequences
3. Balance course load across semesters (12-16 units per semester)
4. Consider term availability for courses
5. Include breadth/general education requirements
6. Do NOT include courses the student has already completed
7. Ensure courses are properly sequenced (lower division before upper division)

CONTEXT FROM COURSE CATALOG AND REQUIREMENTS:
{context}"""),
                ("human", """Create a 4-year academic plan for:
- Major: {major}
- Target Graduation: {graduation_semester} {graduation_year}
- Current Year: {current_year}
- Completed Courses: {completed_courses}

Generate a complete semester-by-semester plan from {current_year} to {graduation_semester} {graduation_year}.

Return ONLY valid JSON in exactly this format (no markdown, no explanation):
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
                    "subject": "SUBJECT",
                    "number": "101",
                    "title": "Course Title",
                    "units": 4,
                    "requirement_type": "lower_division|upper_division|breadth",
                    "requirement_name": "Requirement Category"
                }}
            ],
            "units": 16
        }}
    ],
    "ai_recommendations": "Personalized advice and tips for academic success"
}}""")
            ])

            # Build the chain
            chain = (
                {
                    "context": lambda x: context,
                    "major": lambda x: major,
                    "graduation_semester": lambda x: graduation_semester,
                    "graduation_year": lambda x: graduation_year,
                    "current_year": lambda x: current_year,
                    "completed_courses": lambda x: ", ".join(completed_courses) if completed_courses else "None"
                }
                | prompt_template
                | self.llm
                | StrOutputParser()
            )

            # Generate the response
            logger.info(f"Generating RAG-based schedule for {major}")
            response = chain.invoke({})

            # Parse the JSON response
            schedule = self._parse_schedule_response(response, major, graduation_year, graduation_semester)

            logger.info(f"Successfully generated schedule for {major}")
            return schedule

        except Exception as e:
            logger.error(f"Error generating RAG schedule: {e}", exc_info=True)
            return self._fallback_schedule(major, graduation_year, graduation_semester)

    def _parse_schedule_response(
        self,
        response: str,
        major: str,
        graduation_year: int,
        graduation_semester: str
    ) -> Dict[str, Any]:
        """Parse the LLM response into a schedule dictionary"""
        try:
            # Clean up the response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # Find JSON boundaries
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start_idx:end_idx]
            schedule = json.loads(json_str)

            # Validate required fields
            required_fields = ['major', 'semesters']
            for field in required_fields:
                if field not in schedule:
                    raise ValueError(f"Missing required field: {field}")

            return schedule

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing schedule response: {e}")
            logger.debug(f"Response was: {response[:500]}...")
            return self._fallback_schedule(major, graduation_year, graduation_semester)

    def _fallback_schedule(
        self,
        major: str,
        graduation_year: int,
        graduation_semester: str
    ) -> Dict[str, Any]:
        """Generate a basic fallback schedule when RAG fails"""
        start_year = graduation_year - 4

        # Get major info if available
        major_info = self.majors_data.get(major, {
            'college': 'College of Letters and Science',
            'total_units': 120,
            'requirements': {}
        })

        semesters = []
        for year in range(start_year, graduation_year):
            for term in ['Fall', 'Spring']:
                # Skip semesters after graduation
                if year == graduation_year - 1 and term == 'Spring' and graduation_semester == 'Fall':
                    continue
                if year == graduation_year and term == 'Fall' and graduation_semester == 'Spring':
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

        return {
            'major': major,
            'college': major_info.get('college', 'Unknown College'),
            'graduation_year': graduation_year,
            'graduation_semester': graduation_semester,
            'total_units': major_info.get('total_units', 120),
            'semesters': semesters,
            'ai_recommendations': 'Basic plan generated. For personalized recommendations, please ensure the RAG system is properly configured.'
        }

    def get_ai_suggestions(
        self,
        major: str,
        semester: Dict[str, Any],
        current_courses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get AI-powered course suggestions for a specific semester

        Args:
            major: Student's major
            semester: Semester information (year, term)
            current_courses: Currently planned courses for this semester

        Returns:
            Dictionary with suggestions and advice
        """
        if self.retriever is None:
            return {
                "suggestions": [],
                "advice": "AI suggestions unavailable. Please ensure the system is properly configured."
            }

        try:
            # Create query for relevant courses
            query = f"""UC Berkeley {major} courses available in {semester.get('term', 'Fall')} semester,
            including breadth requirements, electives, and courses that complement:
            {', '.join([f"{c.get('subject', '')} {c.get('number', '')}" for c in current_courses])}"""

            # Retrieve relevant courses
            retrieved_docs = self.retriever.invoke(query)
            context = self._format_docs(retrieved_docs)

            # Create prompt
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are a UC Berkeley academic advisor. Suggest additional courses
based on the provided course catalog and the student's current course selection.

CONTEXT FROM COURSE CATALOG:
{context}"""),
                ("human", """For a {major} major in {term} {year}, with current courses:
{current_courses}

Suggest 3-5 additional courses. Consider:
1. Prerequisites and course sequences
2. Workload balance (aim for 12-16 units total)
3. Course availability in {term}
4. Breadth requirements
5. Major requirements

Return ONLY valid JSON:
{{
    "suggestions": [
        {{
            "subject": "SUBJECT",
            "number": "123",
            "title": "Course Title",
            "units": 4,
            "reason": "Why this course is recommended"
        }}
    ],
    "advice": "General academic advice for this semester"
}}""")
            ])

            # Generate suggestions
            chain = (
                {
                    "context": lambda x: context,
                    "major": lambda x: major,
                    "term": lambda x: semester.get('term', 'Fall'),
                    "year": lambda x: semester.get('year', 2024),
                    "current_courses": lambda x: json.dumps(current_courses, indent=2)
                }
                | prompt_template
                | self.llm
                | StrOutputParser()
            )

            response = chain.invoke({})

            # Parse response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx > 0:
                return json.loads(response[start_idx:end_idx])

        except Exception as e:
            logger.error(f"Error getting AI suggestions: {e}")

        return {
            "suggestions": [],
            "advice": "Unable to generate suggestions at this time. Please try again later."
        }

    def search_courses(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for courses using the vector store

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching courses
        """
        if self.vectorstore is None:
            return []

        try:
            # Search using similarity
            results = self.vectorstore.similarity_search(query, k=limit)

            courses = []
            for doc in results:
                metadata = doc.metadata
                if 'course_code' in metadata:  # Only return course documents
                    courses.append({
                        'code': metadata.get('course_code', ''),
                        'subject': metadata.get('subject', ''),
                        'number': metadata.get('number', ''),
                        'department': metadata.get('department', ''),
                        'units': metadata.get('units_min', 0),
                        'terms': metadata.get('terms', 'Fall, Spring')
                    })

            return courses

        except Exception as e:
            logger.error(f"Error searching courses: {e}")
            return []


# Singleton instance
_rag_pipeline: Optional[BerkeleyRAGPipeline] = None


def get_rag_pipeline() -> Optional[BerkeleyRAGPipeline]:
    """Get the singleton RAG pipeline instance"""
    return _rag_pipeline


def initialize_rag_pipeline(
    api_key: str,
    courses_df: pd.DataFrame,
    majors_data: Dict[str, Any]
) -> BerkeleyRAGPipeline:
    """
    Initialize the RAG pipeline singleton

    Args:
        api_key: Google Gemini API key
        courses_df: DataFrame containing course data
        majors_data: Dictionary of major requirements

    Returns:
        Initialized RAG pipeline instance
    """
    global _rag_pipeline

    try:
        _rag_pipeline = BerkeleyRAGPipeline(api_key, courses_df, majors_data)
        logger.info("RAG Pipeline singleton initialized")
        return _rag_pipeline
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        raise

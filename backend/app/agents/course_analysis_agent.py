"""
Course analysis agent for extracting modules and knowledge points from course content
"""
import json
from typing import Dict, List, Any, Optional
import httpx

from app.core.config import settings
from app.models.course import Course
from app.models.knowledge_point import KnowledgePoint


class CourseAnalysisAgent:
    """
    Specialized agent for analyzing course structure and knowledge points
    """

    def __init__(self):
        """Initialize the course analysis agent"""
        self.client = httpx.AsyncClient(
            base_url=settings.OPENROUTER_BASE_URL,
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=60.0
        )

    async def analyze_course_structure(self, course: Course, additional_content: str = None, model: str = None) -> Dict[str, Any]:
        """
        Analyze course structure and create module/knowledge point breakdown

        Args:
            course: Course database model
            additional_content: Additional course materials to analyze
            model: Optional model name override (defaults to settings.DEFAULT_MODEL)

        Returns:
            Course structure analysis
        """
        # Use provided model or default from settings
        selected_model = model or settings.DEFAULT_MODEL
        # Prepare course content for analysis
        course_content = course.description or ""

        if additional_content:
            course_content += f"\n\nAdditional Content:\n{additional_content}"

        if not course_content.strip():
            return {
                "success": False,
                "error": "No course content available for analysis",
                "modules": [],
                "total_knowledge_points": 0
            }

        prompt = f"""
        You are an expert curriculum designer analyzing the course "{course.title}" in the subject "{course.subject}".

        Based on the course content provided, create a comprehensive course structure by:

        1. **Module Identification**: Divide the course into logical modules/topics
           - Each module should be a coherent unit of study
           - Consider prerequisite relationships between modules
           - Aim for 3-8 modules depending on course scope

        2. **Knowledge Point Extraction**: For each module, identify key knowledge points
           - These are specific concepts, skills, or understandings
           - Include both foundational and advanced knowledge points
           - Consider the hierarchical nature of knowledge

        3. **Difficulty Assessment**: For each knowledge point, assess difficulty
           - Easy: Basic concepts, foundational knowledge
           - Medium: Intermediate application and understanding
           - Hard: Complex applications, advanced concepts

        4. **Learning Dependencies**: Identify prerequisite relationships
           - Which knowledge points/modules are required before others

        Course Content:
        {course_content}

        Return a JSON object with this structure:
        {{
            "course_title": "{course.title}",
            "subject": "{course.subject}",
            "modules": [
                {{
                    "module_id": "unique_id",
                    "module_name": "Name of the module",
                    "description": "Brief description of what this module covers",
                    "prerequisites": ["module_id1", "module_id2"],
                    "knowledge_points": [
                        {{
                            "point_id": "unique_id",
                            "title": "Knowledge point title",
                            "description": "Brief explanation",
                            "difficulty": "easy|medium|hard",
                            "estimated_time_minutes": 30,
                            "tags": ["tag1", "tag2"]
                        }}
                    ]
                }}
            ],
            "learning_path": ["module_id1", "module_id2", ...],
            "total_modules": 0,
            "total_knowledge_points": 0,
            "estimated_course_duration_hours": 0
        }}
        """

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": selected_model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 4096,
                    "temperature": 0.1,  # Low temperature for consistent structure
                }
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                course_structure = json.loads(content)
                course_structure["success"] = True
                return course_structure
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse course structure JSON: {str(e)}",
                    "raw_content": content,
                    "modules": [],
                    "total_knowledge_points": 0
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "modules": [],
                "total_knowledge_points": 0
            }

    async def generate_module_content(self, module_name: str, knowledge_points: List[Dict], model: str = None) -> Dict[str, Any]:
        """
        Generate detailed content for a specific module

        Args:
            module_name: Name of the module
            knowledge_points: List of knowledge points for the module
            model: Optional model name override (defaults to settings.DEFAULT_MODEL)
        """
        # Use provided model or default from settings
        selected_model = model or settings.DEFAULT_MODEL
        knowledge_points_text = "\n".join([
            f"- {kp['title']}: {kp.get('description', '')} (Difficulty: {kp.get('difficulty', 'medium')})"
            for kp in knowledge_points
        ])

        prompt = f"""
        Generate detailed teaching content for the module "{module_name}" with these knowledge points:

        {knowledge_points_text}

        Create a comprehensive module guide that includes:

        1. **Module Overview**: What students will learn and why it's important
        2. **Learning Objectives**: Specific, measurable objectives for each knowledge point
        3. **Key Concepts**: Detailed explanations of each knowledge point
        4. **Examples and Applications**: Real-world examples for each concept
        5. **Practice Activities**: Exercises or activities for each knowledge point
        6. **Assessment Questions**: Sample questions to test understanding

        Structure the response as a JSON object.
        """

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": selected_model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 4096,
                    "temperature": 0.2,
                }
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                module_content = json.loads(content)
                return {"success": True, "module_content": module_content}
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse module content",
                    "raw_content": content
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def assess_student_progress(self, student_assignments: List[Dict], course_structure: Dict, model: str = None) -> Dict[str, Any]:
        """
        Assess student progress across course modules

        Args:
            student_assignments: List of student assignments
            course_structure: Structure of the course
            model: Optional model name override (defaults to settings.DEFAULT_MODEL)
        """
        # Use provided model or default from settings
        selected_model = model or settings.DEFAULT_MODEL
        assignments_summary = "\n".join([
            f"Assignment {i+1}: {assignment.get('title', 'Unknown')} - Status: {assignment.get('status', 'unknown')} - Score: {assignment.get('analysis', {}).get('solution_quality', 'N/A')}/10"
            for i, assignment in enumerate(student_assignments)
        ])

        modules_summary = "\n".join([
            f"Module: {module['module_name']} - Knowledge Points: {len(module.get('knowledge_points', []))}"
            for module in course_structure.get('modules', [])
        ])

        prompt = f"""
        Based on the student's assignment performance and course structure, assess their progress:

        Student Assignments:
        {assignments_summary}

        Course Modules and Knowledge Points:
        {modules_summary}

        Provide a comprehensive progress assessment including:

        1. **Overall Progress**: Current level across the entire course
        2. **Module-by-Module Assessment**: Progress in each module
        3. **Strength Areas**: Modules/concepts where the student excels
        4. **Improvement Areas**: Modules/concepts needing more work
        5. **Knowledge Gaps**: Specific knowledge points that need reinforcement
        6. **Recommendations**: Next steps and focus areas for the student
        7. **Predicted Grade**: Estimated final grade based on current performance

        Return as a JSON object.
        """

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": selected_model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 4096,
                    "temperature": 0.3,
                }
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                progress_assessment = json.loads(content)
                return {"success": True, "progress_assessment": progress_assessment}
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse progress assessment",
                    "raw_content": content
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_course_from_analysis(self, course: Course, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update course model with analysis results
        """
        try:
            # Update course modules in database
            if analysis_result.get("success") and "modules" in analysis_result:
                modules_data = json.dumps(analysis_result["modules"])
                course.modules = modules_data
                # Note: In a real implementation, you'd save this to the database

            return {
                "success": True,
                "message": f"Course '{course.title}' updated with analysis results",
                "modules_count": len(analysis_result.get("modules", [])),
                "knowledge_points_count": analysis_result.get("total_knowledge_points", 0)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def __aenter__(self):
        """Async context manager enter"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()


# Global instance
course_analysis_agent = CourseAnalysisAgent()
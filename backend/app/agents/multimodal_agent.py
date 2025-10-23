"""
Multimodal AI agents for assignment analysis using OpenRouter and Grok
"""
import base64
import json
from typing import Dict, List, Any, Optional
import httpx
from pathlib import Path

from app.core.config import settings
from app.services.knowledge_base import knowledge_base


class MultimodalAgent:
    """
    Multimodal agent for analyzing assignments, extracting knowledge points,
    and providing educational insights
    """

    def __init__(self):
        """Initialize the multimodal agent"""
        self.client = httpx.AsyncClient(
            base_url=settings.OPENROUTER_BASE_URL,
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=60.0
        )

    async def analyze_assignment_image(self, image_path: str, course_name: str = None, model: str = None) -> Dict[str, Any]:
        """
        Analyze an assignment image using multimodal capabilities

        Args:
            image_path: Path to the assignment image
            course_name: Optional course name for context
            model: Optional model name override (defaults to settings.DEFAULT_MODEL)

        Returns:
            Dictionary with analysis results
        """
        try:
            # Use provided model or default from settings
            selected_model = model or settings.DEFAULT_MODEL
            # Read image and encode as base64
            with open(image_path, "rb") as f:
                image_data = f.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')

            context = f" for the course '{course_name}'" if course_name else ""

            prompt = f"""
            You are an expert educational assistant analyzing a student's assignment{context}.

            Please analyze this assignment image and provide:

            1. **Subject/Content Recognition**: What subject and topics are covered?
            2. **Knowledge Points Covered**: List the specific knowledge points or concepts demonstrated
            3. **Problem Analysis**: Identify what problems/questions are being worked on
            4. **Solution Quality**: Assess the correctness and completeness of solutions
            5. **Common Errors**: Note any mistakes or misconceptions
            6. **Knowledge Gaps**: Areas where the student seems to lack understanding
            7. **Improvement Suggestions**: Specific recommendations for the student

            Please structure your response as a JSON object with these keys:
            - subject
            - topics
            - knowledge_points
            - problems_analyzed
            - solution_quality (1-10 scale)
            - common_errors
            - knowledge_gaps
            - improvement_suggestions
            - overall_assessment

            Be thorough but concise in your analysis.
            """

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ]

            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": selected_model,
                    "messages": messages,
                    "max_tokens": 4096,
                    "temperature": 0.3,
                }
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Try to parse JSON response
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, create structured response from text
                analysis = self._parse_text_response(content)

            return {
                "success": True,
                "file_path": image_path,
                "analysis": analysis,
                "raw_response": content
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": image_path,
                "analysis": None
            }

    async def extract_course_modules(self, course_content: str, course_name: str, model: str = None) -> Dict[str, Any]:
        """
        Extract course modules and structure from course content

        Args:
            course_content: The course content to analyze
            course_name: Name of the course
            model: Optional model name override (defaults to settings.DEFAULT_MODEL)
        """
        # Use provided model or default from settings
        selected_model = model or settings.DEFAULT_MODEL
        prompt = f"""
        You are analyzing the content for the course "{course_name}".

        Based on the provided course content, please:

        1. Identify the main modules/topics that this course should be divided into
        2. For each module, list the key knowledge points/concepts
        3. Assess the difficulty level for each knowledge point (easy/medium/hard)
        4. Suggest a logical learning sequence for the modules

        Course Content:
        {course_content[:4000]}...  # Truncate for token limits

        Please respond with a JSON object containing:
        - course_name
        - modules (array of objects with: name, knowledge_points, difficulty_assessment)
        - learning_sequence (array of module names in recommended order)
        - total_knowledge_points
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
                course_structure = json.loads(content)
                return {"success": True, "course_structure": course_structure}
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse course structure",
                    "raw_content": content
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_study_recommendations(self, student_performance: Dict[str, Any], model: str = None) -> Dict[str, Any]:
        """
        Generate personalized study recommendations based on student performance

        Args:
            student_performance: Student performance data
            model: Optional model name override (defaults to settings.DEFAULT_MODEL)
        """
        # Use provided model or default from settings
        selected_model = model or settings.DEFAULT_MODEL
        prompt = f"""
        Based on this student's performance analysis, generate personalized study recommendations:

        Student Performance Data:
        {json.dumps(student_performance, indent=2)}

        Please provide:
        1. Key areas needing immediate focus
        2. Specific study strategies for each weak area
        3. Recommended practice problems or exercises
        4. Long-term learning plan
        5. Resources or materials that would be helpful

        Structure your response as a JSON object with these sections.
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
                recommendations = json.loads(content)
                return {"success": True, "recommendations": recommendations}
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse recommendations",
                    "raw_content": content
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def correlate_errors_with_knowledge_points(self, assignment_analysis: Dict[str, Any], course_structure: Dict[str, Any], model: str = None) -> Dict[str, Any]:
        """
        Correlate student errors with specific knowledge points and modules

        Args:
            assignment_analysis: Analysis of the assignment
            course_structure: Structure of the course
            model: Optional model name override (defaults to settings.DEFAULT_MODEL)
        """
        # Use provided model or default from settings
        selected_model = model or settings.DEFAULT_MODEL
        prompt = f"""
        Analyze how student errors in this assignment correlate with course knowledge points:

        Assignment Analysis:
        {json.dumps(assignment_analysis, indent=2)}

        Course Structure:
        {json.dumps(course_structure, indent=2)}

        Please identify:
        1. Which knowledge points are involved in the student's errors
        2. Which modules these knowledge points belong to
        3. Whether errors indicate systematic misunderstandings in certain modules
        4. Priority order for addressing these knowledge gaps

        Respond with a JSON object mapping errors to knowledge points and modules.
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
                error_correlation = json.loads(content)
                return {"success": True, "error_correlation": error_correlation}
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse error correlation",
                    "raw_content": content
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """
        Parse text response into structured format when JSON parsing fails
        """
        # Simple fallback parsing - in production you'd want better NLP parsing
        return {
            "subject": "Unknown",
            "topics": [],
            "knowledge_points": [],
            "problems_analyzed": [],
            "solution_quality": 5,
            "common_errors": [],
            "knowledge_gaps": [],
            "improvement_suggestions": [],
            "overall_assessment": text[:500] + "..." if len(text) > 500 else text
        }

    async def __aenter__(self):
        """Async context manager enter"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()


# Global instance
multimodal_agent = MultimodalAgent()
"""
Assignment upload and analysis workflow service
"""
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.assignment import Assignment
from app.models.course import Course
from app.services.doc_scanner import DocScanner
from app.services.knowledge_base import knowledge_base
from app.agents.multimodal_agent import multimodal_agent
from app.agents.course_analysis_agent import course_analysis_agent
from app.db.session import get_db


class AssignmentWorkflowService:
    """
    Service for handling complete assignment upload and analysis workflow
    """

    @staticmethod
    def _generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename"""
        file_extension = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"

    @staticmethod
    def _ensure_upload_dir() -> Path:
        """Ensure upload directory exists"""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

    @staticmethod
    async def process_assignment_upload(
        db: AsyncSession,
        file_data: bytes,
        filename: str,
        student_id: int,
        course_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow for processing an assignment upload

        Steps:
        1. Save uploaded file
        2. Document correction with DocScanner
        3. Multimodal analysis with AI agent
        4. Course structure correlation
        5. Knowledge base queries for context
        6. Generate comprehensive analysis report
        """
        try:
            # Step 1: Save uploaded file
            original_filename = filename
            unique_filename = AssignmentWorkflowService._generate_unique_filename(filename)
            upload_dir = AssignmentWorkflowService._ensure_upload_dir()

            original_path = upload_dir / f"original_{unique_filename}"
            with open(original_path, "wb") as f:
                f.write(file_data)

            # Step 2: Document correction
            doc_scanner_result = DocScanner.scan_document(file_data)

            corrected_path = None
            if doc_scanner_result["success"]:
                corrected_filename = f"corrected_{unique_filename}"
                corrected_path = upload_dir / corrected_filename

                # Save corrected image
                corrected_image = doc_scanner_result["corrected_image"]
                if corrected_image is not None:
                    # Convert numpy array back to image if needed
                    import cv2
                    cv2.imwrite(str(corrected_path), corrected_image)

            # Step 3: Create initial assignment record
            assignment = Assignment(
                title=f"Assignment Upload - {original_filename}",
                student_id=student_id,
                course_id=None,  # We can set this from course name later if needed
                original_filename=original_filename,
                corrected_filename=os.path.basename(corrected_path) if corrected_path else None,
                status="processing"
            )

            db.add(assignment)
            await db.commit()
            await db.refresh(assignment)

            # Step 4: Multimodal analysis
            analysis_image_path = str(corrected_path) if corrected_path else str(original_path)

            async with multimodal_agent as agent:
                assignment_analysis = await agent.analyze_assignment_image(
                    analysis_image_path,
                    course_name
                )

            # Step 5: Course correlation and knowledge base lookup
            course_structure = None
            error_correlation = None

            if course_name and assignment_analysis["success"]:
                # Get course structure (would need course ID in real implementation)
                # For now, we'll do general knowledge base queries

                # Query knowledge base for course-related insights
                course_query = f"What are the key topics in {course_name}?"
                kb_result = await knowledge_base.query_knowledge(course_query)

                # Correlate assignment errors with course knowledge
                if assignment_analysis["success"] and kb_result:
                    async with course_analysis_agent as course_agent:
                        error_correlation = await course_agent.assess_student_progress(
                            [assignment_analysis],
                            {"course_name": course_name, "kb_insights": kb_result}
                        )

            # Step 6: Extract and store analysis results
            analysis_results = {
                "doc_correction": {
                    "success": doc_scanner_result["success"],
                    "skew_angle": doc_scanner_result["skew_angle"],
                    "contour_found": doc_scanner_result["contour_found"]
                },
                "multimodal_analysis": assignment_analysis,
                "knowledge_correlation": error_correlation.get("progress_assessment") if error_correlation and error_correlation["success"] else None,
                "course_name": course_name,
                "processing_timestamp": datetime.utcnow().isoformat()
            }

            # Update assignment with analysis results
            assignment.analysis_results = str(analysis_results)
            assignment.status = "completed"

            # Extract meaningful error points and knowledge gaps if available
            if assignment_analysis["success"] and "analysis" in assignment_analysis:
                analysis_data = assignment_analysis["analysis"]
                assignment.error_points = str({
                    "common_errors": analysis_data.get("common_errors", []),
                    "solution_quality": analysis_data.get("solution_quality", 5)
                })
                assignment.knowledge_gaps = str({
                    "gaps": analysis_data.get("knowledge_gaps", []),
                    "recommendations": analysis_data.get("improvement_suggestions", [])
                })

            await db.commit()

            # Step 7: Add to knowledge base for future reference
            if assignment_analysis["success"]:
                analysis_text = f"""
                Assignment Analysis for {course_name or 'General Subject'}:

                Subject: {assignment_analysis['analysis'].get('subject', 'Unknown')}
                Topics: {', '.join(assignment_analysis['analysis'].get('topics', []))}
                Key Findings: {assignment_analysis['analysis'].get('overall_assessment', '')}

                This analysis can help understand common patterns in student learning.
                """

                await knowledge_base.add_document(
                    analysis_text,
                    doc_id=f"assignment_analysis_{assignment.id}",
                    metadata={
                        "assignment_id": assignment.id,
                        "student_id": student_id,
                        "course_name": course_name,
                        "analysis_type": "assignment_review",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

            return {
                "success": True,
                "assignment_id": assignment.id,
                "status": "completed",
                "files": {
                    "original": str(original_path),
                    "corrected": str(corrected_path) if corrected_path else None
                },
                "analysis": analysis_results,
                "processing_summary": {
                    "total_steps": 7,
                    "completed_steps": 7,
                    "doc_correction_applied": doc_scanner_result["success"],
                    "multimodal_analysis_complete": assignment_analysis["success"],
                    "knowledge_correlation_done": error_correlation is not None and error_correlation.get("success", False)
                }
            }

        except Exception as e:
            # Update assignment status to failed if it was created
            if 'assignment' in locals():
                assignment.status = "failed"
                await db.commit()

            return {
                "success": False,
                "error": str(e),
                "stage": "upload_processing"
            }

    @staticmethod
    async def get_assignment_analysis(
        db: AsyncSession,
        assignment_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Retrieve complete assignment analysis
        """
        try:
            from app.models.assignment import Assignment
            from app.services.user import UserService

            assignment = await db.get(Assignment, assignment_id)
            if not assignment:
                return {"success": False, "error": "Assignment not found"}

            # Check permissions (only student or assigned teacher can view)
            if assignment.student_id != user_id:
                # In real implementation, check if user is a teacher for this course
                user = await UserService.get_by_id(db, user_id)
                if not user or not user.is_superuser:
                    return {"success": False, "error": "Access denied"}

            return {
                "success": True,
                "assignment": {
                    "id": assignment.id,
                    "title": assignment.title,
                    "original_filename": assignment.original_filename,
                    "corrected_filename": assignment.corrected_filename,
                    "status": assignment.status,
                    "created_at": assignment.created_at.isoformat(),
                    "analysis_results": assignment.analysis_results,
                    "error_points": assignment.error_points,
                    "knowledge_gaps": assignment.knowledge_gaps
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_student_progress_summary(
        db: AsyncSession,
        student_id: int,
        course_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive student progress summary
        """
        try:
            from app.models.assignment import Assignment
            from sqlalchemy import select

            query = select(Assignment).where(
                Assignment.student_id == student_id,
                Assignment.status == "completed"
            )

            if course_name:
                # Note: In real implementation, you'd filter by course_id
                pass

            result = await db.execute(query)
            assignments = result.scalars().all()

            # Analyze all completed assignments
            assignment_summaries = []
            total_quality = 0
            assignment_count = 0

            for assignment in assignments:
                if assignment.analysis_results:
                    analysis_data = assignment.analysis_results
                    if "multimodal_analysis" in analysis_data:
                        analysis = analysis_data["multimodal_analysis"]
                        if analysis["success"] and "analysis" in analysis:
                            assignment_count += 1
                            quality = analysis["analysis"].get("solution_quality", 5)
                            total_quality += quality

                            assignment_summaries.append({
                                "assignment_id": assignment.id,
                                "title": assignment.title,
                                "quality_score": quality,
                                "topics": analysis["analysis"].get("topics", []),
                                "strengths": analysis["analysis"].get("knowledge_points", [])[:3],  # Top 3
                                "improvement_areas": analysis["analysis"].get("knowledge_gaps", [])[:3]  # Top 3
                            })

            avg_quality = total_quality / assignment_count if assignment_count > 0 else 0

            return {
                "success": True,
                "student_id": student_id,
                "total_assignments": len(assignments),
                "analyzed_assignments": assignment_count,
                "average_quality_score": round(avg_quality, 1),
                "progress_summary": assignment_summaries,
                "overall_performance": AssignmentWorkflowService._assess_overall_performance(avg_quality)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _assess_overall_performance(avg_quality: float) -> str:
        """
        Assess overall student performance based on average quality score
        """
        if avg_quality >= 8.0:
            return "Excellent - Demonstrating strong understanding and application"
        elif avg_quality >= 7.0:
            return "Good - Solid grasp of concepts with room for deeper understanding"
        elif avg_quality >= 6.0:
            return "Satisfactory - Basic understanding achieved, needs practice"
        elif avg_quality >= 5.0:
            return "Needs Improvement - Review fundamental concepts"
        else:
            return "Significant Support Needed - Focus on foundational knowledge"


# Global instance
assignment_workflow = AssignmentWorkflowService()
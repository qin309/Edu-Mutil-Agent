"""
Assignment management endpoints
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.db.session import get_db
from app.core.deps import get_current_active_user
from app.models.user import User as UserModel
from app.services.assignment_workflow import assignment_workflow

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_assignment(
    file: UploadFile = File(...),
    course_name: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> dict:
    """
    Upload and process a student assignment
    """
    try:
        # Read file content
        file_content = await file.read()

        # Validate file type (images only)
        allowed_content_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/tiff",
            "image/bmp"
        ]

        if file.content_type not in allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed. Only image files are supported."
            )

        # Process the assignment
        result = await assignment_workflow.process_assignment_upload(
            db=db,
            file_data=file_content,
            filename=file.filename,
            student_id=current_user.id,
            course_name=course_name
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: {result.get('error', 'Unknown error')}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/")
async def get_user_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 50
) -> List[dict]:
    """
    Get user's assignments
    """
    from app.models.assignment import Assignment
    from sqlalchemy import select, desc

    try:
        query = select(Assignment).where(
            Assignment.student_id == current_user.id
        ).order_by(desc(Assignment.created_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        assignments = result.scalars().all()

        return [{
            "id": assignment.id,
            "title": assignment.title,
            "original_filename": assignment.original_filename,
            "corrected_filename": assignment.corrected_filename,
            "status": assignment.status,
            "created_at": assignment.created_at.isoformat() if assignment.created_at else None,
            "analysis_available": assignment.analysis_results is not None
        } for assignment in assignments]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assignments: {str(e)}"
        )


@router.get("/{assignment_id}")
async def get_assignment_analysis(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> dict:
    """
    Get detailed assignment analysis
    """
    result = await assignment_workflow.get_assignment_analysis(
        db=db,
        assignment_id=assignment_id,
        user_id=current_user.id
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in result["error"].lower() else status.HTTP_403_FORBIDDEN,
            detail=result["error"]
        )

    return result["assignment"]


@router.get("/{assignment_id}/file/{file_type}")
async def get_assignment_file(
    assignment_id: int,
    file_type: str,  # "original" or "corrected"
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> FileResponse:
    """
    Get assignment file (original or corrected)
    """
    from app.models.assignment import Assignment

    try:
        assignment = await db.get(Assignment, assignment_id)
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

        # Check permissions
        if assignment.student_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Determine filename
        if file_type == "original":
            filename = assignment.original_filename
            file_path = Path(settings.UPLOAD_DIR) / f"original_{assignment.id}_{filename}"
        elif file_type == "corrected":
            if not assignment.corrected_filename:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Corrected file not available")
            filename = assignment.corrected_filename
            file_path = Path(settings.UPLOAD_DIR) / filename
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")

        if not file_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="image/jpeg"  # General image type
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve file: {str(e)}"
        )


@router.get("/progress/summary")
async def get_progress_summary(
    course_name: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> dict:
    """
    Get student progress summary
    """
    result = await assignment_workflow.get_student_progress_summary(
        db=db,
        student_id=current_user.id,
        course_name=course_name
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate progress summary: {result.get('error', 'Unknown error')}"
        )

    return result


@router.post("/{assignment_id}/reanalyze")
async def reanalyze_assignment(
    assignment_id: int,
    course_name: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> dict:
    """
    Re-analyze an existing assignment with new parameters
    """
    from app.models.assignment import Assignment

    try:
        assignment = await db.get(Assignment, assignment_id)
        if not assignment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

        if assignment.student_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Update status to processing
        assignment.status = "processing"
        await db.commit()

        # Get file paths
        upload_dir = Path(settings.UPLOAD_DIR)
        corrected_path = upload_dir / assignment.corrected_filename if assignment.corrected_filename else None

        analysis_path = str(corrected_path) if corrected_path and corrected_path.exists() else None
        if not analysis_path:
            # Try original file
            original_pattern = f"original_*{assignment.original_filename}"
            for file_path in upload_dir.glob(original_pattern):
                analysis_path = str(file_path)
                break

        if not analysis_path:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment files not found")

        # Re-run multimodal analysis with new course context
        async with multimodal_agent as agent:
            assignment_analysis = await agent.analyze_assignment_image(
                analysis_path,
                course_name
            )

        if assignment_analysis["success"]:
            # Update analysis results
            current_results = assignment.analysis_results or "{}"
            import json
            existing_results = json.loads(current_results) if current_results else {}

            existing_results["multimodal_analysis"] = assignment_analysis
            existing_results["course_name"] = course_name
            existing_results["reanalyzed_at"] = str(datetime.utcnow())

            assignment.analysis_results = json.dumps(existing_results)
            assignment.status = "completed"
            await db.commit()

        return {
            "success": True,
            "assignment_id": assignment_id,
            "reanalysis_complete": assignment_analysis["success"],
            "updated_analysis": assignment_analysis
        }

    except HTTPException:
        # Reset status if permission/file error
        if 'assignment' in locals() and isinstance(assignment, Assignment):
            assignment.status = "completed"
            await db.commit()
        raise
    except Exception as e:
        # Reset status on error
        if 'assignment' in locals() and isinstance(assignment, Assignment):
            assignment.status = "completed"
            await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Re-analysis failed: {str(e)}"
        )
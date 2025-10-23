"""
Knowledge base API endpoints
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel

from app.services.knowledge_base import knowledge_base

# Knowledge space management endpoints
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


class KnowledgeQuery(BaseModel):
    """Knowledge query request model"""
    question: str
    mode: str = "hybrid"  # naive, local, global, hybrid
    model: Optional[str] = None  # Optional model override


class KnowledgeQueryResponse(BaseModel):
    """Knowledge query response model"""
    question: str
    answer: str
    sources: List[str]
    mode: str


class DocumentAdd(BaseModel):
    """Document addition request model"""
    content: str
    title: str
    metadata: Dict[str, Any] = {}


class SpaceCreate(BaseModel):
    """Knowledge space creation request model"""
    space_name: str


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(
    query: KnowledgeQuery,
    space_name: Optional[str] = None,
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for debugging
) -> KnowledgeQueryResponse:
    """
    Query the knowledge base using LightRAG with timeout protection and fallback strategies
    """
    try:
        print(f"[API] Received knowledge query: {query.question[:50]}... for space '{space_name}'")
        print(f"[API] Query mode: {query.mode}, model: {query.model}")
        
        if knowledge_base is None:
            print("[API] ERROR: knowledge_base is None")
            fallback_answer = _get_educational_fallback(query.question)
            return KnowledgeQueryResponse(
                question=query.question,
                answer=f"Knowledge base service not initialized. {fallback_answer}",
                sources=["System Fallback"],
                mode="service_error"
            )
            
        print(f"[API] Knowledge base available for space '{space_name}': {knowledge_base.is_available(space_name)}")
        
        if knowledge_base.is_available(space_name):
            print(f"[API] Calling LightRAG knowledge_base.query_knowledge...")
            try:
                # Apply timeout protection to prevent hanging (increased by 1 minute as requested)
                import asyncio
                result = await asyncio.wait_for(
                    knowledge_base.query_knowledge(
                        question=query.question,
                        mode=query.mode,
                        space_name=space_name,
                        model=query.model
                    ),
                    timeout=90.0  # 90 second timeout (30s + 1 minute as requested)
                )
                print(f"[API] LightRAG query completed, answer length: {len(str(result.get('answer', '')))}")
                
                # Return successful LightRAG response
                return KnowledgeQueryResponse(
                    question=query.question,
                    answer=result["answer"],
                    sources=result.get("sources", ["Knowledge Base"]),
                    mode=result.get("mode", query.mode)
                )
                
            except asyncio.TimeoutError:
                print(f"[API] LightRAG query timed out after 90s, using educational fallback")
                # Implement immediate educational fallback (based on memory: "Knowledge Query Fallback Strategy")
                fallback_answer = _get_educational_fallback(query.question)
                return KnowledgeQueryResponse(
                    question=query.question,
                    answer=f"Query processing took longer than expected. Here's some guidance while the system optimizes: \n\n{fallback_answer}",
                    sources=["Educational Fallback"],
                    mode="timeout_fallback"
                )
            except Exception as e:
                print(f"[API] LightRAG query failed: {e}")
                import traceback
                traceback.print_exc()
                
                # Provide educational fallback on error
                fallback_answer = _get_educational_fallback(query.question)
                return KnowledgeQueryResponse(
                    question=query.question,
                    answer=f"Knowledge retrieval encountered an issue. Here's educational guidance: \n\n{fallback_answer}",
                    sources=["Error Fallback"],
                    mode="error_fallback"
                )
        else:
            print(f"[API] Knowledge base not available, using educational fallback")
            # Fallback when LightRAG is not available
            fallback_answer = _get_educational_fallback(query.question)
            return KnowledgeQueryResponse(
                question=query.question,
                answer=fallback_answer,
                sources=["Educational Assistant"],
                mode="unavailable_fallback"
            )

    except Exception as e:
        print(f"[API] ERROR in query_knowledge: {e}")
        import traceback
        traceback.print_exc()
        
        # Always provide educational response even on system errors
        fallback_answer = _get_educational_fallback(query.question)
        return KnowledgeQueryResponse(
            question=query.question,
            answer=f"System error occurred. Here's educational support: \n\n{fallback_answer}",
            sources=["System Error Handler"],
            mode="system_error"
        )


def _get_educational_fallback(question: str) -> str:
    """
    Provide educational fallback responses when AI is unavailable
    """
    question_lower = question.lower()

    if any(keyword in question_lower for keyword in ["formula", "equation", "calculation", "solve"]):
        return """
**Problem-Solving Strategy:**

When facing mathematical problems, follow this approach:

1. **Understand the Problem**: Read carefully, identify what's given and what's needed

2. **Choose a Strategy**: Consider these methods:
   - Work backwards
   - Use similar problems as patterns
   - Visualize the problem
   - Try smaller numbers first

3. **Solve Step by Step**: Write out each step clearly

4. **Check Your Work**: Verify your answer makes sense

**Example Process:**
- What type of problem is this? (Geometry, Algebra, etc.)
- What formulas should I use?
- Are the units consistent?

*Upload your assignment for guided step-by-step help!*"""

    elif any(keyword in question_lower for keyword in ["concept", "understand", "explain", "meaning"]):
        return """
**Understanding Concepts:**

To deeply understand any subject:

🔍 **Active Learning:**
- Explain the concept in your own words
- Connect it to real-world examples
- Ask: "Why?" at every step

🧠 **Memory Techniques:**
- Use analogies and metaphors
- Create visual mind maps
- Teach the concept to someone else

📚 **Application Focus:**
- Practice with similar problems
- Identify common mistake patterns
- Build connections to related topics

**Key Question**: Can you restate this concept differently? That's the first sign of true understanding.

*For personalized concept explanations, please provide specific details about what you're studying!*"""

    else:
        return f"""
**Learning Support:**

I understand you'd like to learn about: "{question}"

Here are some proven learning strategies that work for most students:

📝 **Study Techniques:**
• **Active Recall**: Test yourself without looking at answers
• **Spaced Repetition**: Review material at increasing intervals
• **Interleaved Practice**: Mix different types of problems
• **Self-Explanation**: Explain why each step works

🎯 **Goal Setting:**
• Break large topics into manageable chunks
• Set specific, measurable study goals
• Track your progress regularly
• Celebrate small victories

💪 **Mindset Matters:**
• See challenges as opportunities to grow
• Persist through difficult concepts
• Learn from mistakes rather than avoiding them

**Getting Specific Help:**
For detailed explanations of specific topics or assignments, try uploading your coursework for AI-powered analysis and personalized guidance.

*How can I help you achieve your learning goals today?*"""


@router.post("/add-document")
async def add_document(
    document: DocumentAdd,
    space_name: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Add a document to the knowledge base (supports space parameter)
    """
    try:
        # Add user-specific metadata
        metadata = document.metadata.copy()
        metadata.update({
            "added_by": current_user.email,
            "user_id": current_user.id,
            "title": document.title
        })

        success = await knowledge_base.add_document(
            content=document.content,
            title=document.title,
            doc_type="text/plain",
            metadata=metadata,
            space_name=space_name
        )

        if success:
            return {"message": "Document added successfully", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add document to knowledge base"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document addition failed: {str(e)}"
        )


@router.get("/status")
async def get_knowledge_base_status(
    space_name: Optional[str] = None,
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for debugging
) -> Dict[str, Any]:
    """
    Get knowledge base status (supports space parameter)
    """
    return {
        "available": knowledge_base.is_available(space_name),
        "space_name": space_name or "default",
        "message": f"Knowledge base is ready for space '{space_name or 'default'}'" if knowledge_base.is_available(space_name) else f"Knowledge base not available for space '{space_name or 'default'}'"
    }


@router.get("/course-structure/{course_name}")
async def get_course_structure(
    course_name: str,
    space_name: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get course structure and knowledge points (supports space parameter)
    """
    try:
        result = await knowledge_base.get_course_structure(course_name, space_name)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get course structure: {str(e)}"
        )


@router.post("/upload-document", status_code=status.HTTP_201_CREATED)
async def upload_knowledge_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    course_name: Optional[str] = Form(None),
    space_name: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Upload a document to the knowledge base and process it with LightRAG
    Supports: .txt, .md, .pdf, .docx files
    space_name: Target knowledge space (defaults to 'default')
    model: Optional AI model for document indexing
    """
    try:
        # Read file content
        file_content = await file.read()

        # Validate file size (limit to 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size too large. Maximum allowed size is 10MB."
            )

        # Process file and add to knowledge base in background
        result = await knowledge_base.process_file_upload(
            file_content=file_content,
            filename=file.filename,
            title=title,
            user_id=str(current_user.id),
            course_name=course_name,
            space_name=space_name or "default",
            model=model
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to process document")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/documents")
async def get_knowledge_documents(
    space_name: Optional[str] = None,
    # current_user: User = Depends(get_current_user),  # Temporarily disabled for debugging
) -> Dict[str, Any]:
    """
    Get list of documents in knowledge base (supports space parameter)
    """
    try:
        documents = knowledge_base.get_documents_list(space_name)
        stats = knowledge_base.get_stats(space_name)

        return {
            "documents": documents,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get documents: {str(e)}"
        )


@router.delete("/documents/{document_title}")
async def delete_knowledge_document(
    document_title: str,
    space_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Delete a document from knowledge base (supports space parameter)
    """
    try:
        # URL decode the document title
        import urllib.parse
        decoded_title = urllib.parse.unquote(document_title)

        # Delete the document using the knowledge base service
        success = await knowledge_base.delete_document(decoded_title, space_name)

        if success:
            return {
                "success": True,
                "message": f"Document '{decoded_title}' successfully deleted from knowledge base"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{decoded_title}' not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}"
        )


# Knowledge Space Management Endpoints

@router.post("/spaces", response_model=Dict[str, Any])
async def create_knowledge_space(
    space_data: SpaceCreate,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Create a new knowledge space
    """
    try:
        success = knowledge_base.create_space(space_data.space_name)

        if success:
            return {
                "success": True,
                "message": f"Knowledge space '{space_data.space_name}' created successfully",
                "space_name": space_data.space_name
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create knowledge space"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Space creation failed: {str(e)}"
        )


@router.get("/spaces", response_model=List[Dict[str, Any]])
async def get_knowledge_spaces(
    # current_user: User = Depends(get_current_user),  # Temporarily disabled for debugging
) -> List[Dict[str, Any]]:
    """
    Get list of all knowledge spaces with their stats
    """
    try:
        return knowledge_base.get_spaces_info()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge spaces: {str(e)}"
        )


@router.get("/spaces/list", response_model=List[str])
async def list_knowledge_spaces(
    current_user: User = Depends(get_current_user),
) -> List[str]:
    """
    Get list of all knowledge space names
    """
    try:
        return knowledge_base.list_spaces()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list knowledge spaces: {str(e)}"
        )


@router.get("/graph")
async def get_knowledge_base_graph(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get knowledge base graph data for visualization
    """
    try:
        # Check if LightRAG is available
        if not knowledge_base.is_available():
            # Return mock data for demonstration
            return {
                "entities": [
                    {
                        "id": "1",
                        "label": "Machine Learning",
                        "type": "concept",
                        "properties": {}
                    },
                    {
                        "id": "2",
                        "label": "Neural Networks",
                        "type": "concept",
                        "properties": {}
                    },
                    {
                        "id": "3",
                        "label": "Deep Learning",
                        "type": "concept",
                        "properties": {}
                    },
                    {
                        "id": "4",
                        "label": "Python",
                        "type": "tool",
                        "properties": {}
                    },
                ],
                "relationships": [
                    {
                        "source": "1",
                        "target": "2",
                        "type": "includes",
                        "weight": 0.8
                    },
                    {
                        "source": "2",
                        "target": "3",
                        "type": "subtype",
                        "weight": 0.9
                    },
                    {
                        "source": "1",
                        "target": "4",
                        "type": "uses",
                        "weight": 0.7
                    },
                ]
            }

        # Try to get graph data from LightRAG
        try:
            graph_data = knowledge_base.get_graph()
            return {
                "entities": graph_data.get("entities", []),
                "relationships": graph_data.get("relationships", []),
                "chunks": graph_data.get("chunks", [])
            }
        except Exception as e:
            print(f"Failed to get graph from LightRAG: {e}")
            # Return mock data as fallback
            return {
                "entities": [
                    {
                        "id": "1",
                        "label": "Sample Concept",
                        "type": "concept",
                        "properties": {}
                    }
                ],
                "relationships": [],
                "chunks": []
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get graph: {str(e)}"
        )


@router.get("/stats")
async def get_knowledge_base_stats(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get knowledge base statistics
    """
    try:
        stats = knowledge_base.get_stats()
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
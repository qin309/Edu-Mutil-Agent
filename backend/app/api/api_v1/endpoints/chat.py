"""
Chat API endpoints
"""
import json
import httpx
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter()


async def call_chat_api(message: str, model: str = None) -> str:
    """
    Direct chat API call to SiliconFlow without knowledge base integration

    Args:
        message: The user's message
        model: Optional model name override (defaults to Pro/moonshotai/Kimi-K2-Instruct-0905)

    Returns:
        AI response as string
    """
    try:
        # Use SiliconFlow API with specified model
        selected_model = model or "Pro/moonshotai/Kimi-K2-Instruct-0905"
        api_key = settings.SILICONFLOW_API_KEY or "sk-mczrhquoybaxwicxgsfdaereipgbapmtiersywbzkorjogla"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.siliconflow.cn/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": selected_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful AI assistant. Please provide clear and accurate responses."
                        },
                        {
                            "role": "user",
                            "content": message
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "stream": False
                }
            )

            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "I apologize, but I couldn't generate a response right now.")

    except httpx.TimeoutException:
        return "I'm sorry, the AI service is taking too long to respond. Please try again."
    except httpx.HTTPStatusError as e:
        print(f"SiliconFlow API error: {e.response.status_code} - {e.response.text}")
        return f"I encountered an error while processing your request ({e.response.status_code}). Please try again."
    except Exception as e:
        print(f"Error calling SiliconFlow API: {e}")
        return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."


class ChatMessage(BaseModel):
    """Chat message request model"""
    message: str
    student_id: str
    model: Optional[str] = None  # Optional model name override


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    sources: List[str] = []
    message_id: str = ""


# Simple test endpoint to verify routing works
@router.get("/test")
async def test_chat_endpoint():
    return {"message": "Chat API routing is working", "endpoint": "chat/test"}

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    chat_message: ChatMessage,
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for testing
) -> ChatResponse:
    """
    Simple chat endpoint - directly calls AI model without knowledge base integration
    """
    try:
        # Direct API call to SiliconFlow
        ai_response = await call_chat_api(
            message=chat_message.message,
            model=chat_message.model
        )

        return ChatResponse(
            response=ai_response,
            sources=["SiliconFlow AI"],
            message_id=f"chat_{int(__import__('time').time())}"
        )

    except Exception as e:
        print(f"Chat API error: {e}")
        # Simple fallback response
        return ChatResponse(
            response="I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
            sources=["System"],
            message_id=f"error_{int(__import__('time').time())}"
        )


def enhance_educational_response(message: str, base_response: str, user) -> str:
    """
    Enhance the AI response with personalized educational context
    """
    if not base_response or "apologize" in base_response.lower():
        return generate_educational_fallback(message)

    # Add personalized greeting for educational context
    greeting = f"Hi {user.full_name or 'there'}! Here's what I think:"
    enhanced = f"{greeting}\n\n{base_response}\n\n"

    # Add relevant study tips based on message content
    if any(keyword in message.lower() for keyword in ["help", "explain", "understand"]):
        enhanced += "💡 **Pro Tip**: Try connecting new concepts to real-life examples - it helps cement your understanding!\n\n"

    if any(keyword in message.lower() for keyword in ["difficult", "hard", "struggle", "confused"]):
        enhanced += "🎯 **Study Strategy**: Break complex topics into smaller, manageable steps. Small victories lead to big successes!\n\n"

    if any(keyword in message.lower() for keyword in ["assignment", "homework", "project"]):
        enhanced += "📚 **Resource**: Check out your EduAgent dashboard for assignment analysis and study recommendations!\n\n"

    enhanced += "Feel free to ask if you'd like me to explain anything differently! 😊"

    return enhanced


def generate_educational_fallback(message: str) -> str:
    """
    Generate a fallback response when knowledge base is not available
    """
    message_lower = message.lower()

    # Analyze message for educational keywords and provide targeted responses
    if any(keyword in message_lower for keyword in ["assignment", "homework", "task"]):
        return """I understand you're asking about your assignment! 📝

While I don't have access to your specific assignment materials right now, I can offer some general guidance:

**For Assignment Success:**
• Start by carefully reading all instructions
• Break complex problems into smaller, manageable steps
• Review similar examples from your course materials
• Check your work before submitting

**Getting Unstuck:**
• Try explaining the problem out loud
• Draw diagrams or make notes to visualize concepts
• Look for patterns in similar problems you've solved

What specific aspect of your assignment would you like help with? I'm here to guide you! 🎯"""

    elif any(keyword in message_lower for keyword in ["progress", "improvement", "study", "learn"]):
        return """Great question about your learning progress! 📈

Here are some proven strategies for effective studying:

**Track Your Progress:**
• Keep a study journal to note what you've learned
• Set small, achievable daily goals
• Review and practice regularly rather than cramming

**Improve Understanding:**
• Teach concepts to someone else (or even yourself out loud)
• Create mind maps to connect related ideas
• Practice applying concepts to new situations

**Stay Motivated:**
• Celebrate small victories along the way
• Connect your learning to your personal goals
• Find study methods that work best for your learning style

What specific area would you like to focus on improving? 🚀"""

    elif any(keyword in message_lower for keyword in ["concept", "understand", "explain"]):
        return """I'd love to help you understand this concept better! 🧠

**Effective Learning Strategies:**
• Start with the basic definition and key points
• Look for real-world examples that illustrate the concept
• Practice explaining it in your own words
• Connect it to things you already know

**When Concepts Feel Difficult:**
• Break them down into smaller parts
• Use visual aids like diagrams or charts
• Find multiple sources that explain it differently
• Practice with examples until it clicks

**Remember:** Understanding takes time, and it's okay to revisit concepts multiple times. Each time you encounter them, your understanding deepens!

Could you share more details about the specific concept you're working with? 🤔"""

    elif any(keyword in message_lower for keyword in ["grade", "score", "performance", "result"]):
        return """I understand you're concerned about your academic performance! 📊

**Improving Your Results:**
• Analyze where you lost points and focus on those areas
• Create a study schedule that covers all topics regularly
• Practice active recall instead of just re-reading notes
• Seek help early when you don't understand something

**Building Confidence:**
• Focus on progress, not just final grades
• Identify your strengths and build on them
• Learn from mistakes rather than dwelling on them
• Set realistic, achievable goals

**Study Strategies That Work:**
• Use practice tests and quizzes to identify weak spots
• Form study groups with classmates
• Visit office hours or tutoring sessions
• Review material within 24 hours of learning it

Remember, grades are just one measure of learning. Focus on understanding and growth! 💪"""

    else:
        return f"""Thank you for your question! 🤔

I understand you're asking: "{message}"

While I don't have access to your specific course materials right now, I'm here to help with your learning journey! Here are some ways I can assist:

**General Academic Support:**
• Study strategies and time management tips
• Help breaking down complex problems
• Learning techniques for different subjects
• Motivation and goal-setting advice

**Best Practices:**
• Regular review helps retention more than cramming
• Active engagement (like teaching others) improves understanding
• Connecting new concepts to prior knowledge strengthens learning
• Practice and repetition build confidence

**Next Steps:**
• Could you provide more specific details about what you're studying?
• What particular aspect would you like help with?
• Are there any specific challenges you're facing?

I'm here to support your learning success! 🎓"""
#!/usr/bin/env python3
"""
Database initialization script
Creates database tables and populates initial data
"""
import asyncio
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.models.user import User, Base as UserBase
from app.models.course import Course, Base as CourseBase
from app.models.assignment import Assignment, Base as AssignmentBase
from app.models.knowledge_point import KnowledgePoint, Base as KnowledgePointBase
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def create_tables():
    """Create all database tables"""
    try:
        # Import Base from the models to access metadata
        from app.models.user import Base

        async with engine.begin() as conn:
            # Create all tables using Base.metadata.create_all
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Database tables created successfully!")

        # Create the actual user you're trying to use
        AsyncSessionLocal = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with AsyncSessionLocal() as session:
            # Check if user exists
            result = await session.execute(text("SELECT email FROM users WHERE email = '3506718947@qq.com'"))
            existing = result.fetchone()

            if not existing:
                # Create the actual user from the 500 error
                hashed = get_password_hash("20030324l")
                await session.execute(text(f"""
                    INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser)
                    VALUES ('3506718947@qq.com', '{hashed}', 'User', 1, 0)
                """))
                await session.commit()
                print("✅ Created user: 3506718947@qq.com / 20030324l")
            else:
                print("✅ User 3506718947@qq.com already exists.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_tables())
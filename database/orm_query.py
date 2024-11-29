from sqlalchemy import select

from database.models import Question, Student
from sqlalchemy.ext.asyncio import AsyncSession
from .engine import connection


@connection
async def orm_add_student(session: AsyncSession, student_tg_id: int):
    obj = Student(
        student_tg_id=student_tg_id
    )

    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@connection
async def orm_add_question(session: AsyncSession, question_text: str, student_id: Student):
    obj = Question(
        question_text=question_text,
        student_id=student_id
    )
    session.add(obj)
    await session.commit()


@connection
async def orm_find_student(session: AsyncSession, student_tg_id: int):
    result = await session.execute(select(Student).filter_by(student_tg_id=student_tg_id))
    return result.scalar_one_or_none()


@connection
async def orm_delete_question():
    pass


@connection
async def orm_delete_student():
    pass

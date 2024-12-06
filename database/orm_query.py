from sqlalchemy import select, delete

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
async def orm_add_question(session: AsyncSession, question_text: (str, str,), image: str, student_id: Student):
    obj = Question(
        short_question=question_text[0],
        full_question=question_text[1],
        image=image,
        student_id=student_id
    )
    session.add(obj)
    await session.commit()


@connection
async def orm_find_student(session: AsyncSession, student_tg_id: int):
    result = await session.execute(select(Student).filter_by(student_tg_id=student_tg_id))
    return result.scalar_one_or_none()


@connection
async def orm_get_student_questions(session: AsyncSession, student_tg_id: int):
    query = (
    select(Question)
    .join(Student.questions)
    .where(Student.student_tg_id == student_tg_id)
)
    questions = await session.execute(query)
    return questions.scalars().all()


@connection
async def orm_delete_question(session: AsyncSession, question_id: int):
    query = delete(Question).where(Question.id == question_id)
    await session.execute(query)
    await session.commit()


@connection
async def orm_get_questions(session: AsyncSession):
    query = select(Question)
    questions = await session.execute(query)
    return questions.scalars().all()

# @connection
# async def orm_delete_student():
#     pass

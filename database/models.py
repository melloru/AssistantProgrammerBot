from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_tg_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    # Связь с вопросами
    questions: Mapped[list['Question']] = relationship("Question", back_populates="student", cascade='all')
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())


class Question(Base):
    __tablename__ = 'student_questions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('students.id'))
    question_text: Mapped[str] = mapped_column(String(150))
    moderation: Mapped[bool] = mapped_column(nullable=True)
    # Связь с пользователем
    student: Mapped[Student] = relationship("Student", back_populates="questions")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

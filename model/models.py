from typing import Optional
from pydantic import BaseModel
from enum import Enum

class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class TestType(str, Enum):
    multi = "multiple choice with 4 options and only 1 correct answer"
    flash = "flashcard where a definition or question is paired by 1 answer"

class QuizParam(BaseModel):
    url: str                # link
    amt_quest: int = 10     # number of questions
    difficulty: Difficulty = Difficulty.easy # difficulty
    test_type: TestType = TestType.flash # type of test

class QuizParamNew(BaseModel):
    title: str
    description: str
    transcript: Optional[str] = None
    amt_quest: int = 5
    difficulty: str
    test_type: str

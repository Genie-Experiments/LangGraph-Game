from typing import TypedDict, Annotated, Optional
import operator


class WordGameAgent(TypedDict):
    """
    State for the word guessing game.
    """
    words: list[str]
    max_number_of_questions: int
    current_question_index: int
    questions: Annotated[list[str], operator.add]
    answers: Annotated[list[str], operator.add]
    guess: Optional[str]
    asked_set: set[str]
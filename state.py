from typing import TypedDict, Literal, Optional, Annotated, List
import operator

class NumberGameAgent(TypedDict):
    min: int
    max: int
    guess: int
    next_step: Optional[Literal["start", "guessing", "done"]]

class WordGameAgent(TypedDict):
    words: list[str]
    max_number_of_questions: int
    current_question_index: int
    questions: Annotated[list[str], operator.add]
    answers: Annotated[list[str], operator.add]
    guess: Optional[str]
    asked_set: set[str]

class GameState(TypedDict):
    game_choice: Optional[Literal["number_game", "word_game", "retry"]]
    number_game_state: Optional[NumberGameAgent]
    word_game_state: Optional[WordGameAgent]
    word_game_count: int
    number_game_count: int

def create_initial_state() -> GameState:
    return {
        "game_choice": None,
        "number_game_state": None,
        "word_game_state": None,
        "word_game_count": 0,
        "number_game_count": 0
    }
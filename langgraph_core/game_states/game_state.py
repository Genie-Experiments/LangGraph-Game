from typing import TypedDict, Literal, Optional, Annotated, List, Union
import operator

from langgraph_core.game_states.number_game_state import NumberGameAgent
from langgraph_core.game_states.word_game_state import WordGameAgent


class GameState(TypedDict, total=False):
    """
    Main game state that includes both game types and tracking info.
    """
    game_choice: Optional[Literal["number_game", "word_game", "retry"]]
    number_game_state: Optional[NumberGameAgent]
    word_game_state: Optional[WordGameAgent]
    word_game_count: int
    number_game_count: int

    # API interaction fields
    __user_input__: str
    __messages__: list[str]


def create_initial_state() -> GameState:
    """
    Creates the initial state for a new game session.
    """
    return {
        "game_choice": None,
        "number_game_state": None,
        "word_game_state": None,
        "word_game_count": 0,
        "number_game_count": 0,
        "__messages__": [],
        "__user_input__": ""
    }
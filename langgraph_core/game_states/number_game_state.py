from typing import TypedDict, Literal, Optional


class NumberGameAgent(TypedDict):
    """
    State for the number guessing game.
    """
    min: int
    max: int
    guess: int
    next_step: Optional[Literal["start", "guessing", "guessed number"]]
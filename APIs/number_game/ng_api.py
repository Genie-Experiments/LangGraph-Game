from fastapi import APIRouter
from pydantic import BaseModel
from langgraph_core.graph.graph import app as langgraph_app
from langgraph_core.game_states.game_state import GameState, create_initial_state
from langgraph_core.nodes.number_game import guess_number
from langgraph_core.nodes.exit import exit_game

router = APIRouter()


class GameRequest(BaseModel):
    state: GameState
    user_input: str = ""


@router.post("/game/start")
def start_game(request: GameRequest):
    state = request.state
    user_input = request.user_input.strip()

    # Preserve game counts when starting a new game
    number_game_count = state.get("number_game_count", 0)
    word_game_count = state.get("word_game_count", 0)

    if user_input == "1":
        state["game_choice"] = "number_game"
        state["number_game_state"] = {
            "min": 1,
            "max": 50,
            "guess": 0,
            "next_step": "guessing"
        }
        state["__messages__"] = ["Think of a number between 1 and 50. Is your number greater than 25? (y/n)"]

        # Preserve game counts
        state["number_game_count"] = number_game_count
        state["word_game_count"] = word_game_count

        return state
    elif user_input == "2":
        state["game_choice"] = "word_game"
        state["word_game_state"] = {
            "words": ["apple", "kiwi", "desk", "chair", "car", "pen"],
            "max_number_of_questions": 5,
            "current_question_index": 0,
            "questions": [],
            "answers": [],
            "guess": None,
            "asked_set": set(),
            "word_list_shown": True  # Flag to indicate the word list was shown here
        }
        state["__messages__"] = [
            "Think of a word from this list:",
            "apple, kiwi, desk, chair, car, pen"
        ]

        # Preserve game counts
        state["number_game_count"] = number_game_count
        state["word_game_count"] = word_game_count

        return state
    else:
        try:
            state["__user_input__"] = user_input
            result = langgraph_app.invoke(state)

            # Preserve game counts in the returned state
            if "number_game_count" not in result and number_game_count > 0:
                result["number_game_count"] = number_game_count
            if "word_game_count" not in result and word_game_count > 0:
                result["word_game_count"] = word_game_count

            return result
        except Exception as e:
            state["game_choice"] = None
            state["__messages__"] = ["Please select a valid game option."]

            # Preserve game counts
            state["number_game_count"] = number_game_count
            state["word_game_count"] = word_game_count

            return state


@router.post("/game/number")
def number_game_step(request: GameRequest):
    state = request.state
    user_input = request.user_input.strip().lower()

    all_messages = state.get("__messages__", [])
    is_play_again_question = any("play again" in msg.lower() for msg in all_messages) or any(
        "play another game" in msg.lower() for msg in all_messages)

    if is_play_again_question:
        state["game_choice"] = "retry"
        state["__user_input__"] = user_input
        return langgraph_app.invoke(state)

    try:
        state["__user_input__"] = user_input
        if state.get("game_choice") != "number_game":
            state["game_choice"] = "number_game"

        updated_state = guess_number(state)

        return updated_state

    except Exception as e:
        print(f"Error in number_game_step: {str(e)}")

        state["__messages__"] = [
            "I'm having trouble with the number game at the moment.",
            "Please try again or select a different game."
        ]
        return state

@router.post("/game/exit")
def exit_game_endpoint(request: GameRequest):
    state = request.state

    result = exit_game(state)
    result["number_game_count"] = 0
    result["word_game_count"] = 0

    return result
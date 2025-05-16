from fastapi import APIRouter
from pydantic import BaseModel
from langgraph_core.graph.graph import app as langgraph_app
from langgraph_core.game_states.game_state import GameState, create_initial_state
from langgraph_core.nodes.word_game import ask_questions, guess_word
from langgraph_core.nodes.exit import exit_game

router = APIRouter()

class WordGameRequest(BaseModel):
    state: GameState
    user_input: str = ""

@router.post("/game/word")
def word_game_step(request: WordGameRequest):
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
        if state.get("game_choice") != "word_game":
            state["game_choice"] = "word_game"

        wg = state.get("word_game_state", {})

        if wg.get("current_question_index", 0) == 0 and not wg.get("questions", []):
            return ask_questions(state)

        is_responding_to_guess = any("My guess is" in msg for msg in all_messages) and any(
            "Was I correct?" in msg for msg in all_messages)
        if is_responding_to_guess:
            if user_input.lower() in ["yes", "y"]:
                state["__messages__"] = [
                    "Yay! I guessed right!",
                    "Would you like to play again?"
                ]
            else:
                state["__messages__"] = [
                    "I'm sorry I couldn't guess your word.",
                    "Would you like to play again?"
                ]
            return state

        current_q = wg.get("current_question_index", 1)
        max_q = wg.get("max_number_of_questions", 5)
        if current_q >= max_q:
            return guess_word(state)

        return ask_questions(state)

    except Exception as e:
        print(f"Error in word_game_step: {str(e)}")

        is_responding_to_guess = any("My guess is" in msg for msg in all_messages) and any(
            "Was I correct?" in msg for msg in all_messages)

        if is_responding_to_guess:
            if user_input.lower() in ["yes", "y"]:
                state["__messages__"] = [
                    "Yay! I guessed right!",
                    "Would you like to play again?"
                ]
            else:
                state["__messages__"] = [
                    "I'm sorry I couldn't guess your word.",
                    "Would you like to play again?"
                ]
            return state

        state["__messages__"] = [
            "I'm having trouble with the word game at the moment.",
            "Please try again or select a different game."
        ]
        return state


@router.post("/game/exit")
def exit_game_endpoint(request: WordGameRequest):
    state = request.state

    result = exit_game(state)
    result["number_game_count"] = 0
    result["word_game_count"] = 0

    return result
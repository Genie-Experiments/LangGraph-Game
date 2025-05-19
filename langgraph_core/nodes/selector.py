from langgraph_core.game_states.game_state import GameState
from langgraph_core.nodes.exit import exit_game


def game_selector(state: GameState) -> GameState:
    user_input = state.get("__user_input__", "").strip()
    messages = []

    if state.get("game_choice") == "word_game":
        if not state.get("__messages__"):
            messages.append("Continuing Word Game")
        else:
            return state
    elif state.get("game_choice") == "number_game":
        if not state.get("__messages__"):
            messages.append("Continuing Number Game")
        else:
            return state

    elif state.get("game_choice") == "retry":
        state["game_choice"] = None

        if user_input.lower() in ["yes", "y"]:
            messages.append("Returning to game selection. Please select a game.")
        else:
            messages.append("Thanks for playing! Goodbye!")
    elif user_input == "1":
        state.update({
            "game_choice": "number_game",
            "number_game_state": {
                "min": 1,
                "max": 50,
                "guess": 0,
                "next_step": "start"
            },
            "word_game_state": None
        })
        messages.append("Starting Number Guessing Game!")
    elif user_input == "2":
        words = ["apple", "kiwi", "desk", "chair", "car", "pen"]
        state.update({
            "game_choice": "word_game",
            "word_game_state": {
                "words": words,
                "max_number_of_questions": 5,
                "current_question_index": 0,
                "questions": [],
                "answers": [],
                "guess": None,
                "asked_set": set()
            },
            "number_game_state": None
        })
        messages.append("Starting Word Clue Guesser Game!")
    elif user_input == "":
        return exit_game(state)
    else:
        state["game_choice"] = None
        messages.append("Invalid choice. Please select a valid game option.")

    if messages:
        state["__messages__"] = messages
    return state
from langgraph_core.game_states.game_state import GameState


def choose_number(state: GameState) -> GameState:
    state["__messages__"] = ["Think of a number between 1 and 50. Press enter when ready."]

    if not state.get("number_game_state"):
        state["number_game_state"] = {
            "min": 1,
            "max": 50,
            "guess": 0,
            "next_step": "guessing"
        }
    else:
        state["number_game_state"]["next_step"] = "guessing"

    return state


def guess_number(state: GameState) -> GameState:
    ng = state.get("number_game_state", {})
    min_val, max_val = ng.get("min", 1), ng.get("max", 50)
    user_input = state.get("__user_input__", "").lower()
    messages = []

    all_messages = state.get("__messages__", [])
    is_play_again_question = any("play again" in msg.lower() for msg in all_messages) or any(
        "play another game" in msg.lower() for msg in all_messages)

    if is_play_again_question:
        if user_input in ["yes", "y"]:
            state["game_choice"] = "retry"
        else:
            state["game_choice"] = None

        state["number_game_state"] = None

        state["__messages__"] = [
            "Done guessing your number.",
            "Would you like to play another game? (yes/no)"
        ]
        return state

    if user_input in ["y", "n"]:
        mid = (min_val + max_val) // 2
        if user_input == "y":
            ng["min"] = mid + 1
        else:
            ng["max"] = mid

        state["number_game_state"] = ng

    min_val, max_val = ng.get("min", 1), ng.get("max", 50)
    if min_val >= max_val:
        state["number_game_count"] = state.get("number_game_count", 0) + 1

        messages.append(f"Your number is {min_val}!")
        messages.append("Would you like to play again?")
        ng["next_step"] = "guessed number"
    else:
        mid = (min_val + max_val) // 2
        messages.append(f"Is your number greater than {mid}? (y/n)")
        ng["next_step"] = "guessing"

    state["__messages__"] = messages
    return state
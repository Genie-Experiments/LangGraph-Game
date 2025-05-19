from langgraph_core.game_states.game_state import GameState


def exit_game(state: GameState) -> GameState:
    """
    Generate final game statistics and prepare exit message.
    """
    number_games = state.get("number_game_count", 0)
    word_games = state.get("word_game_count", 0)

    state["__messages__"] = [
        f"Thanks for playing!",
        f"You played {number_games} Number Guessing Games and {word_games} Word Clue Guesser Games in this session."
    ]

    return state
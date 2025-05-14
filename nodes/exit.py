from state import GameState

def exit_game(state: GameState) -> GameState:
    print(
        f"\nThanks for playing! You played {state.get('word_game_count', 0)} Word Clue Guesser Games and {state.get('number_game_count', 0)} Number Games."
    )
    state["game_choice"] = None
    return state

from state import GameState

def game_selector(state: GameState) -> GameState:
    print("\nGame Selector")
    choice = input("Enter '1' for number game or '2' for word game (or press Enter to quit): ").strip()

    if choice == "1":
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

    elif choice == "2":
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

    elif choice == "":
        state["game_choice"] = None

    else:
        print("Invalid choice. Defaulting to number game.")
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

    return state
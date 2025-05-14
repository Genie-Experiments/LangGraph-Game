from state import GameState

def choose_number(state: GameState) -> GameState:
    print("Think of a number between 1 and 50. I will try to guess it.")
    input("Press Enter when you're ready...")
    state["number_game_state"]["next_step"] = "guessing"
    return state

def guess_number(state: GameState) -> GameState:
    ng = state["number_game_state"]
    min_val, max_val = ng["min"], ng["max"]

    if min_val == max_val:
        print(f"Your number is {min_val}!")
        ng["next_step"] = "guessed number"
        return state

    mid = (min_val + max_val) // 2
    response = input(f"Is your number greater than {mid}? (y/n): ").strip().lower()

    if response == "y":
        ng["min"] = mid + 1
    elif response == "n":
        ng["max"] = mid
    else:
        print("Please enter 'y' or 'n'.")

    ng["next_step"] = "guessing"
    return state

def number_game_done(state: GameState) -> GameState:
    print("Done guessing your number.")
    state["number_game_count"] += 1
    retry = input("Would you like to play another game? (yes/no): ").strip().lower()
    state.update({
        "game_choice": "retry" if retry == "yes" else None,
        "number_game_state": None
    })
    return state

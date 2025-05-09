from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Optional, Annotated, List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import operator

from dotenv import load_dotenv, find_dotenv
import sys
sys.path.append('../..')
_ = load_dotenv(find_dotenv())
model = ChatGroq(model="llama3-8b-8192")

# --- Game State Classes ---
class NumberGameAgent(TypedDict):
    min: int
    max: int
    guess: int
    next_step: Optional[Literal["start", "guessing", "done"]]

class WordGameAgent(TypedDict):
    words: list[str]
    max_number_of_questions: int
    current_question_index: int
    questions: Annotated[list[str], operator.add]
    answers: Annotated[list[str], operator.add]
    guess: Optional[str]
    asked_set: set[str]

class GameState(TypedDict):
    game_choice: Optional[Literal["number_game", "word_game", "replay_word_game"]]
    number_game_state: Optional[NumberGameAgent]
    word_game_state: Optional[WordGameAgent]
    word_game_count: int
    number_game_count: int

def create_initial_state() -> GameState:
    return {
        "game_choice": None,
        "number_game_state": None,
        "word_game_state": None,
        "word_game_count": 0,
        "number_game_count": 0
    }

# ---- Custom Exit ----
def exit_game(state: GameState) -> GameState:
    print(
        f"\nThanks for playing! You played {state.get('word_game_count', 0)} Word Clue Guesser Games and {state.get('number_game_count', 0)} Number Games.")
    state["game_choice"] = None
    return state

# --- Entry Router ---
def entry_router(state: GameState) -> GameState:
    return state

# --- Game Selector ---
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
        return state

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
        return state

    elif choice == "":
        state["game_choice"] = None
        return state

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


# --- Word Game Restart Node ---
def word_game_restart(state: GameState) -> GameState:
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
    return state

# --- Number Game ---
def number_game_start(state: GameState) -> GameState:
    print("Think of a number between 1 and 50. I will try to guess it.")
    input("Press Enter when you're ready...")
    state["number_game_state"]["next_step"] = "guessing"
    return state

def number_game_guess(state: GameState) -> GameState:
    ng = state["number_game_state"]
    min_val, max_val = ng["min"], ng["max"]

    if min_val == max_val:
        print(f"Your number is {min_val}!")
        ng["next_step"] = "done"
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
    print("Done guessing your number. Returning to game selector...\n")
    state["number_game_count"] += 1
    state.update({"game_choice": None, "number_game_state": None})
    return state

# --- Word Clue Guesser Game Logic ---
def get_question(wg: WordGameAgent) -> str:
    prompt = PromptTemplate.from_template(
        """You are a word detective. The user has chosen a word from this list: {words}.
Ask a unique, descriptive yes/no/maybe question (not a guess) to help narrow it down.
Avoid repeating previous questions: {asked}.
This is question {question_number} of {max_q}.
Do NOT guess the word — just ask a useful question.
Do NOT return anything other than the question. 
Here is an example response: Is it a living thing?"""
    )

    formatted_prompt = prompt.format(
        words=", ".join(wg["words"]),
        question_number=wg["current_question_index"] + 1,
        max_q=wg["max_number_of_questions"],
        asked=", ".join(wg["asked_set"]) if wg["asked_set"] else "none"
    )

    question = model.invoke(formatted_prompt).content.strip()
    while question in wg["asked_set"]:
        question = model.invoke(formatted_prompt).content.strip()

    wg["asked_set"].add(question)
    return question

def word_game_ask_questions(state: GameState) -> GameState:
    wg = state["word_game_state"]
    if wg["current_question_index"] == 0:
        print("Think of a word from this list:")
        print(", ".join(wg["words"]))
        input("Press Enter when you're ready...")

    if wg["current_question_index"] < wg["max_number_of_questions"]:
        question = get_question(wg)
        print(f"Question {wg['current_question_index'] + 1}: {question}")
        user_answer = input("Your answer (yes/no/maybe): ").strip()

        wg["questions"].append(question)
        wg["answers"].append(user_answer)
        wg["current_question_index"] += 1

    return state

def word_game_guess_word(state: GameState) -> GameState:
    wg = state["word_game_state"]

    prompt = PromptTemplate.from_template(
        """You are a word detective. The possible words are: {words}.
Based on these question-answer pairs:
{qa}
Which word do you think the user picked? Make SURE to ONLY return ONE word from the list.
Do NOT include any other statements other than the guess word.
Here is an example response: Kiwi!"""
    )
    qa_pairs = "\n".join(
        f"Q{i+1}: {q} A: {a}" for i, (q, a) in enumerate(zip(wg["questions"], wg["answers"]))
    )
    guess = model.invoke(prompt.format(words=", ".join(wg["words"]), qa=qa_pairs)).content.strip()
    wg["guess"] = guess

    print(f"My guess is: **{guess}**")
    correct = input("Was I correct? (yes/no): ").strip().lower()

    state["word_game_count"] += 1

    if correct == "yes":
        print("Woohoo! I guessed it right!")
        state["game_choice"] = None
    else:
        print("Oops! I lost.")
        replay = input("Do you want to play the word game again? (yes/no): ").strip().lower()
        if replay == "yes":
            state["game_choice"] = "replay_word_game"
        else:
            state["game_choice"] = None

    return state

# --- LangGraph Setup ---
workflow = StateGraph(GameState)

# Nodes
workflow.add_node("entry_router", entry_router)
workflow.add_node("game_selector", game_selector)
workflow.add_node("word_game_restart", word_game_restart)
workflow.add_node("number_game_start", number_game_start)
workflow.add_node("number_game_guess", number_game_guess)
workflow.add_node("number_game_done", number_game_done)
workflow.add_node("word_game_ask_questions", word_game_ask_questions)
workflow.add_node("word_game_guess_word", word_game_guess_word)
workflow.add_node("exit_game", exit_game)


# Entry
workflow.set_entry_point("entry_router")

# Entry routing
workflow.add_conditional_edges(
    "entry_router",
    lambda state: state["game_choice"],
    {
        None: "game_selector",
        "replay_word_game": "word_game_restart"
    }
)

# Game selector routing
workflow.add_conditional_edges(
    "game_selector",
    lambda state: state["game_choice"],
    {
        "number_game": "number_game_start",
        "word_game": "word_game_ask_questions",
        None: "exit_game"
    }
)


workflow.add_edge("word_game_restart", "word_game_ask_questions")

workflow.add_conditional_edges(
    "number_game_start",
    lambda state: state["number_game_state"]["next_step"],
    {"guessing": "number_game_guess"}
)

workflow.add_conditional_edges(
    "number_game_guess",
    lambda state: state["number_game_state"]["next_step"],
    {
        "guessing": "number_game_guess",
        "done": "number_game_done"
    }
)

workflow.add_edge("number_game_done", "game_selector")

workflow.add_conditional_edges(
    "word_game_ask_questions",
    lambda state: (
        "word_game_ask_questions"
        if state["word_game_state"]["current_question_index"] < state["word_game_state"]["max_number_of_questions"]
        else "word_game_guess_word"
    ),
    {
        "word_game_ask_questions": "word_game_ask_questions",
        "word_game_guess_word": "word_game_guess_word"
    }
)

workflow.add_edge("word_game_guess_word", "entry_router")

# Compile and run
app = workflow.compile()

initial_state = create_initial_state()
result = app.invoke(initial_state)

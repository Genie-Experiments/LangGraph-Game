from langgraph_core.game_states.game_state import GameState
from langgraph_core.prompts.wg_prompts import get_question_prompt, guess_word_prompt
from utils.model import model

WORD_LIST = ["apple", "kiwi", "desk", "chair", "car", "pen"]
MAX_QUESTIONS = 5

def init_word_game_state(show_list: bool = False) -> dict:
    return {
        "words": WORD_LIST,
        "max_number_of_questions": MAX_QUESTIONS,
        "current_question_index": 0,
        "questions": [],
        "answers": [],
        "guess": None,
        "asked_set": set(),
        "word_list_shown": show_list
    }

def append_question_prompt(messages: list, question: str, index: int):
    messages.append(f"Question {index + 1}: {question}")
    messages.append("Your answer? (yes/no/maybe)")

def choose_word(state: GameState) -> GameState:
    state["__messages__"] = [
        "Think of a word from this list:",
        ", ".join(WORD_LIST)
    ]

    state["word_game_state"] = init_word_game_state(show_list=True)
    return state

def get_question(wg):
    formatted_prompt = get_question_prompt.format(
        words=", ".join(wg["words"]),
        question_number=wg["current_question_index"] + 1,
        max_q=wg["max_number_of_questions"],
        asked=", ".join(wg.get("asked_set", set())) if wg.get("asked_set") else "none"
    )

    try:
        question = model.invoke(formatted_prompt).content.strip()

        if "asked_set" not in wg:
            wg["asked_set"] = set()

        max_attempts = 3
        attempt = 0
        while question in wg["asked_set"] and attempt < max_attempts:
            question = model.invoke(formatted_prompt).content.strip()
            attempt += 1

        wg["asked_set"].add(question)
        return question

    except Exception as e:
        return "Is it something you use daily?"


def ask_questions(state: GameState) -> GameState:
    if "word_game_state" not in state:
        state["word_game_state"] = init_word_game_state()

    wg = state["word_game_state"]
    messages = []

    if wg["current_question_index"] < wg["max_number_of_questions"]:
        question = get_question(wg)
        wg["questions"].append(question)
        append_question_prompt(messages, question, wg["current_question_index"])
        wg["current_question_index"] += 1

    state["__messages__"] = messages
    return state


def guess_word(state: GameState) -> GameState:
    wg = state.get("word_game_state", {})
    user_input = state.get("__user_input__", "").strip().lower()

    # Record latest user answer if one is pending
    if user_input and len(wg["answers"]) < len(wg["questions"]):
        wg["answers"].append(user_input)

    try:
        qa_pairs = [
            f"Q{i + 1}: {q} A: {wg['answers'][i]}"
            for i, q in enumerate(wg["questions"])
            if i < len(wg["answers"])
        ]

        qa_text = "\n".join(qa_pairs)

        guess = model.invoke(guess_word_prompt.format(
            words=", ".join(wg["words"]),
            qa=qa_text
        )).content.strip()

        wg["guess"] = guess

    except Exception:
        wg["guess"] = WORD_LIST[0]

    state["word_game_count"] = state.get("word_game_count", 0) + 1
    state["__messages__"] = [
        f"My guess is: **{wg['guess']}**",
        "Was I correct? (yes/no)"
    ]

    if user_input in ["yes", "no"]:
        state["game_choice"] = "retry" if user_input == "yes" else None

    return state
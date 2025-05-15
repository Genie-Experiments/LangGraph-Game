from state import GameState
from langchain_core.prompts import PromptTemplate
from utils.model import model


def get_question(wg):
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
    if not state.get("word_game_state"):
        words = ["apple", "kiwi", "desk", "chair", "car", "pen"]
        state["word_game_state"] = {
            "words": words,
            "max_number_of_questions": 5,
            "current_question_index": 0,
            "questions": [],
            "answers": [],
            "guess": None,
            "asked_set": set(),
            "word_list_shown": False
        }

    wg = state["word_game_state"]
    messages = []

    if wg["current_question_index"] < wg["max_number_of_questions"]:
        try:
            question = get_question(wg)
            wg.setdefault("questions", []).append(question)
            messages.append(f"Question {wg['current_question_index'] + 1}: {question}")
            messages.append("Your answer? (yes/no/maybe)")
            wg["current_question_index"] += 1
        except Exception as e:
            messages.append("I'm having trouble thinking of a question.")
            messages.append("Your answer? (yes/no/maybe)")
            wg["current_question_index"] += 1

    state["__messages__"] = messages
    return state

def guess_word(state: GameState) -> GameState:
    wg = state.get("word_game_state", {})
    user_input = state.get("__user_input__", "").strip().lower()

    if user_input and wg.get("questions") and len(wg.get("questions", [])) > len(wg.get("answers", [])):
        wg.setdefault("answers", []).append(user_input)

    try:
        prompt = PromptTemplate.from_template(
            """You are a word detective. The possible words are: {words}.
Based on these question-answer pairs:
{qa}
Which word do you think the user picked? Make SURE to ONLY return ONE word from the list.
Do NOT include any other statements other than the guess word.
Here is an example response: Kiwi!"""
        )

        qa_pairs = []
        for i, q in enumerate(wg.get("questions", [])):
            if i < len(wg.get("answers", [])):
                qa_pairs.append(f"Q{i + 1}: {q} A: {wg['answers'][i]}")

        qa_text = "\n".join(qa_pairs)

        guess = model.invoke(prompt.format(
            words=", ".join(wg.get("words", [])),
            qa=qa_text
        )).content.strip()

        wg["guess"] = guess
    except Exception as e:
        wg["guess"] = wg.get("words", ["apple"])[0]

    state["word_game_count"] = state.get("word_game_count", 0) + 1

    state["__messages__"] = [
        f"My guess is: **{wg.get('guess')}**",
        "Was I correct? (yes/no)"
    ]

    if user_input in ["yes", "no"]:
        state["game_choice"] = "retry" if user_input == "yes" else None

    return state
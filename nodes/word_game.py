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
        asked=", ".join(wg["asked_set"]) if wg["asked_set"] else "none"
    )

    question = model.invoke(formatted_prompt).content.strip()
    while question in wg["asked_set"]:
        question = model.invoke(formatted_prompt).content.strip()

    wg["asked_set"].add(question)
    return question

def ask_questions(state: GameState) -> GameState:
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

def guess_word(state: GameState) -> GameState:
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
    else:
        print("Oops! I lost.")

    retry = input("Would you like to play another game? (yes/no): ").strip().lower()
    state["game_choice"] = "retry" if retry == "yes" else None
    return state

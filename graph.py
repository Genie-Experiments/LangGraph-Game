from langgraph.graph import StateGraph, END
from state import GameState
from nodes.selector import game_selector
from nodes.number_game import choose_number, guess_number, number_game_done
from nodes.word_game import ask_questions, guess_word
from nodes.exit import exit_game

workflow = StateGraph(GameState)

workflow.add_node("game_selector", game_selector)
workflow.add_node("choose_number", choose_number)
workflow.add_node("guess_number", guess_number)
workflow.add_node("number_game_done", number_game_done)
workflow.add_node("ask_questions", ask_questions)
workflow.add_node("guess_word", guess_word)
workflow.add_node("exit_game", exit_game)

workflow.set_entry_point("game_selector")

workflow.add_conditional_edges(
    "game_selector",
    lambda state: state["game_choice"],
    {
        "number_game": "choose_number",
        "word_game": "ask_questions",
        "retry": "game_selector",
        None: "exit_game"
    }
)


workflow.add_conditional_edges(
    "choose_number",
    lambda state: state["number_game_state"]["next_step"],
    {"guessing": "guess_number"}
)

workflow.add_conditional_edges(
    "guess_number",
    lambda state: state["number_game_state"]["next_step"],
    {
        "guessing": "guess_number",
        "guessed number": "number_game_done"
    }
)

workflow.add_edge("number_game_done", "game_selector")

workflow.add_conditional_edges(
    "ask_questions",
    lambda state: (
        "ask_questions"
        if state["word_game_state"]["current_question_index"] < state["word_game_state"]["max_number_of_questions"]
        else "guess_word"
    ),
    {
        "ask_questions": "ask_questions",
        "guess_word": "guess_word"
    }
)

workflow.add_edge("guess_word", "game_selector")

app = workflow.compile()

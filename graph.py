from langgraph.graph import StateGraph, END
from state import GameState
from nodes.selector import game_selector
from nodes.number_game import choose_number, guess_number
from nodes.word_game import ask_questions, guess_word

workflow = StateGraph(GameState)


workflow.add_node("game_selector", game_selector)
workflow.add_node("choose_number", choose_number)
workflow.add_node("guess_number", guess_number)
workflow.add_node("ask_questions", ask_questions)
workflow.add_node("guess_word", guess_word)

workflow.set_entry_point("game_selector")

workflow.add_conditional_edges(
    "game_selector",
    lambda state: state.get("game_choice"),
    {
        "number_game": "choose_number",
        "word_game": "ask_questions",
        "retry": "game_selector",
        None: END
    }
)

workflow.add_conditional_edges(
    "choose_number",
    lambda state: state.get("number_game_state", {}).get("next_step"),
    {"guessing": "guess_number"}
)

workflow.add_conditional_edges(
    "guess_number",
    lambda state: state.get("number_game_state", {}).get("next_step"),
    {
        "guessing": "guess_number"
    }
)

# Direct edge from guess_number to game_selector
workflow.add_edge("guess_number", "game_selector")


def word_game_next(state):
    word_state = state.get("word_game_state", {})
    current_q = word_state.get("current_question_index", 0)
    max_q = word_state.get("max_number_of_questions", 5)

    if current_q < max_q:
        return "ask_questions"
    else:
        return "guess_word"


workflow.add_conditional_edges(
    "ask_questions",
    word_game_next,
    {
        "ask_questions": "ask_questions",
        "guess_word": "guess_word"
    }
)

workflow.add_edge("guess_word", "game_selector")


app = workflow.compile()

mermaid_text = app.get_graph().draw_mermaid()
with open("graph.mmd", "w") as f:
    f.write(mermaid_text)
print("Mermaid text saved as graph.mmd")
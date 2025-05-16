from langgraph.graph import StateGraph, END
from langgraph_core.game_states.game_state import GameState
from langgraph_core.nodes.selector import game_selector
from langgraph_core.nodes.number_game import choose_number, guess_number
from langgraph_core.nodes.word_game import choose_word, ask_questions, guess_word

workflow = StateGraph(GameState)

# Add nodes
workflow.add_node("game_selector", game_selector)
workflow.add_node("choose_number", choose_number)
workflow.add_node("guess_number", guess_number)
workflow.add_node("choose_word", choose_word)
workflow.add_node("ask_questions", ask_questions)
workflow.add_node("guess_word", guess_word)

# Set entry point
workflow.set_entry_point("game_selector")

# Selector routes
workflow.add_conditional_edges(
    "game_selector",
    lambda state: state.get("game_choice"),
    {
        "number_game": "choose_number",
        "word_game": "choose_word",
        "retry": "game_selector",
        None: END
    }
)

# Number game logic
workflow.add_conditional_edges(
    "choose_number",
    lambda state: state.get("number_game_state", {}).get("next_step"),
    {"Number chosen": "guess_number"}
)

workflow.add_conditional_edges(
    "guess_number",
    lambda state: state.get("number_game_state", {}).get("next_step"),
    {"guessing": "guess_number"}
)

workflow.add_edge("guess_number", "game_selector")


# choose_word → ask_questions
workflow.add_conditional_edges(
    "choose_word",
    lambda state: state.get("word_game_state", {}).get("next_step"),
    {"Word chosen": "ask_questions"}
)

# ask_questions → ask_questions OR guess_word
workflow.add_conditional_edges(
    "ask_questions",
    lambda state: (
        "ask_questions" if state.get("word_game_state", {}).get("current_question_index", 0) <
                          state.get("word_game_state", {}).get("max_number_of_questions", 5)
        else "guess_word"
    ),
    {
        "asking questions": "ask_questions",
        "guess_word": "guess_word"
    }
)

# guess_word → game_selector
workflow.add_edge("guess_word", "game_selector")

# Compile
app = workflow.compile()

# Optional: Mermaid diagram output
try:
    mermaid_text = app.get_graph().draw_mermaid()
    with open("graph.mmd", "w") as f:
        f.write(mermaid_text)
    print("Mermaid text saved as graph.mmd")
except Exception as e:
    print(f"Could not generate mermaid diagram: {e}")

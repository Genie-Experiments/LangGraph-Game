from graph import app
from state import create_initial_state

if __name__ == "__main__":
    initial_state = create_initial_state()
    result = app.invoke(initial_state)

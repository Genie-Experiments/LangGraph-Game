import streamlit as st
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

import sys, os

sys.path.append(os.getenv("PYTHONPATH", "."))
from langgraph_core.game_states.game_state import GameState, create_initial_state

# Set page configuration with a dark theme
st.set_page_config(
    page_title="LangGraph Games",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# API URL - change this if your FastAPI is running on a different port/host
API_URL = "http://localhost:8000"

# Custom CSS with improved visibility
st.markdown("""
<style>
    /* Main elements */
    .main-title {
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
        color: #ffffff;
    }
    .game-title {
        font-size: 28px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #ffffff;
    }

    /* Card styling */
    .game-card {
        background-color: #2e3856;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        color: #ffffff;
        border: 1px solid #3e4a7a;
    }

    /* Message containers */
    .message-container {
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 8px;
        margin-top: 5px;
        font-size: 16px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .system-message {
        background-color: #313c63;
        color: #ffffff;
        border-left: 4px solid #4c8bf5;
    }
    .user-message {
        background-color: #27344d;
        text-align: right;
        color: #ffffff;
        border-right: 4px solid #4ecdc4;
    }

    /* Status elements */
    .spinner {
        text-align: center;
        margin: 20px 0;
    }
    .error-message {
        background-color: #472a2a;
        color: #ff6b6b;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #a83232;
    }

    /* Text formatting */
    .bold-text {
        font-weight: bold;
        color: #4ecdc4;
    }

    /* Footer */
    .footer {
        margin-top: 30px;
        text-align: center;
        color: #7a88b8;
        font-size: 14px;
    }

    /* Streamlit element overrides */
    .stButton > button {
        background-color: #4c8bf5;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #3a78e7;
    }
    .stTextInput > div > div > input {
        background-color: #27344d;
        color: white;
        border: 1px solid #3e4a7a;
    }

    /* Dropdown styling */
    .stSelectbox > div > div {
        background-color: #27344d;
        color: white;
        border: 1px solid #3e4a7a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'state' not in st.session_state:
    st.session_state.state = create_initial_state()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'game_type' not in st.session_state:
    st.session_state.game_type = None
if 'error' not in st.session_state:
    st.session_state.error = None
if 'retries' not in st.session_state:
    st.session_state.retries = 0
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0


# Function to make API requests with error handling and retries
def make_api_request(endpoint, state, user_input="", max_retries=3):
    st.session_state.error = None
    retries = 0

    while retries < max_retries:
        try:
            payload = {
                "state": state,
                "user_input": user_input
            }

            # Make request
            response = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            # Retry with backoff
            retries += 1
            st.session_state.retries = retries

            if retries < max_retries:
                # Wait with exponential backoff
                time.sleep(0.5 * (2 ** retries))
            else:
                # Max retries reached
                error_msg = f"API Error after {max_retries} attempts: {str(e)}"
                st.session_state.error = error_msg
                return None


# Function to display messages
def display_messages():
    for msg in st.session_state.messages:
        if msg['type'] == 'system':
            st.markdown(f'<div class="message-container system-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:  # user message
            st.markdown(f'<div class="message-container user-message">{msg["content"]}</div>', unsafe_allow_html=True)


# Helper function to navigate between pages
def navigate_to(page):
    st.session_state.page = page


# Add the submit_response function
def submit_response(user_response):
    # Add user message to chat
    st.session_state.messages.append({"type": "user", "content": user_response})

    # Determine API endpoint
    endpoint = None
    if st.session_state.game_type == "number_game":
        endpoint = "/game/number"
    elif st.session_state.game_type == "word_game":
        endpoint = "/game/word"

    if endpoint:
        with st.spinner("Processing..."):
            # Store current game counts before API call
            number_count = st.session_state.state.get('number_game_count', 0)
            word_count = st.session_state.state.get('word_game_count', 0)

            result = make_api_request(endpoint, st.session_state.state, user_response)
            if result:
                # Update state with API response
                st.session_state.state = result

                # Check if API incremented the game counts
                new_number_count = result.get('number_game_count', 0)
                new_word_count = result.get('word_game_count', 0)

                # If game counts were not preserved correctly, keep the previous values
                if new_number_count == 0 and number_count > 0:
                    st.session_state.state['number_game_count'] = number_count
                if new_word_count == 0 and word_count > 0:
                    st.session_state.state['word_game_count'] = word_count

                # Add system messages
                for msg in result.get("__messages__", []):
                    st.session_state.messages.append({"type": "system", "content": msg})

                # Check for specific game state transitions
                if result.get("game_choice") is None:
                    # Game is over, return to home
                    navigate_to('home')
                elif "Would you like to play another game?" in " ".join(
                        result.get("__messages__", [])) or "Would you like to play again?" in " ".join(
                    result.get("__messages__", [])):
                    # Stay in the current screen to get the yes/no response
                    pass
                elif "Returning to game selection" in " ".join(result.get("__messages__", [])):
                    # Explicitly return to home screen
                    navigate_to('home')
            else:
                # Keep gameplay page open even if there's an error
                pass

        # Increment the key to reset the input field on next render
        st.session_state.input_key += 1

        # Force page refresh to show new messages
        st.rerun()


# Main title for all pages
st.markdown('<div class="main-title">🎮 LangGraph Games</div>', unsafe_allow_html=True)

# Display error if present
if st.session_state.error:
    st.markdown(f'<div class="error-message">{st.session_state.error}</div>', unsafe_allow_html=True)
    if st.button("Clear Error"):
        st.session_state.error = None
        st.rerun()

# HOME PAGE
if st.session_state.page == 'home':
    st.markdown('<div class="game-title">Select a Game</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.markdown("### 🔢 Number Guessing Game")
        st.markdown("Think of a number and I'll guess it!")
        if st.button("Play Number Game"):
            st.session_state.game_type = "number_game"
            st.session_state.messages = []  # Clear messages

            # THE FIX: Create a new state but preserve game counts
            new_state = create_initial_state()
            if 'state' in st.session_state:
                new_state['number_game_count'] = st.session_state.state.get('number_game_count', 0)
                new_state['word_game_count'] = st.session_state.state.get('word_game_count', 0)
            st.session_state.state = new_state

            # Make API call to start the game
            with st.spinner("Starting game..."):
                result = make_api_request("/game/start", st.session_state.state, "1")
                if result:
                    # Preserve game counts when updating state
                    number_count = st.session_state.state.get('number_game_count', 0)
                    word_count = st.session_state.state.get('word_game_count', 0)

                    st.session_state.state = result

                    # Make sure the counts are preserved in the new state
                    if 'number_game_count' not in result or result.get('number_game_count', 0) == 0:
                        st.session_state.state['number_game_count'] = number_count
                    if 'word_game_count' not in result or result.get('word_game_count', 0) == 0:
                        st.session_state.state['word_game_count'] = word_count

                    for msg in result.get("__messages__", []):
                        st.session_state.messages.append({"type": "system", "content": msg})
                    navigate_to('gameplay')
                    st.rerun()
                else:
                    st.error("Failed to start game. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="game-card">', unsafe_allow_html=True)
        st.markdown("### 🔤 Word Clue Guesser")
        st.markdown("I'll try to guess your word by asking questions!")
        if st.button("Play Word Game"):
            st.session_state.game_type = "word_game"
            st.session_state.messages = []  # Clear messages

            # THE FIX: Create a new state but preserve game counts
            new_state = create_initial_state()
            if 'state' in st.session_state:
                new_state['number_game_count'] = st.session_state.state.get('number_game_count', 0)
                new_state['word_game_count'] = st.session_state.state.get('word_game_count', 0)
            st.session_state.state = new_state

            # Make API call to start the game
            with st.spinner("Starting game..."):
                result = make_api_request("/game/start", st.session_state.state, "2")
                if result:
                    # Preserve game counts when updating state
                    number_count = st.session_state.state.get('number_game_count', 0)
                    word_count = st.session_state.state.get('word_game_count', 0)

                    st.session_state.state = result

                    # Make sure the counts are preserved in the new state
                    if 'number_game_count' not in result or result.get('number_game_count', 0) == 0:
                        st.session_state.state['number_game_count'] = number_count
                    if 'word_game_count' not in result or result.get('word_game_count', 0) == 0:
                        st.session_state.state['word_game_count'] = word_count

                    for msg in result.get("__messages__", []):
                        st.session_state.messages.append({"type": "system", "content": msg})
                    navigate_to('gameplay')
                    st.rerun()
                else:
                    st.error("Failed to start game. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Add End Game button to show statistics
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("End Game", key="end_game"):
        # Get statistics from state or from API
        state = st.session_state.state
        if state:
            # Make API call to get stats
            with st.spinner("Getting game stats..."):
                result = make_api_request("/game/exit", state)
                if result:
                    st.session_state.state = result
                    st.session_state.messages = []
                    for msg in result.get("__messages__", []):
                        st.session_state.messages.append({"type": "system", "content": msg})
                    navigate_to('exit')
                else:
                    # Create default stats message if API fails
                    number_games = state.get("number_game_count", 0)
                    word_games = state.get("word_game_count", 0)
                    st.session_state.messages = [{
                        "type": "system",
                        "content": f"Thanks for playing! You played {number_games} Number Guessing Games and {word_games} Word Clue Guesser Games in this session."
                    }]

                    # Reset counts in the state after showing stats
                    state["number_game_count"] = 0
                    state["word_game_count"] = 0
                    st.session_state.state = state

                    navigate_to('exit')

# GAMEPLAY PAGE
elif st.session_state.page == 'gameplay':
    game_display_name = st.session_state.game_type.replace("_", " ").title() if st.session_state.game_type else "Game"
    st.markdown(f'<div class="game-title">Playing {game_display_name}</div>', unsafe_allow_html=True)

    # Display chat history
    display_messages()

    # Get all message contents for easier analysis
    all_message_content = " ".join([m.get('content', '') for m in st.session_state.messages])
    last_message = st.session_state.messages[-1]['content'] if st.session_state.messages else ""

    # Check if we're at the "play again" prompt or if the number was just guessed
    is_play_again = ("Would you like to play again?" in all_message_content or
                     "Would you like to play another game?" in all_message_content)
    is_number_guessed = "Your number is" in last_message and st.session_state.game_type == "number_game"

    if is_play_again or is_number_guessed:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Play Again", key="play_again_btn"):
                # THE FIX: Store the current game counts before navigating away
                number_count = st.session_state.state.get('number_game_count', 0)
                word_count = st.session_state.state.get('word_game_count', 0)

                # Navigate to home screen
                navigate_to('home')

                # Create a new clean state but preserve the game counts
                new_state = create_initial_state()
                new_state['number_game_count'] = number_count
                new_state['word_game_count'] = word_count
                st.session_state.state = new_state

                st.rerun()
        with col2:
            if st.button("Exit Game", key="exit_in_gameplay"):
                navigate_to('home')
                st.rerun()
    # Special case for word selection phase
    elif ("Think of a word from this list" in all_message_content and
          "Question" not in all_message_content):
        # Word selection phase - only show the button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("I've Selected a Word", key="ready_button"):
            submit_response("")  # Empty response to start the game
    else:
        # Check if this is the number game and requires yes/no response
        if st.session_state.game_type == "number_game" and any(phrase in last_message for phrase in
                                                               ["Is your number greater than",
                                                                "Is your number higher than",
                                                                "Is your number less than",
                                                                "Is your number lower than",
                                                                "Is your number equal to"]) and "(y/n)" in last_message:
            # Use a dropdown for yes/no in the number game
            yes_no_options = ["Select response", "y", "n"]
            user_selection = st.selectbox("Select your response:",
                                          yes_no_options,
                                          index=0,
                                          key=f"yes_no_select_{st.session_state.input_key}")

            submit = st.button("Submit")
            if submit and user_selection != "Select response":
                submit_response(user_selection)
            elif submit and user_selection == "Select response":
                st.warning("Please select an option before submitting.")
        # Check if this is the word game and requires yes/no/maybe response
        elif st.session_state.game_type == "word_game" and ("Your answer? (yes/no/maybe)" in last_message or
                                                            "(yes/no/maybe)" in last_message):
            # Use a dropdown for yes/no/maybe in the word game
            options = ["Select response", "yes", "no", "maybe"]
            user_selection = st.selectbox("Select your response:",
                                          options,
                                          index=0,
                                          key=f"word_game_select_{st.session_state.input_key}")

            submit = st.button("Submit")
            if submit and user_selection != "Select response":
                submit_response(user_selection)
            elif submit and user_selection == "Select response":
                st.warning("Please select an option before submitting.")
        else:
            # All other cases - show normal input
            user_input = st.text_input("Your response:", key=f"user_input_{st.session_state.input_key}")
            submit = st.button("Submit")
            if submit or (user_input and len(user_input.strip()) > 0):
                submit_response(user_input.strip())

    # Add "Back to Home" button (only show if not already on the play again screen)
    if not is_play_again and not is_number_guessed:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Exit Game", key="exit_game_button"):
            navigate_to('home')
            st.rerun()

# GAME OVER PAGE
elif st.session_state.page == 'game_over':
    st.markdown('<div class="game-title">Game Complete</div>', unsafe_allow_html=True)

    # Display final game state
    display_messages()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Play Again"):
            # Go back to home to select a new game
            navigate_to('home')

    with col2:
        if st.button("Exit Game"):
            # Go directly to home without showing stats
            navigate_to('home')
            st.rerun()

# EXIT PAGE
elif st.session_state.page == 'exit':
    st.markdown('<div class="game-title">Thanks for Playing!</div>', unsafe_allow_html=True)

    # Display exit message
    display_messages()

    if st.button("Back to Home"):
        # Make sure counts are reset when returning to home
        if 'state' in st.session_state:
            st.session_state.state["number_game_count"] = 0
            st.session_state.state["word_game_count"] = 0
        navigate_to('home')

# Footer
st.markdown('<div class="footer">Built with Streamlit and LangGraph</div>', unsafe_allow_html=True)
import streamlit as st
import time
from src.state import GameState
from src.agent import game_agent # Our compiled LangGraph agent

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Choose Your Own Adventure",
    page_icon="📖",
    layout="centered"
)

# --- CSS for Styling (Optional but Recommended for Aesthetics) ---
st.markdown("""
    <style>
    .main-header {
        font-size: 3em;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 0.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .subheader {
        font-size: 1.5em;
        color: #555;
        text-align: center;
        margin-bottom: 1em;
    }
    .story-text {
        font-family: 'Georgia', serif;
        font-size: 1.1em;
        line-height: 1.6;
        color: #333;
        background-color: #f9f9f9;
        border-left: 5px solid #4CAF50;
        padding: 1em 1.5em;
        margin: 1.5em 0;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .player-stats {
        font-size: 1em;
        color: #666;
        background-color: #e6ffe6;
        padding: 0.8em 1.2em;
        border-radius: 5px;
        margin-bottom: 1em;
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
    }
    .player-stat-item {
        margin: 0.5em 1em;
    }
    .stButton>button {
        width: 100%;
        margin-top: 0.7em;
        padding: 0.8em;
        border-radius: 12px;
        font-size: 1.1em;
        font-weight: bold;
        background-color: #66bb6a; /* A bit darker green for buttons */
        color: white;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #4CAF50;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .game-over-message {
        font-size: 2em;
        color: #D32F2F; /* Red for game over */
        text-align: center;
        margin-top: 2em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


# --- Game Logic Functions ---

def init_game():
    """Initializes or resets the game state."""
    st.session_state.game_state = GameState()
    # Set a dummy input for the initial run to trigger the 'describe_scene_step' path in the agent
    st.session_state.game_state.user_input = "__INITIAL_RUN__"

    # Run the agent once to get the initial scene description
    try:
        # Pass a higher recursion limit for debugging (optional but recommended)
        initial_state_output = game_agent.invoke(st.session_state.game_state, config={"recursion_limit": 50})
        if not isinstance(initial_state_output, GameState):
            st.session_state.game_state = GameState(**initial_state_output)
            print(f"DEBUG: init_game - Converted initial_state_output from AddableValuesDict to GameState.")
        else:
            st.session_state.game_state = initial_state_output # It was already GameState

        # IMPORTANT: Clear the dummy input after the initial run has completed
        # This prevents it from being processed as an actual choice in subsequent turns.
        st.session_state.game_state.user_input = ""
    except Exception as e:
        st.error(f"Error initializing game: {e}")
        st.session_state.game_state.current_story_text = "An error occurred during game initialization. Please try refreshing."
        st.session_state.game_state.available_choices = []




def make_choice(choice_text: str):
    """Callback function when a choice button is clicked."""

    # This handles cases where state was left as AddableValuesDict from previous script run
    if not isinstance(st.session_state.game_state, GameState):
        try:
            st.session_state.game_state = GameState(**st.session_state.game_state)
            print(f"DEBUG: make_choice - Converted incoming session state from AddableValuesDict to GameState.")
        except Exception as e:
            st.error(f"FATAL ERROR in make_choice: Could not convert game state object. Details: {e}")
            st.stop() # Stop the app if the state is unrecoverable
  

    if st.session_state.game_state.game_over:
        return # Do nothing if game is over

    st.session_state.game_state.user_input = choice_text # Set the user_input for the agent

    # Run the agent with the updated state
    try:
        with st.spinner("Thinking..."): # Show a spinner while LLM processes
            # Pass a higher recursion limit for debugging (optional but recommended)
            new_state = game_agent.invoke(st.session_state.game_state, config={"recursion_limit": 50})
            if not isinstance(new_state, GameState):
                st.session_state.game_state = GameState(**new_state)
                print(f"DEBUG: make_choice - Converted invoked new_state from AddableValuesDict to GameState.")
            else:
                st.session_state.game_state = new_state # It was already GameState
   
    except Exception as e:
        st.error(f"Error processing choice: {e}")
        st.session_state.game_state.current_story_text += "\n\nAn error occurred while processing your choice."
        st.session_state.game_state.available_choices = ["Restart"] # Offer restart

    # Check for game over condition
    if st.session_state.game_state.player.health <= 0:
        st.session_state.game_state.game_over = True
        st.session_state.game_state.current_story_text += "\n\n**Your health has dropped to zero! The adventure ends here.**"
        st.session_state.game_state.available_choices = ["Restart Game"]


# --- Main Streamlit App Layout ---

st.markdown("<h1 class='main-header'>The Whispering Wilds</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='subheader'>A Choose Your Own Adventure</h2>", unsafe_allow_html=True)

# Initialize game state if not already present
if "game_state" not in st.session_state:
    init_game()

current_game_state = st.session_state.game_state

# LangGraph might return AddableValuesDict even when using Pydantic state.
# We need to ensure we're always working with our GameState Pydantic object.
if not isinstance(current_game_state, GameState):
    try:
        # Attempt to re-instantiate GameState from the dict-like object
        current_game_state = GameState(**current_game_state)
        st.session_state.game_state = current_game_state # Update session state with the correct type
        print(f"DEBUG: Converted state from AddableValuesDict to GameState successfully.")
    except Exception as e:
        st.error(f"FATAL ERROR: Could not convert game state object. Details: {e}")
        st.stop()

# --- Display Player Stats ---
st.markdown("<div class='player-stats'>", unsafe_allow_html=True)
st.markdown(f"<span class='player-stat-item'>❤️ Health: **{current_game_state.player.health}**</span>", unsafe_allow_html=True)
st.markdown(f"<span class='player-stat-item'>🎒 Inventory: **{', '.join(current_game_state.player.inventory) if current_game_state.player.inventory else 'Empty'}**</span>", unsafe_allow_html=True)
st.markdown(f"<span class='player-stat-item'>📍 Location: **{current_game_state.player.current_location_name}**</span>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Display Story Text ---
st.markdown("<div class='story-text'>", unsafe_allow_html=True)
st.markdown(current_game_state.current_story_text) # Use markdown to render potential bold/italics from LLM
st.markdown("</div>", unsafe_allow_html=True)

# --- Display Choices or Game Over Message ---
if current_game_state.game_over:
    st.markdown("<p class='game-over-message'>GAME OVER</p>", unsafe_allow_html=True)
    if st.button("Restart Game", key="restart_game_button"):
        init_game() # Re-initialize the game
        st.rerun() # Rerun the app to show the new initial state
else:
    st.markdown("---")
    st.subheader("What do you do next?")
    
    # Create buttons for each choice
    # Using st.columns to put buttons side-by-side if there are many choices
    # cols = st.columns(len(current_game_state.available_choices)) # This can be too many columns
    
    # Better to just stack them or use a fixed number of columns for better layout control
    # For now, let's just stack them for simplicity and robust responsiveness.
    for i, choice in enumerate(current_game_state.available_choices):
        # Use a unique key for each button to prevent Streamlit warnings
        if st.button(choice, key=f"choice_button_{i}", use_container_width=True):
            make_choice(choice)
            st.rerun() # Rerun the app to process the choice and update the display

# Optional: Add a debug section to view the full state
# with st.expander("Debug Game State"):
#    st.json(st.session_state.game_state.model_dump_json())
import os
from dotenv import load_dotenv

# Langchain/LangGraph specific imports
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

# Local imports from our project structure
from src.state import GameState 
from src.prompts import ( 
    SYSTEM_PROMPT,
    SCENE_PROMPT,
    CHOICE_INTERPRETATION_PROMPT,
    INVALID_CHOICE_PROMPT
)

# --- Configuration ---
load_dotenv() # Load environment variables from .env file

# --- Google Gemini API Key ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please set it.")

# Initialize the Gemini Model
# We'll use a specific model here, e.g., 'gemini-pro' or 'gemini-1.5-flash'
# 'gemini-1.5-flash' is often a good balance of speed and capability for this kind of application.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, google_api_key=GEMINI_API_KEY)

# --- LangGraph Agent Definition ---

# Let's define the nodes of our graph. Each node is a function that takes the current GameState
# and returns an updated GameState

def describe_scene(state: GameState) -> GameState:
    """
    Generates the narrative description for the current scene based on the GameState.
    """
    print(f"--- Node: describe_scene ({state.player.current_location_id}) ---")

    # Construct the prompt for Gemini to describe the scene
    prompt = SCENE_PROMPT.format(
        location_name=state.player.current_location_name,
        current_story_text=state.current_story_text, # Pass previous text for context if needed
        player_inventory=", ".join(state.player.inventory) if state.player.inventory else "nothing",
        player_health=state.player.health
    )

    # Use Gemini to generate the scene description
    try:
        response_content = llm.invoke([
            HumanMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]).content

        # The response should ideally include choices structured in a specific way,
        # but for now, let's assume it's just raw text that we'll parse later or
        # generate choices separately.
        # For a true "Choose Your Own Adventure", the choices are often fixed per scene.
        # We'll adjust this to explicitly generate choices.
        # For simplicity in this first pass, let's have Gemini describe the scene,
        # and then a separate function will generate/handle choices.

        # For now, let's assume the narrative is just the direct response.
        # We will refine this to extract choices dynamically or load them from data.
        narrative_description = response_content

        # Update the state with the new story text.
        # We append to ensure a history, or overwrite if we only want the current scene.
        # Let's append for now to build a story history.
        new_story_text = state.current_story_text + "\n\n" + narrative_description

        # IMPORTANT: For this first iteration, we'll need to manually define choices
        # or load them from a data structure associated with `current_location_id`.
        # Gemini is good for narrative, but for explicit CYOA choices, we often need structure.
        # Let's mock some choices based on location for now.
        if state.player.current_location_id == "start_forest":
            choices = ["Go deeper into the forest", "Look for a path to the village", "Examine the strange glowing mushroom"]
        elif state.player.current_location_id == "deep_forest":
             choices = ["Follow the sound of running water", "Try to climb a tall tree", "Rest and recover health"]
        else: # Default choices for unhandled locations
            choices = ["Continue forward", "Turn back"]

        return GameState(
            player=state.player,
            current_story_text=new_story_text,
            available_choices=choices # Pass the choices to the frontend
        )

    except Exception as e:
        print(f"Error in describe_scene: {e}")
        return GameState(
            player=state.player,
            current_story_text=state.current_story_text + "\n\nAn error occurred while generating the scene: " + str(e),
            available_choices=["Restart"]
        )


def handle_user_choice(state: GameState) -> GameState:
    """
    Processes the user's choice and determines the next location or story branch.
    This node primarily sets up the next_location_id based on the choice.
    """
    print(f"\n===== HANDLE_USER_CHOICE NODE START =====")
    print(f"HANDLE_USER_CHOICE: User chose: '{state.user_input}'")
    print(f"HANDLE_USER_CHOICE: Current health BEFORE turn processing: {state.player.health}") # for debugging


    user_choice = state.user_input.strip().lower()
    next_location_id = state.player.current_location_id # Default to current, or an error state

    # This is a critical point for decision logic.
    # For a real game, you'd have a mapping from current_location_id + choice -> next_location_id
    # You could load this from a JSON file (e.g., in data/story_config.json)
    # For now, let's use simple if/elif for our example locations.

    response_text = ""
    is_valid_choice = False

    HEALTH_DECREASE_PER_TURN = 10 # You can adjust this value
    state.player.health -= HEALTH_DECREASE_PER_TURN
    response_text += f"\n\n_Your journey drains your energy. (-{HEALTH_DECREASE_PER_TURN} health. Current health: {state.player.health})_"
    
    # Check if the user's choice is one of the available choices
    if user_choice in [c.lower() for c in state.available_choices]:
        is_valid_choice = True
        if state.player.current_location_id == "start_forest":
            if "go deeper into the forest" in user_choice:
                next_location_id = "deep_forest"
                response_text = "\nYou venture deeper into the tangled woods."
            elif "look for a path to the village" in user_choice:
                next_location_id = "village_outskirts"
                response_text = "\nYou search for a path and soon find a faint trail."
            elif "examine the strange glowing mushroom" in user_choice:
                response_text = "\nYou cautiously approach the mushroom. It pulses with a soft, ethereal light. Touching it gives you a strange tingling sensation, and you feel slightly more robust (+5 health)."
                state.player.health += 5 # Example of state change based on choice
                # Stay in the same location for a minor interaction
                next_location_id = "start_forest"
        elif state.player.current_location_id == "deep_forest":
            if "follow the sound of running water" in user_choice:
                next_location_id = "forest_stream"
                response_text = "\nYou follow the gentle gurgle of a hidden stream."
            elif "try to climb a tall tree" in user_choice:
                response_text = "\nAfter a strenuous climb, you reach the canopy. You see vast stretches of forest, but no clear path. You spot a distant ruined tower."
                next_location_id = "deep_forest" # Stay, but maybe add a 'tower_seen' flag
                state.plot_flags["tower_seen"] = True
            elif "rest and recover health" in user_choice:
                response_text = "\nYou find a hidden clearing and rest for a while, regaining some strength. (+10 health)"
                state.player.health += 10
                next_location_id = "deep_forest" # Stay
        # ... add more location-specific logic here

        else: # For locations not yet explicitly handled for choices
            response_text = "\nYou proceed, but the path ahead is still uncertain."
            next_location_id = "unknown_path" # A placeholder for generic progression
    else:
        # User entered an invalid choice, or free-form text
        # Use Gemini to generate a response explaining the invalid choice
        print("Invalid choice detected. Using Gemini for response.")
        prompt = INVALID_CHOICE_PROMPT.format(
            user_input=state.user_input,
            available_choices=", ".join(state.available_choices)
        )
        try:
            gemini_response = llm.invoke([
                HumanMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]).content
            response_text = "\n" + gemini_response
            next_location_id = state.player.current_location_id # Stay in current location
        except Exception as e:
            response_text = f"\nInvalid choice. Please choose from the available options. Error: {e}"
            next_location_id = state.player.current_location_id # Stay in current location

    # --- The health cap and game over check also come only once, at the end of the function ---
    if state.player.health < 0:
        state.player.health = 0
    if state.player.health <= 0:
        state.game_over = True
        response_text += "\n\n**Your health has dropped to zero! The adventure ends here.**"
        state.available_choices = ["Restart Game"]
        print("HANDLE_USER_CHOICE: Game Over triggered!")

        
    # Update the player's location ID based on the choice logic
    state.player.current_location_id = next_location_id
    state.current_story_text += response_text # Append choice outcome

    # Clear previous choices as new ones will be generated by describe_scene
    state.available_choices = []
    state.user_input = "" # Clear user input after processing

    return state


def update_location_name(state: GameState) -> GameState:
    """
    Updates the human-readable location name based on the current_location_id.
    This could be expanded to load from a data file.
    """
    print(f"--- Node: update_location_name ({state.player.current_location_id}) ---")
    location_names = {
        "start_forest": "Mysterious Whispering Forest",
        "deep_forest": "Dense Tangled Woods",
        "village_outskirts": "Dusty Village Outskirts",
        "forest_stream": "Glistening Forest Stream",
        "unknown_path": "An Uncharted Path",
    }
    state.player.current_location_name = location_names.get(state.player.current_location_id, "An Unknown Place")
    return state


# --- NEW: Game Start Node ---
def game_start_node(state: GameState) -> GameState:
    """
    The actual entry point node for the graph.
    It simply passes the state along, allowing the router to then decide the flow.
    """
    print(f"\n===== GAME_START_NODE EXECUTION =====")
    print(f"GAME_START_NODE: Initial state received by entry point.")
    return state # No state modification needed here, just a pass-through

def route_game_step(state: GameState) -> str:
    """
    Routes the graph based on whether user input needs processing
    or a new scene needs to be described.
    """
    # We use "__INITIAL_RUN__" as a specific marker for the very first scene generation.
    if state.user_input and state.user_input != "__INITIAL_RUN__":
        return "process_choice"
    else:
        return "describe_scene_step"

# --- Define the LangGraph StateGraph ---
def create_game_agent():
    workflow = StateGraph(GameState)

    # Add all your node functions to the workflow
    workflow.add_node("game_start_node", game_start_node)
    workflow.add_node("update_location_name", update_location_name)
    workflow.add_node("describe_scene", describe_scene)
    workflow.add_node("handle_user_choice", handle_user_choice)

    # 1. Set the ACTUAL entry point to the 'game_start_node'
    workflow.set_entry_point("game_start_node")

    # 2. Define conditional edges from the router
    # The 'route_game_step' function's return value ("process_choice" or "describe_scene_step")
    # determines the next node.
    workflow.add_conditional_edges(
        "game_start_node", # The node FROM which the conditional edge originates
        route_game_step,   # The function that decides the next step (returns a string)
        {
            "process_choice": "handle_user_choice",      # Map string to target node name
            "describe_scene_step": "update_location_name", # Map string to target node name
        },
    )

    # 3. Define transitions for processing a choice:
    # After handling a user choice, the game needs to generate the new scene.
    workflow.add_edge("handle_user_choice", "update_location_name")

    # 4. Define transitions for scene description:
    # After updating the location name, generate the scene description.
    workflow.add_edge("update_location_name", "describe_scene")

    # 5. CRITICAL: Make `describe_scene` the terminal node for each invocation.
    # This tells LangGraph to stop after generating and updating the scene.
    workflow.add_edge("describe_scene", END)

    return workflow.compile()

# Instantiate the agent globally (at the bottom of src/agent.py)
game_agent = create_game_agent()
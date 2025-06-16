# 📖 Choose Your Own Adventure: An AI-Powered Interactive Story

Welcome to the **Choose Your Own Adventure** game! This project leverages the power of Large Language Models (LLMs) with LangChain and LangGraph to create a dynamic, interactive storytelling experience where your choices directly shape the narrative and your character's fate. Built with Streamlit, it provides a user-friendly interface to embark on endless adventures.

## ✨ Features

* **Interactive Storytelling:** The narrative adapts in real-time based on your decisions.
* **Dynamic Choices:** LLM-generated choices keep the story fresh and unpredictable.
* **Persistent Character State:** Your character's health, inventory, and location are tracked throughout the game.
* **Health System:** Your character's health decreases with each turn, leading to a "Game Over" if it drops to zero. Specific choices can also affect health.
* **Plot Flags:** Internal mechanisms to remember past events, influencing future interactions (e.g., finding a secret, examining an item).
* **Modular Agent Design:** Utilizes LangGraph for a robust and traceable state machine, managing the flow of the game logic.
* **User-Friendly Interface:** A clean and engaging web UI built with Streamlit.

## 🚀 How to Play

1.  **Start Your Journey:** Click "Start New Game" to begin your adventure in a mysterious forest.
2.  **Read the Story:** The AI will describe your current scene and situation.
3.  **Make a Choice:** Select one of the available actions presented at the bottom of the screen.
4.  **Observe Consequences:** Your health will decrease with each turn. Your choice will lead to a new part of the story, potentially changing your location, inventory, or health.
5.  **Survive!** Keep an eye on your health. If it drops to 0, your adventure ends, and you'll be prompted to start a new game.

## 🛠️ Getting Started

Follow these steps to get a copy of the project up and running on your local machine.

### Prerequisites

* **Python 3.9+** (Recommended)
* **Google API Key** for Gemini (or another LLM provider like OpenAI, if configured).
    * You can get a Google API Key from the Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME # Replace YOUR_REPO_NAME with your actual repository name
    ```
    (If you've just pushed, you'll skip cloning and just `cd` into your project directory.)

2.  **Create a Python Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install the required dependencies:**
    Create a `requirements.txt` file in your project's root directory with the following content:
    ```
    streamlit
    langchain
    langchain-google-genai
    langgraph
    langchain-core
    pydantic==1.10.13 # Pinning for compatibility
    ```
    Then, install them:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up your Google API Key:**
    Create a `.env` file in the root of your project directory and add your API key:
    ```
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
    ```
    **IMPORTANT:** Make sure this `.env` file is listed in your `.gitignore` to prevent it from being accidentally committed to your public repository!

## 🚀 Running the Application

Once everything is set up, run the Streamlit application:

```bash
streamlit run app.py

Project Structure
.
├── app.py                     # Main Streamlit application and UI logic
├── src/
│   ├── __init__.py            # Makes 'src' a Python package
│   ├── agent.py               # Defines the LangGraph agent and its nodes (game logic)
│   ├── state.py               # Pydantic models for GameState and PlayerState
│   └── prompts.py             # Stores system prompts and LLM instructions
├── .gitignore                 # Specifies files/folders to be ignored by Git
├── requirements.txt           # Lists Python dependencies
└── README.md                  # This file

🎮 Game Mechanics Details
Player State: Managed by src/state.py, tracking health, inventory, current_location_id, etc.
Game Flow (src/agent.py):
game_start_node: The initial entry point.
route_game_step: A router function that decides if the agent needs to process user input or describe a new scene.
handle_user_choice: Processes player input, applies health changes, updates location, and checks for game over. This is where per-turn health decrease happens.
update_location_name: Uses an LLM to generate a descriptive name for the new location.
describe_scene: Generates the story text and available choices for the current scene using an LLM.
The graph intelligently transitions between these nodes and terminates at END after each complete "turn" (choice processed, new scene generated).
Health System:
Starts at 100 health.
Decreases by 10 points after every choice (every turn).
Can be affected by specific narrative events (e.g., gaining health from an item).
Game ends if health drops to 0 or below.
💡 Future Improvements
More Complex Inventory: Implement item usage, combining items, or persistent effects.
Combat System: Introduce turn-based combat with enemies, damage calculations, and different attack options.
Dialogue System: NPCs with branching dialogue trees.
Saving/Loading Game: Persist game state across sessions.
Enhanced Plot Flags: More intricate branching storylines and consequence tracking.
Error Handling: More graceful handling of LLM generation failures.
More Diverse Locations/Encounters: Expand the world with more unique places and events.
Sound/Music: Add audio elements for immersion.
🤝 Contributing
Feel free to fork the repository, open issues, or submit pull requests with improvements!

📄 License
This project is licensed under the MIT License - see the LICENSE file for details (you would create a LICENSE file in your root directory if you want a formal license, e.g., by copying from choosealicense.com).

import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import random

# --- CONFIGURATION & SETUP ---
st.set_page_config(page_title="Chef AI-XORA", page_icon="🍳", layout="centered")
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

FILE_NAME = "chat_memory.json"

# Custom CSS for styling the app
st.markdown("""
<style>

/* --- USE SYSTEM THEME --- */
:root {
    color-scheme: light dark;
}

/* --- CHAT BUBBLES --- */
[data-testid="stChatMessageContent"] {
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 15px;
    line-height: 1.5;
    max-width: 85%;
}

/* USER MESSAGE (works in both modes) */
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #fde68a, #fcd34d);
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

/* AI MESSAGE (auto adapts) */
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0,0,0,0.1);
    border-bottom-left-radius: 4px;
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
    [data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] {
        background: rgba(30, 30, 30, 0.9);
        border: 1px solid rgba(255,255,255,0.1);
    }
}

/* --- INPUT BOX --- */
.stChatInput input {
    border-radius: 12px !important;
}

/* --- BUTTON --- */
.stButton button {
    border-radius: 10px;
    padding: 10px;
    border: none;
    background: linear-gradient(135deg, #f97316, #ea580c);
    color: white;
    font-weight: 500;
}

.stButton button:hover {
    background: linear-gradient(135deg, #ea580c, #c2410c);
}

/* --- REMOVE FOOTER --- */
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC ---
def load_data():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []

def save_data(chat_history):
    new_memory = []
    for message in chat_history:
        new_memory.append({
            "role": message.role,
            "parts": [{"text": message.parts[0].text}]
        })
    with open(FILE_NAME, "w") as f:
        json.dump(new_memory, f, indent=4)

# Initialize Gemini
if api_key:
    genai.configure(api_key=api_key)
    instructions = """You are Chef AI-Xora — a smart, practical kitchen assistant.

You speak like a real person: natural, slightly warm, and thoughtful.
Avoid sounding robotic, but also avoid being too brief.
Your responses should feel complete and useful — not one-liners.

Aim for balanced detail:
• Give enough explanation to be helpful
• Keep it easy to read
• Do not over-explain

Core Behavior:

1. Remember the User
If the user shares lifestyle, health goals, diet, allergies, or preferences — remember and apply them naturally in future responses.
Do not repeat or re-ask unless needed.

2. Rescue First
If an ingredient is about to expire, prioritize it.
Build the meal around it naturally.

3. Think Before Suggesting
Use available ingredients first.
Avoid unnecessary additions.

4. Budget Awareness
If a shopping list is needed and budget is unknown, ask briefly.
When given:
• Keep suggestions realistic
• Avoid waste
• Prefer flexible ingredients

5. Smart Shopping
Only include missing items.
Keep quantities practical and budget-aware.

6. Special Case: Missing Ingredients / No Inventory (IMPORTANT)

If the user:
• says they don’t have ingredients
• OR says they are missing items for a recipe
• OR says “I want to make this but I don’t have things”

Then you MUST:

Step 1:
Ask (in a natural, short way):
• What is your budget (Rs)?
• How many people are you cooking for?

Do NOT generate a shopping list yet.

Step 2:
After the user answers:
• Generate a complete shopping list based on:
  - the recipe
  - number of people
  - budget

• Adjust quantities to fit the budget
• Prioritize essential ingredients first
• Suggest cheaper alternatives if needed

7. Recipe Output Format (IMPORTANT)

Whenever suggesting a dish, include a clean Markdown table:

| Ingredients | Time | Calories |
|------------|------|----------|
| ingredient list | total time | estimated calories per serving |

Keep it neat and readable.

8. Natural Flow
Write like a person helping in the kitchen.
Not rigid, not robotic.

9. Keep It Useful
Avoid extremely short answers.
Avoid long unnecessary explanations.

10. Reduce Waste
Encourage reuse, leftovers, and smart ingredient usage.

11. Ask Only When Needed
Ask short, natural follow-ups if required.

12. Stay in Role
If the user asks something unrelated:
Reply briefly and politely, then return focus to kitchen help.

Most importantly:
Be human, be practical, and help the user cook smarter within their means."""

    model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite", system_instruction=instructions)
else:
    st.error("API Key not found. Please check your .env file.")

# --- SESSION STATE MANAGEMENT ---
if "messages" not in st.session_state:
    saved_history = load_data()
    # Convert JSON format to Streamlit-friendly format
    st.session_state.messages = [{"role": m["role"], "content": m["parts"][0]["text"]} for m in saved_history]

if "chat_session" not in st.session_state:
    # Convert JSON history back to Gemini format for the chat object
    gemini_history = []
    for m in st.session_state.messages:
        gemini_history.append({"role": m["role"], "parts": [m["content"]]})
    st.session_state.chat_session = model.start_chat(history=gemini_history)



# --- SIDEBAR UI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1830/1830839.png", width=100)
    st.title("Chef AI-XORA")
    st.markdown("**Strategic Kitchen Assistant**")
    st.divider()

    st.info("I help you reduce waste, stay on budget, and cook delicious meals with what's already in your fridge.")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)
        st.rerun()

    st.divider()
    st.caption("Developed & Deployed by:")
    st.markdown("**Dua Noor**")

# --- MAIN CHAT INTERFACE ---
st.title("🍳 Chef AI-XORA")
st.caption("Your personalized culinary co-pilot.")

# Display Chat History
for message in st.session_state.messages:
    role_class = "user-bubble" if message["role"] == "user" else "assistant-bubble"
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("What's in your fridge?"):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking of a recipe..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                full_response = response.text

                st.markdown(full_response)

                # Add to State and Save
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                save_data(st.session_state.chat_session.history)

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- DYNAMIC TIP---
tips = [
    "Tell Xora your budget & number of servings for custom shopping lists.",
    "Tell Xora about your allergies or food waste goals for better suggestions."
]
# --- FOOTER ---
st.markdown("---")
st.caption("Tip: " + random.choice(tips))
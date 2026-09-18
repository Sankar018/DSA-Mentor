import logging

from flask import Flask, request, jsonify, send_from_directory
from google import genai
from dotenv import load_dotenv
import os


# ============================================================
# LOGGER CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("DSA-Mentor")


# ============================================================
# GEMINI API CONFIGURATION
# ============================================================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

logger.info("Gemini client initialized successfully.")


# ============================================================
# CHAT HISTORY
# ============================================================

previous_interaction_id = None

# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are a Data Structure and Algorithm instructor.

Your job is to teach Data Structures and Algorithms in a
simple, clear, and beginner-friendly way.

IMPORTANT RULES:

1. Only answer questions related to Data Structures and Algorithms.

2. If the user asks something unrelated to DSA, politely reply:
"Please ask Data Structure and Algorithm related questions only."

3. Do not use unnecessary headings such as "Key Points",
"Important Points", "Conclusion", etc.

4. Do not use excessive bullet points.

5. Do not use excessive bold text, emojis, or decorative formatting.

6. Give answers in a natural conversational teaching style.

7. Start with a simple definition or direct answer.

8. If an example is useful, give one simple example.

9. If code is required, provide a small and easy-to-understand code example.

10. Explain difficult concepts step by step using simple language.

11. Do not make the answer unnecessarily long.

12. For algorithm questions, explain:
- What the algorithm does
- How it works
- A simple example
- Time complexity, when relevant

13. For data structure questions, explain:
- What it is
- How it works
- A simple example
- Time complexity, when relevant

14. Use plain text formatting whenever possible.

15. Answer like a friendly teacher explaining the concept to a beginner.
"""


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__, static_folder=".", static_url_path="")


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():

    logger.info("Home page requested.")

    return send_from_directory(".", "index.html")


# ============================================================
# CHAT API
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    global previous_interaction_id

    logger.info("Received POST request: /api/chat")

    body = request.get_json(silent=True) or {}

    user_message = (body.get("message") or "").strip()

    if not user_message:

        logger.warning("Received empty message.")

        return jsonify({
            "error": "Empty message"
        }), 400

    logger.info("User message received.")

    try:

        logger.info("Sending request to Gemini...")

        # ----------------------------------------------------
        # FIRST MESSAGE
        # ----------------------------------------------------

        if previous_interaction_id is None:

            logger.info("Starting a new conversation.")

            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                system_instruction=SYSTEM_INSTRUCTION,
                input=user_message,
            )

        # ----------------------------------------------------
        # FOLLOW-UP MESSAGE
        # ----------------------------------------------------

        else:

            logger.info(
                "Continuing previous interaction."
            )

            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                system_instruction=SYSTEM_INSTRUCTION,
                previous_interaction_id=previous_interaction_id,
                input=user_message,
            )

        # ----------------------------------------------------
        # SAVE NEW INTERACTION ID
        # ----------------------------------------------------

        previous_interaction_id = interaction.id

        logger.info(
            "Interaction ID updated successfully."
        )

        # ----------------------------------------------------
        # GET GEMINI RESPONSE
        # ----------------------------------------------------

        reply = interaction.output_text

        logger.info(
            "Gemini response received successfully."
        )

        logger.info(
            "Response length: %d characters",
            len(reply)
        )

    except Exception as e:

        logger.exception(
            "Error while communicating with Gemini."
        )

        return jsonify({
            "reply": "[Backend error] Something went wrong."
        }), 500

    logger.info(
        "Sending response to frontend."
    )

    return jsonify({
        "reply": reply
    })


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    logger.info(
        "Starting DSA Mentor backend..."
    )

    logger.info(
        "Server running at http://127.0.0.1:5000"
    )

    app.run(
        debug=True,
        port=5000
    )


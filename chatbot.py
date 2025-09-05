import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai

# Load env variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")  # Set on Render dashboard or .env

if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not set")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()
origins = [
    "http://localhost:5500",
    "https://your-vercel-frontend-url",
    "https://your-render-backend-url"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompt tailored to H2flow Controls website content
h2flow_prompt = """
You are a professional AI assistant representing H2flow Controls, a global company specializing in flow measurement solutions, industrial control, pool & spa equipment, and machine protection devices.

INSTRUCTIONS:
- ONLY ANSWER QUESTIONS RELATED TO H2flow Controls PRODUCTS, SERVICES, INDUSTRIES, AND COMPANY INFORMATION.
- Keep responses VERY SHORT and CLEAR (3 sentences max).
- Do NOT answer questions unrelated to H2flow. If asked unrelated questions, respond with: "Please ask questions only about H2flow Controls products or services."
- Use professional language suitable for technical and industrial audiences.
- Maximum response length: 300 characters.
"""

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Start Gemini chat session with system prompt as initial context
        chat = model.start_chat(history=[{"role": "user", "parts": [h2flow_prompt]}])
        while True:
            message = await websocket.receive_text()
            try:
                response = chat.send_message(message)
                await websocket.send_text(response.text)
            except Exception as e:
                logging.error(f"Error in Gemini chat: {e}")
                await websocket.send_text("Sorry, an error occurred while processing your message.")
    except WebSocketDisconnect:
        logging.info("Client disconnected")
    except Exception as e:
        logging.error(f"Unexpected exception: {e}")
    finally:
        await websocket.close()

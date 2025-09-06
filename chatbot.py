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
    "h2flow.vercel.app",
    "https://h2flow.onrender.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompt tailored to H2flow Controls website content
h2flow_prompt = """
You are an expert technical sales assistant for H2Flow Controls. When a user asks about solutions, always tailor your answers by presenting only the most relevant product names and technical descriptions from the portfolio below, matching the user's stated application, industry, or technical requirement. Be concise, accurate, and ready to clarify features or specs for any listed product.

Product and Solution Portfolio (present only what fits the user's context):

    LevelSmart Wireless Autofill: Wireless water level automation for pools, preventing overfill and manual checking.

    ProcessDefender™: Condition monitoring device for motor-driven machinery—alerts operators about abnormal operation to prevent downtime and damage.

    FlowVis®: Mechanical flow meter (≥98.1% accuracy, 1.5"-8" pipe, GPM/LPM/m³/h, NSF 50 Level 1) for pools, spas, or any water system demanding precise, reliable flow verification.

    FlowVis® Digital: Digital upgrade for any FlowVis model; adds remote indication, alarm integration, and turnover rate display.

    FaraMag FM750: Electromagnetic (mag) flow meter for water and process fluids, with ±0.25% accuracy—ideal for varied fluid handling needs.

    AcuFlow™: High-accuracy (≥98.1%) mechanical flow meter for clean, grey, or potable water applications, 1.5”-8” compatible—upgradable to digital.

    AcuFlow™ Digital: Add-on for AcuFlow meters to enable digital monitoring, alarms, and integration with external control/indicator systems.

    AC Drive Solutions: Variable speed/frequency drives and soft starters designed for energy savings, optimized for pool, spa, and industrial motors.

How to respond:

    Review the user's question for industry keywords (e.g., pool, spa, industrial, OEM, water level, flow measurement, process control).

    Name and recommend only the most relevant H2Flow Controls products (from the above list) for their industry or need.

    Provide 1-2 precise technical features for each product you mention.

    Offer to explain more technical details or send specifications if the user asks.

Core proficiencies:

    Control (drive/soft start solutions), Protect (preventative monitoring devices), Measure (flow/level meters, digital upgrades for process insight).

Industries served:

    Pool & Spa (energy efficiency, anti-entrapment, water level automation)

    Industrial/OEM (ruggedized flow & level metering, motor control, preventative maintenance)

Highlight that H2Flow Controls is a global provider, headquartered in Toledo, Ohio, with solutions distributed in over 60 countries.
"""

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
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
    # Remove the finally block that calls `await websocket.close()`

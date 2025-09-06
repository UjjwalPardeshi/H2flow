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
Prompt:
You are an expert sales and support assistant for H2Flow Controls. Your job is to present the full catalog of H2Flow Controls’ solutions, using technical product names and short, precise descriptions tailored to pool & spa, industrial, and OEM customers. Always be ready to clarify technical terms on request.

Product and Solution Portfolio:

    LevelSmart Wireless Autofill: Intelligent wireless system to automate swimming pool water level, eliminating manual filling and risk of overfill.

    ProcessDefender™: Predictive protection device for motor-driven machinery; detects abnormal operating conditions and alerts operators, preventing damage and costly downtime.

    FlowVis®: High-accuracy (≥98.1%) mechanical flow meter for pool and spa piping (1.5”-8”, d50-d200), NSF 50 Level 1 certified, supports GPM, LPM, m³/h, with universal mounting orientation.

    FlowVis® Digital: Digital upgrade for FlowVis meters with NSF 50 certification; enables remote flow/turnover monitoring, flow alarms, and equipment integration.

    FaraMag FM750: Advanced electromagnetic flow meter for diverse fluid applications, with ±0.25% accuracy, delivering economic, high-precision flow solutions.

    AcuFlow™: Mechanical flow meter for clean, grey, and potable water, with ≥98.1% accuracy, for 1.5”-8” pipes, and field-upgradeable to digital.

    AcuFlow™ Digital: Digital companion for AcuFlow meters, offering remote monitoring, flow alarms, and external control integration.

    AC Drive Solutions: Variable speed drives and soft start devices optimized for pool, spa, and industrial segments, improving system efficiency and reducing energy cost.

Core Proficiencies:

    Control: Variable speed/soft start for optimized motor control.

    Protect: Monitoring devices for preventative maintenance and machinery/process reliability.

    Measure: Flow measurement products for various pipe sizes, liquids, and industrial needs.

Industries Served:

    Pool & Spa (energy-efficient flow, anti-entrapment, remote level control)

    Industrial/OEM (rugged flow/level/motor control solutions for demanding applications)

Mention H2Flow Controls’ global presence with partners in 60+ countries and highlight their new Toledo, Ohio headquarters and manufacturing facility.
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

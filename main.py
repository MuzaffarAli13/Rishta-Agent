import streamlit as st
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from whatsapp_sender import send_whatsapp_message
import asyncio
from data import get_user_data_from_sheet

load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# Rishty Wali Agent
rishty_agent = Agent(
    name="Rishty Wali Auntie",
    instructions="""
     You are a warm, friendly, and slightly nosy 'Rishtay Wali Auntie' named Rishtay Wali Auntie whose job is to find suitable matches for people based on their preferences.
     
     You have access to two tools:
     1. `get_user_data_from_sheet`: Fetches profiles from a public Google Sheet and filters them based on the given age and finds profiles of the opposite gender.
     2. `send_whatsapp_message`: Sends WhatsApp messages via the UltraMSG API.
     
     When a user sends a prompt:
     - First, check the message for a phone number, preferred age, and gender.
     - If all are provided, find matching profiles from the Google Sheet using `get_user_data_from_sheet`.
     - Share the matching profile’s details by sending a WhatsApp message to the provided number using `send_whatsapp_message`, but ONLY if the user explicitly asks you to send it.
     
     Always reply in English with a kind, playful, and slightly nosy tone like a caring rishtay wali auntie.
     
     If anyone asks your name, reply: "Rishty Wali Auntie".
     
     Keep your responses short, clear, and to the point.
     Do not respond to any topic other than finding matches and sending WhatsApp messages.
     
     If multiple matches are found, list them clearly with numbering or bullet points in your response. Only send match details via WhatsApp if the user asks for it.
     """,
    model=model,
    tools=[get_user_data_from_sheet, send_whatsapp_message]
)

st.image("agent.png", width=650)

# Streamlit App
st.title("📱 Rishty Wali Auntie 🤭")

st.markdown("""
### Salam beta! 👋  
Main Rishty Wali Auntie hoon — agar rishta karwana hai to **apna naam, age, gender, aur WhatsApp number** zaroor batana.  
Bina inn cheezon ke Auntie kuch nahi karegi 😄
""")

    

prompt = st.text_area("📩 Prompt:")


if "history" not in st.session_state:
   histroy =  st.session_state.history = []

st.markdown(
    """
    <a href="https://forms.gle/Arpz3zRRx7RAXeWW9" target="_blank">
        <button style='padding: 10px 13px; font-size: 16px; background-color: #f63366; color: white; border: none; border-radius: 5px; cursor: pointer; margin-bottom: 12px;'>
            👵 Add Rishta
        </button>
    </a>
    """,
    unsafe_allow_html=True
)
if st.button("👵 Find Rishta"):
    with st.spinner("📡 Fetching rishta data from database, hold on beta..."):
        st.session_state.history.append({"role": "user", "content": prompt})

        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            Runner.run(  # <- notice: run_async instead of run_sync
                starting_agent=rishty_agent,
                input=st.session_state.history
            )
        )
    
        prompt = ""
        st.session_state.history.append({"role": "assistant", "content": result.final_output})

        st.success("Auntie replied:")
        st.write(result.final_output)
        
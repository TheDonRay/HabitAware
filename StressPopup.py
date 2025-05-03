import streamlit as st
import openai
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

class StressPopUp:
    def __init__(self):
        self.last_shown_at = 0  # Track when we last showed a tip
    
    def check_and_show_motivation(self, stress_attempts):
        """Check stress attempts and show motivation at 5+ attempts with 5-attempt intervals"""
        if stress_attempts >= 5 and (stress_attempts - self.last_shown_at) >= 5:
            self.show_popup(stress_attempts)
            self.last_shown_at = stress_attempts  # Update last shown counter
            return True
        return False

    def fetch_ai_tip(self):
        """Fetch a fresh AI-generated stress relief tip"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Change model if you need another version
                messages=[
                    {
                        "role": "user",
                        "content": "Give a short, science-backed tip for reducing stress. Make it friendly and practical."
                    }
                ],
                max_tokens=60,
                temperature=0.7
            )
            tip = response.choices[0].message["content"].strip()
            return tip
        except Exception as e:
            st.error(f"❌ OpenAI error: {e}")
            return "😞 Could not fetch a tip. Please try again later."

    def show_popup(self, current_attempts):
        """Display the motivational popup"""
        with st.popover("🌟 AI-Powered Stress Relief Tip", use_container_width=True):
            st.markdown(f"### You've reached {current_attempts} stress attempts!")
            st.markdown("Here's something to help you relax:")
            st.markdown(f"**{self.fetch_ai_tip()}**")
            
            if st.button("Got it!", key=f"dismiss_motivation_{current_attempts}"):
                # Mark the motivation as shown without resetting counter
                st.session_state.motivation_shown = True
                st.rerun()


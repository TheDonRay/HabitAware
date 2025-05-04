import streamlit as st
import openai
from dotenv import load_dotenv
import os
import time

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

class StressPopUp:
    def __init__(self):
        self.last_shown_at = 0  # Track when we last showed a tip
        self.last_positive_at = 0  # Track when we last showed positive reinforcement
        self.cached_tip = None
        self.cached_positive = None
        self.cache_time = 0
    
    def check_and_show_motivation(self, stress_attempts):
        """Check stress attempts and show motivation at 5+ attempts with 5-attempt intervals"""
        if stress_attempts >= 5 and (stress_attempts - self.last_shown_at) >= 5:
            self.show_popup(stress_attempts)
            self.last_shown_at = stress_attempts  # Update last shown counter
            return True
        return False

    def check_and_show_positive_reinforcement(self, time_since_last_stress):
        """Show positive reinforcement when user has been stress-free for a while"""
        if time_since_last_stress >= 15 and (time.time() - self.last_positive_at) >= 30:  # Show every 30 seconds if conditions met
            self.show_positive_popup(time_since_last_stress)
            self.last_positive_at = time.time()
            return True
        return False

    def fetch_ai_tip(self):
        """Fetch a fresh AI-generated stress relief tip"""
        # Use cached tip if it's less than 5 minutes old
        if self.cached_tip and (time.time() - self.cache_time) < 300:
            return self.cached_tip
            
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": "Give a simple, practical tip for reducing stress. Focus on common techniques like breathing, stretching, or taking a short break. Also include a short fact about stress relief. Keep it friendly and straightforward, under 30 words."
                    }
                ],
                max_tokens=40,
                temperature=0.7
            )
            self.cached_tip = response.choices[0].message["content"].strip()
            self.cache_time = time.time()
            return self.cached_tip
        except Exception as e:
            st.error(f"❌ OpenAI error: {e}")
            return "Take a deep breath and relax."

    def fetch_positive_message(self):
        """Fetch a motivational message"""
        # Use cached message if it's less than 5 minutes old
        if self.cached_positive and (time.time() - self.cache_time) < 300:
            return self.cached_positive
            
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": "Give a simple, encouraging message about making progress in breaking bad habits. Focus on the positive impact of their effort. Also a short fact on benefits of breaking bad habits. Keep it friendly and straightforward, under 30 words."
                    }
                ],
                max_tokens=30,
                temperature=0.7  # Lower temperature for more consistent messages
            )
            self.cached_positive = response.choices[0].message["content"].strip()
            self.cache_time = time.time()
            return self.cached_positive
        except Exception as e:
            st.error(f"❌ OpenAI error: {e}")
            return "You're making great progress!"

    def show_popup(self, current_attempts):
        """Display the motivational popup"""
        st.toast(
            f"🌟 You've reached {current_attempts} stress attempts!\n"
            f"Here's something to help you relax:\n"
            f"**{self.fetch_ai_tip()}**",
            icon="🌟"
        )

    def show_positive_popup(self, time_since_last_stress):
        """Display the positive reinforcement popup"""
        st.toast(
            f"🎉 You've been stress-free for {int(time_since_last_stress)} seconds!\n"
            f"**{self.fetch_positive_message()}**",
            icon="🎉"
        )


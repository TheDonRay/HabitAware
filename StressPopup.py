# - This would handle: Storing and managing motivational quotes Storing and managing health facts Logic for displaying these at appropriate intervals
# Any related UI elements for displaying the messages notification_manager.py - This would handle: Push notification logic Tracking attempt frequency
# Managing notification timing and content
# Integration with the system's notification system 

import streamlit as st
import random

class StressPopUp:
    def __init__(self):
        self.stressful_tips = [
            "💆 Take 5 deep breaths - inhale for 4 seconds, hold for 4, exhale for 6",
            "✋ Try squeezing a stress ball instead - it gives your hands something to do",
            "🚶‍♂️ Take a short walk - physical movement helps reduce stress hormones",
            "💧 Drink some water - dehydration can increase stress responses",
            "🎵 Listen to calming music for 2 minutes - it can lower your heart rate",
            "🧘 Try the 5-4-3-2-1 grounding technique: Notice 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste"
        ]
        self.last_shown_at = 0  # Track when we last showed a tip
        
    def check_and_show_motivation(self, stress_attempts):
        """Check stress attempts and show motivation at 5+ attempts with 5-attempt intervals"""
        if stress_attempts >= 5 and (stress_attempts - self.last_shown_at) >= 5:
            self.show_popup(stress_attempts)
            self.last_shown_at = stress_attempts  # Update last shown counter
            return True
        return False
    
    def show_popup(self, current_attempts):
        """Display the motivational popup"""
        with st.popover("🌟 Stress Relief Tip", use_container_width=True):
            st.markdown(f"### You've reached {current_attempts} stress attempts!")
            st.markdown("Here's a healthy alternative to try:")
            st.markdown(f"**{random.choice(self.stressful_tips)}**")
            
            if st.button("Got it!", key=f"dismiss_motivation_{current_attempts}"):
                # Don't reset the counter completely, just mark as shown
                st.session_state.motivation_shown = True
                st.rerun()
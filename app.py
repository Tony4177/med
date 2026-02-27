import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
from streamlit_autorefresh import st_autorefresh

DATA_FILE = "reminders.json"

# --- HEARTBEAT: Checks every 30 seconds ---
st_autorefresh(interval=30000, key="checker")

# ---------- Utility Functions ----------

def load_reminders():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_reminders(reminders):
    with open(DATA_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

def notify_browser(title, message):
    """Sends a real push notification to the user's desktop/phone browser."""
    js_code = f"""
    if (Notification.permission === 'granted') {{
        new Notification("{title}", {{
            body: "{message}",
            icon: "https://cdn-icons-png.flaticon.com/512/822/822143.png"
        }});
    }} else {{
        Notification.requestPermission();
    }}
    """
    streamlit_js_eval(js_expressions=js_code)

# ---------- App Configuration ----------

st.set_page_config(page_title="Medical Reminder System", page_icon="💊")

# Initial permission request
streamlit_js_eval(js_expressions="Notification.requestPermission()")

st.title("💊 Medical Reminder System")

# Sidebar Test Button
if st.sidebar.button("🔔 Test Push Notification"):
    notify_browser("Test Alert", "If you see this, your notifications are working!")

reminders = load_reminders()

# ---------- BACKGROUND CHECKER ----------
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
modified = False

for r in reminders:
    # Match Date and Time exactly (to the minute)
    if r['datetime'] == now_str and not r.get("notified", False):
        notify_browser(
            f"Medicine Alert: {r['name']}", 
            f"It is time to take {r['dosage']} of {r['medicine']}"
        )
        r["notified"] = True
        modified = True
        st.toast(f"Notification triggered for {r['medicine']}!", icon="🔔")

if modified:
    save_reminders(reminders)

# ---------- Menu Selection ----------
menu = st.sidebar.selectbox("Menu", ["Add Reminder", "View Reminders"])

if menu == "Add Reminder":
    st.subheader("Add New Reminder")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Patient Name")
        medicine = st.text_input("Medicine Name")
    with col2:
        dosage = st.text_input("Dosage (e.g., 2 pills)")
        
    st.write("---")
    st.write("### Set Reminder Time")
    rem_date = st.date_input("Select Date", datetime.now())
    rem_time = st.time_input("Select Exact Time") # User can set ANY time here

    if st.button("Save Reminder"):
        if name and medicine and dosage:
            # Combine date and time into the matching format
            dt_string = f"{rem_date} {rem_time.strftime('%H:%M')}"
            
            new_reminder = {
                "id": int(time.time()),
                "name": name,
                "medicine": medicine,
                "dosage": dosage,
                "datetime": dt_string,
                "notified": False
            }
            reminders.append(new_reminder)
            save_reminders(reminders)
            st.success(f"Reminder set for {medicine} at {dt_string}")
        else:
            st.error("Please fill in all details.")

elif menu == "View Reminders":
    st.subheader("Schedule")
    if not reminders:
        st.info("No reminders scheduled.")
    else:
        for reminder in reminders:
            status = "✅ Done" if reminder.get("notified") else "⏳ Waiting"
            with st.expander(f"{reminder['datetime']} - {reminder['medicine']} ({status})"):
                st.write(f"**Patient:** {reminder['name']}")
                st.write(f"**Dosage:** {reminder['dosage']}")
                if st.button("Delete", key=f"del_{reminder['id']}"):
                    reminders = [r for r in reminders if r["id"] != reminder["id"]]
                    save_reminders(reminders)
                    st.rerun()

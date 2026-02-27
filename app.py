import streamlit as st
import json
import os
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
from streamlit_autorefresh import st_autorefresh

DATA_FILE = "reminders.json"

# --- AUTO-REFRESH (Checks every 30 seconds) ---
st_autorefresh(interval=30000, key="datacheck")

# ---------- Utility Functions ----------

def load_reminders():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_reminders(reminders):
    with open(DATA_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

def trigger_notification(name, med, dosage):
    """Sends a browser-level push notification."""
    js_code = f"""
    if (Notification.permission === 'granted') {{
        new Notification('MEDICINE ALERT: {name}', {{
            body: 'Time to take {dosage} of {med}!',
            icon: 'https://cdn-icons-png.flaticon.com/512/822/822143.png'
        }});
    }} else if (Notification.permission !== 'denied') {{
        Notification.requestPermission();
    }}
    """
    streamlit_js_eval(js_expressions=js_code)

# ---------- App UI ----------

st.set_page_config(page_title="Medical Reminder System", page_icon="💊")

# Request permission on app load
streamlit_js_eval(js_expressions="Notification.requestPermission()")

st.title("💊 Medical Reminder System")

# --- BACKGROUND CHECKER ---
# This part scans your JSON and fires a notification if the time matches
reminders = load_reminders()
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

for r in reminders:
    # We strip the seconds for a clean match on the minute
    if r['datetime'][:16] == now_str:
        trigger_notification(r['name'], r['medicine'], r['dosage'])
        st.toast(f"🚨 ALERT: {r['medicine']} for {r['name']}", icon="🔔")

menu = st.sidebar.selectbox("Menu", ["Add Reminder", "View Reminders"])

# ---------- Add Reminder ----------

if menu == "Add Reminder":
    st.subheader("Add New Reminder")
    name = st.text_input("Patient Name")
    medicine = st.text_input("Medicine Name")
    dosage = st.text_input("Dosage (e.g., 1 tablet)")
    date = st.date_input("Date")
    time_val = st.time_input("Time")

    if st.button("Add Reminder"):
        if name and medicine and dosage:
            reminder = {
                "id": len(reminders) + 1,
                "name": name,
                "medicine": medicine,
                "dosage": dosage,
                "datetime": f"{date} {time_val}"
            }
            reminders.append(reminder)
            save_reminders(reminders)
            st.success("Reminder added successfully!")
        else:
            st.error("Please fill all fields.")

# ---------- View Reminders ----------

elif menu == "View Reminders":
    st.subheader("All Reminders")
    if not reminders:
        st.info("No reminders added yet.")
    else:
        for reminder in reminders:
            with st.expander(f"🧑 {reminder['name']} - {reminder['medicine']}"):
                st.write(f"🧾 Dosage: {reminder['dosage']}")
                st.write(f"⏰ Scheduled: {reminder['datetime']}")
                
                if st.button(f"Delete", key=f"del_{reminder['id']}"):
                    reminders = [r for r in reminders if r["id"] != reminder["id"]]
                    save_reminders(reminders)
                    st.rerun()

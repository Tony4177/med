import streamlit as st
import json
import os
import threading
import time
from datetime import datetime

try:
    from plyer import notification
except ImportError:
    notification = None

DATA_FILE = "reminders.json"

# ---------- Utility Functions ----------

def load_reminders():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_reminders(reminders):
    with open(DATA_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

# ---------- Notification Thread ----------

def check_reminders():
    while True:
        if os.path.exists(DATA_FILE) and notification is not None:
            try:
                with open(DATA_FILE, "r") as f:
                    reminders = json.load(f)
                
                modified = False
                now = datetime.now()
                
                for r in reminders:
                    if not r.get("notified", False):
                        try:
                            # Parse "YYYY-MM-DD HH:MM:SS"
                            rem_time = datetime.fromisoformat(str(r["datetime"]))
                            if now >= rem_time:
                                notification.notify(
                                    title=f"Medical Reminder: {r['name']}",
                                    message=f"Take {r['medicine']} ({r['dosage']})\nTime: {r['datetime']}",
                                    app_name="Medical Reminder",
                                    timeout=10
                                )
                                r["notified"] = True
                                modified = True
                        except Exception as e:
                            print(f"Error processing reminder runtime: {e}")
                
                if modified:
                    with open(DATA_FILE, "w") as f:
                        json.dump(reminders, f, indent=4)
            except Exception as e:
                print(f"Background thread error: {e}")
        
        time.sleep(10)  # Check every 10 seconds

@st.cache_resource
def start_thread():
    t = threading.Thread(target=check_reminders, daemon=True)
    t.start()
    return t

if notification is not None:
    start_thread()
else:
    st.warning("The 'plyer' library is not installed. Desktop notifications will not work. Please install it with 'pip install plyer'.")

# ---------- App UI ----------

st.set_page_config(page_title="Medical Reminder System", page_icon="💊")

st.title("💊 Medical Reminder System")
st.write("Simple medication reminder app built with Streamlit")

menu = st.sidebar.selectbox("Menu", ["Add Reminder", "View Reminders"])

reminders = load_reminders()

# ---------- Add Reminder ----------

if menu == "Add Reminder":
    st.subheader("Add New Reminder")

    name = st.text_input("Patient Name")
    medicine = st.text_input("Medicine Name")
    dosage = st.text_input("Dosage (e.g., 1 tablet)")
    date = st.date_input("Date")
    time = st.time_input("Time")

    if st.button("Add Reminder"):
        if name and medicine and dosage:
            reminder = {
                "id": len(reminders) + 1,
                "name": name,
                "medicine": medicine,
                "dosage": dosage,
                "datetime": f"{date} {time}"
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
            st.markdown(f"""
            ### 🧑 {reminder['name']}
            - 💊 Medicine: {reminder['medicine']}
            - 🧾 Dosage: {reminder['dosage']}
            - ⏰ Date & Time: {reminder['datetime']}
            """)

            if st.button(f"Delete {reminder['id']}"):
                reminders = [r for r in reminders if r["id"] != reminder["id"]]
                save_reminders(reminders)
                st.warning("Reminder deleted.")
                st.experimental_rerun()

import streamlit as st
import json
import os
from datetime import datetime

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
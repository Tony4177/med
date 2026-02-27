import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Smart Medicine Reminder", layout="wide")

# ----------------------------
# Session Storage
# ----------------------------
if "medicines" not in st.session_state:
    st.session_state.medicines = []

if "logs" not in st.session_state:
    st.session_state.logs = []

# ----------------------------
# Add Medicine Section
# ----------------------------
st.title("💊 Smart Medicine Reminder System")

st.header("Add Medicine")

name = st.text_input("Medicine Name")
dosage = st.text_input("Dosage")
time = st.time_input("Medicine Time")
total_pills = st.number_input("Total Pills", min_value=1)

if st.button("Add Medicine"):
    st.session_state.medicines.append({
        "name": name,
        "dosage": dosage,
        "time": time,
        "pills": total_pills
    })
    st.success("Medicine Added Successfully!")

# ----------------------------
# Dashboard
# ----------------------------
st.header("📊 Dashboard")

taken_count = 0
total_count = len(st.session_state.logs)

for med in st.session_state.medicines:
    st.subheader(med["name"])
    st.write(f"Dosage: {med['dosage']}")
    st.write(f"Time: {med['time']}")
    st.write(f"Pills Left: {med['pills']}")

    col1, col2 = st.columns(2)

    if col1.button(f"Taken - {med['name']}"):
        med["pills"] -= 1
        st.session_state.logs.append({"medicine": med["name"], "status": "Taken"})
        taken_count += 1
        st.success("Marked as Taken")

    if col2.button(f"Missed - {med['name']}"):
        st.session_state.logs.append({"medicine": med["name"], "status": "Missed"})
        st.warning("Marked as Missed")

    # Refill Alert
    if med["pills"] <= 2:
        st.error("⚠ Low Stock! Please Refill")

# ----------------------------
# Adherence Calculation
# ----------------------------
taken_count = len([log for log in st.session_state.logs if log["status"] == "Taken"])
total_count = len(st.session_state.logs)

if total_count > 0:
    adherence = (taken_count / total_count) * 100
else:
    adherence = 0

st.header("📈 Adherence Report")
st.write(f"Adherence: {adherence:.2f}%")
st.progress(adherence / 100)

# ----------------------------
# AI Risk Score (Simulated)
# ----------------------------
if adherence < 60:
    risk = "🔴 High Risk"
elif adherence < 85:
    risk = "🟡 Medium Risk"
else:
    risk = "🟢 Low Risk"

st.write("AI Risk Level:", risk)

# ----------------------------
# AI Weekly Summary (Auto Generated)
# ----------------------------
st.header("🧠 AI Weekly Summary")

if total_count > 0:
    summary = f"""
    This week adherence is {adherence:.2f}%.
    Total doses: {total_count}.
    Missed doses: {total_count - taken_count}.
    Risk Level: {risk}.
    """
    st.info(summary)
else:
    st.write("No data available yet.")

# ----------------------------
# Caregiver Alert Simulation
# ----------------------------
missed_count = len([log for log in st.session_state.logs if log["status"] == "Missed"])

if missed_count >= 3:
    st.error("🚨 Caregiver Alert Triggered! (Simulated Notification)")

# ----------------------------
# Chat Assistant (Basic)
# ----------------------------
st.header("🤖 AI Health Assistant")

question = st.text_input("Ask something like: What is my adherence?")

if question:
    if "adherence" in question.lower():
        st.write(f"Your adherence is {adherence:.2f}%")
    elif "missed" in question.lower():
        st.write(f"You missed {total_count - taken_count} doses.")
    else:
        st.write("I can answer about adherence and missed doses.")

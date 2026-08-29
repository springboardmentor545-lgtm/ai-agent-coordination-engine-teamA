import os

from flask import Flask, render_template, request
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from tools import (
    symptom_checker,
    bmi_calculator,
    appointment_booking
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Please check your .env file."
    )


# ============================================================
# GROQ MODEL
# ============================================================

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=0.3
)


# ============================================================
# CHAT DATA
# Server-side variables
# No Flask session = No large cookie problem
# ============================================================

messages = [
    {
        "sender": "agent",
        "text": (
            "Hello! I am your AI Agent.\n\n"
            "I can answer general questions and "
            "also provide healthcare tools."
        )
    }
]


# ============================================================
# TOOL STATE
# ============================================================

current_state = "normal"

user_height = None

appointment_doctor = None

appointment_date = None


# ============================================================
# GENERAL AI
# ============================================================

def normal_chat(query):

    prompt = f"""
You are a professional general-purpose AI assistant.

You are NOT restricted to healthcare.

You can answer questions about:

General Knowledge
Programming
Python
Java
C
Artificial Intelligence
Machine Learning
Data Science
Web Development
Education
Mathematics
Science
Technology
Career
Interview Preparation
Business
Healthcare
Daily Life
and other general topics.

Answer the user's question clearly and professionally.

Do not force normal questions into healthcare.

User Question:
{query}
"""

    response = llm.invoke(prompt)

    return response.content


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/", methods=["GET", "POST"])
def chat():

    global current_state
    global user_height
    global appointment_doctor
    global appointment_date


    # ========================================================
    # POST REQUEST
    # ========================================================

    if request.method == "POST":

        # ----------------------------------------------------
        # CHECK TOOL BUTTON
        # ----------------------------------------------------

        selected_tool = request.form.get(
            "tool",
            ""
        )


        # ====================================================
        # SYMPTOM CHECKER BUTTON
        # ====================================================

        if selected_tool == "symptom":

            current_state = "symptom_input"

            response = (
                "Symptom Checker activated.\n\n"
                "Please describe your symptoms.\n"
                "Example: I have fever and cough"
            )

            messages.append({
                "sender": "agent",
                "text": response
            })

            return render_template(
                "index.html",
                messages=messages
            )


        # ====================================================
        # BMI BUTTON
        # ====================================================

        if selected_tool == "bmi":

            current_state = "bmi_height"

            response = (
                "BMI Calculator activated.\n\n"
                "Please enter your height in cm.\n"
                "Example: 170"
            )

            messages.append({
                "sender": "agent",
                "text": response
            })

            return render_template(
                "index.html",
                messages=messages
            )


        # ====================================================
        # APPOINTMENT BUTTON
        # ====================================================

        if selected_tool == "appointment":

            current_state = "appointment_doctor"

            response = (
                "Appointment Booking activated.\n\n"
                "Please enter the doctor name.\n"
                "Example: Dr. Ravi"
            )

            messages.append({
                "sender": "agent",
                "text": response
            })

            return render_template(
                "index.html",
                messages=messages
            )


        # ====================================================
        # USER MESSAGE
        # ====================================================

        user_message = request.form.get(
            "message",
            ""
        ).strip()


        if not user_message:

            return render_template(
                "index.html",
                messages=messages
            )


        # ----------------------------------------------------
        # SAVE USER MESSAGE
        # ----------------------------------------------------

        messages.append({
            "sender": "user",
            "text": user_message
        })


        # ====================================================
        # STATE 1 - SYMPTOM CHECKER
        # ====================================================

        if current_state == "symptom_input":

            response = symptom_checker.invoke(
                user_message
            )

            current_state = "normal"


        # ====================================================
        # STATE 2 - BMI HEIGHT
        # ====================================================

        elif current_state == "bmi_height":

            try:

                height = float(user_message)

                if height <= 0:

                    response = (
                        "Please enter a valid height.\n"
                        "Example: 170"
                    )

                else:

                    user_height = height

                    current_state = "bmi_weight"

                    response = (
                        f"Height received: {height:.0f} cm\n\n"
                        "Now please enter your weight in kg.\n"
                        "Example: 70"
                    )

            except ValueError:

                response = (
                    "Please enter height as a number.\n"
                    "Example: 170"
                )


        # ====================================================
        # STATE 3 - BMI WEIGHT
        # ====================================================

        elif current_state == "bmi_weight":

            try:

                weight = float(user_message)

                if weight <= 0:

                    response = (
                        "Please enter a valid weight.\n"
                        "Example: 70"
                    )

                else:

                    response = bmi_calculator.invoke(
                        f"{user_height} {weight}"
                    )

                    user_height = None

                    current_state = "normal"

            except ValueError:

                response = (
                    "Please enter weight as a number.\n"
                    "Example: 70"
                )


        # ====================================================
        # STATE 4 - APPOINTMENT DOCTOR
        # ====================================================

        elif current_state == "appointment_doctor":

            appointment_doctor = user_message

            current_state = "appointment_date"

            response = (
                f"Doctor name received: {appointment_doctor}\n\n"
                "Please enter the appointment date.\n"
                "Example: 15 August 2026"
            )


        # ====================================================
        # STATE 5 - APPOINTMENT DATE
        # ====================================================

        elif current_state == "appointment_date":

            appointment_date = user_message

            current_state = "appointment_time"

            response = (
                f"Appointment date received: {appointment_date}\n\n"
                "Please enter the appointment time.\n"
                "Example: 10 AM"
            )


        # ====================================================
        # STATE 6 - APPOINTMENT TIME
        # ====================================================

        elif current_state == "appointment_time":

            appointment_time = user_message

            response = appointment_booking.invoke(
                f"{appointment_doctor} | "
                f"{appointment_date} | "
                f"{appointment_time}"
            )

            appointment_doctor = None
            appointment_date = None

            current_state = "normal"


        # ====================================================
        # STATE 7 - NORMAL AI
        # ====================================================

        else:

            lower_message = user_message.lower()


            # ------------------------------------------------
            # SYMPTOM CHECKER COMMAND
            # ------------------------------------------------

            if (
                lower_message == "symptom checker"
                or lower_message == "symptom check"
                or lower_message == "check symptoms"
            ):

                current_state = "symptom_input"

                response = (
                    "Symptom Checker activated.\n\n"
                    "Please describe your symptoms.\n"
                    "Example: I have fever and cough"
                )


            # ------------------------------------------------
            # BMI COMMAND
            # ------------------------------------------------

            elif (
                lower_message == "bmi"
                or lower_message == "bmi calculator"
                or lower_message == "calculate bmi"
            ):

                current_state = "bmi_height"

                response = (
                    "BMI Calculator activated.\n\n"
                    "Please enter your height in cm.\n"
                    "Example: 170"
                )


            # ------------------------------------------------
            # APPOINTMENT COMMAND
            # ------------------------------------------------

            elif (
                lower_message == "appointment"
                or lower_message == "appointment booking"
                or lower_message == "book appointment"
            ):

                current_state = "appointment_doctor"

                response = (
                    "Appointment Booking activated.\n\n"
                    "Please enter the doctor name.\n"
                    "Example: Dr. Ravi"
                )


            # ------------------------------------------------
            # GENERAL AI
            # ------------------------------------------------

            else:

                response = normal_chat(
                    user_message
                )


        # ====================================================
        # SAVE AGENT RESPONSE
        # ====================================================

        messages.append({
            "sender": "agent",
            "text": response
        })


    # ========================================================
    # DISPLAY
    # ========================================================

    return render_template(
        "index.html",
        messages=messages
    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print("Healthcare AI Agent - Milestone 2")

    print("Server running at:")
    print("http://127.0.0.1:5000")

    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
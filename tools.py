from langchain.tools import tool
from datetime import datetime

# -----------------------------
# 1. Symptom Checker Tool
# -----------------------------
@tool
def symptom_checker(symptoms: str) -> str:
    """
    Checks symptoms and provides basic health suggestions.
    """

    symptoms = symptoms.lower()

    if "fever" in symptoms and "cough" in symptoms:
        return """
Possible Condition:
- Viral Fever
- Common Cold

Recommendation:
Drink plenty of water, take rest, and consult a doctor if symptoms continue.
"""

    elif "headache" in symptoms:
        return """
Possible Condition:
- Stress
- Migraine

Recommendation:
Take proper rest, stay hydrated, and consult a doctor if severe.
"""

    elif "chest pain" in symptoms:
        return """
Emergency Alert!

Chest pain can be serious.
Please visit the nearest hospital immediately.
"""

    else:
        return "Unable to identify the condition. Please consult a healthcare professional."


# -----------------------------
# 2. BMI Calculator
# -----------------------------
@tool
def bmi_calculator(data: str) -> str:
    """
    Calculate BMI.
    Input format:
    height weight

    Example:
    170 70
    """

    try:

        height, weight = data.split()

        height = float(height)
        weight = float(weight)

        bmi = weight / ((height / 100) ** 2)

        if bmi < 18.5:
            status = "Underweight"

        elif bmi < 25:
            status = "Normal"

        elif bmi < 30:
            status = "Overweight"

        else:
            status = "Obese"

        return f"BMI : {bmi:.2f}\nCategory : {status}"

    except:
        return "Enter input like: 170 70"


# -----------------------------
# 3. Appointment Booking Tool
# -----------------------------
@tool
def appointment_booking(details: str) -> str:
    """
    Books appointment.

    Example:
    Dr.Ravi tomorrow 10AM
    """

    return f"""
Appointment Booked Successfully

Doctor : {details}

Booking Time :
{datetime.now()}

Status : Confirmed
"""
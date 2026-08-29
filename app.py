import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from tools import symptom_checker, bmi_calculator, appointment_booking

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Groq API Key not found!")
    exit()

# Initialize Groq
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=0.3
)

print("=" * 60)
print("🏥 Healthcare AI Agent - Milestone 2")
print("Available Tools:")
print("1. Symptom Checker")
print("2. BMI Calculator")
print("3. Appointment Booking")
print("Type 'exit' to quit")
print("=" * 60)

while True:

    query = input("\nYou : ")

    if query.lower() == "exit":
        print("Goodbye 👋")
        break

    lower_query = query.lower()

    # -------- Symptom Checker --------
    if any(word in lower_query for word in ["fever", "cough", "cold", "headache", "chest pain"]):
        print("\nAgent:")
        print(symptom_checker.invoke(query))
        continue

    # -------- BMI Calculator --------
    elif lower_query.startswith("bmi"):
        print("\nEnter Height(cm) and Weight(kg)")
        data = input("Example: 170 70 : ")

        print("\nAgent:")
        print(bmi_calculator.invoke(data))
        continue

    # -------- Appointment Booking --------
    elif "appointment" in lower_query or "book" in lower_query:

        doctor = input("Doctor Name : ")
        date = input("Date : ")
        time = input("Time : ")

        details = f"{doctor} | {date} | {time}"

        print("\nAgent:")
        print(appointment_booking.invoke(details))
        continue

    # -------- Normal AI Chat --------
    else:

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a Healthcare AI Assistant. Give helpful health information, but do not replace professional medical advice."),
            ("human", "{query}")
        ])

        chain = prompt | llm

        response = chain.invoke({
            "query": query
        })

        print("\nAgent:")
        print(response.content)
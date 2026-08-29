import requests

url = "http://localhost:8000/api/v1/triage"
payload = {
    "patient_id": "6cf8d015-a29b-4a42-80b6-e67555a086f1",
    "message": "I have been experiencing a very tight pain in the center of my chest for the past 2 hours. It hurts when I breathe deeply and I feel a bit dizzy and sweaty."
}

print("Running End-to-End Triage API Test...")
print("Submitting symptoms...")

try:
    response = requests.post(url, json=payload)
    print("\n--- Response Received ---")
    print("Status Code:", response.status_code)
    try:
        data = response.json()
        print("Urgency Level:", data.get("urgency_level"))
        print("Department:", data.get("recommended_department"))
        print("Condition:", data.get("suspected_condition"))
        print("Appointment ID:", data.get("appointment_id"))
        print("Triage ID:", data.get("triage_id"))
        print("\nAI Explanation:\n", data.get("ai_explanation"))
    except:
        print("Response Body:", response.text)
except Exception as e:
    print("Error:", e)

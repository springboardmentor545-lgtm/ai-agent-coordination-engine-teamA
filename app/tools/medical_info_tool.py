"""
Medical Info Tool
=================
Provides medical information database for common conditions,
symptoms, medications, and departments.

Use Cases:
- Look up disease information
- Get medicine details
- Find department by specialty
- Symptom checker
- Common medical procedures

Author: Team A - Pratik
"""

import logging
from typing import Dict, Any, List
from langchain.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


# ============================================
# Medical Knowledge Database
# ============================================
DISEASES_DATABASE = {
    "diabetes": {
        "type": "Chronic disease",
        "symptoms": ["Increased thirst", "Frequent urination", "Fatigue", "Blurred vision", "Slow healing wounds"],
        "risk_factors": ["Family history", "Obesity", "Age > 45", "Sedentary lifestyle"],
        "department": "Endocrinology / General Medicine",
        "severity": "Moderate to High",
        "treatment": "Insulin, oral medications, diet control, exercise"
    },
    "hypertension": {
        "type": "Cardiovascular condition",
        "symptoms": ["Headaches", "Shortness of breath", "Nosebleeds", "Chest pain", "Dizziness"],
        "risk_factors": ["Age", "Family history", "Obesity", "High salt diet", "Smoking"],
        "department": "Cardiology",
        "severity": "High",
        "treatment": "Antihypertensive drugs, lifestyle changes, low sodium diet"
    },
    "asthma": {
        "type": "Respiratory condition",
        "symptoms": ["Wheezing", "Shortness of breath", "Chest tightness", "Coughing"],
        "risk_factors": ["Allergies", "Family history", "Air pollution", "Respiratory infections"],
        "department": "Pulmonology",
        "severity": "Moderate",
        "treatment": "Inhalers (bronchodilators), corticosteroids, avoid triggers"
    },
    "migraine": {
        "type": "Neurological condition",
        "symptoms": ["Severe headache", "Nausea", "Sensitivity to light", "Vision problems"],
        "risk_factors": ["Family history", "Stress", "Hormonal changes", "Certain foods"],
        "department": "Neurology",
        "severity": "Moderate",
        "treatment": "Pain relievers, triptans, preventive medications"
    },
    "fracture": {
        "type": "Bone injury",
        "symptoms": ["Severe pain", "Swelling", "Bruising", "Deformity", "Inability to move"],
        "risk_factors": ["Osteoporosis", "Age", "Sports injuries", "Accidents"],
        "department": "Orthopedics",
        "severity": "High",
        "treatment": "Immobilization (cast/splint), pain management, surgery if needed"
    },
    "flu": {
        "type": "Viral infection",
        "symptoms": ["Fever", "Cough", "Sore throat", "Body aches", "Fatigue", "Chills"],
        "risk_factors": ["Weak immunity", "Age extremes", "Chronic conditions"],
        "department": "General Medicine",
        "severity": "Low to Moderate",
        "treatment": "Rest, fluids, antiviral drugs, symptomatic treatment"
    },
    "covid": {
        "type": "Viral infection",
        "symptoms": ["Fever", "Cough", "Loss of taste/smell", "Fatigue", "Difficulty breathing"],
        "risk_factors": ["Age > 60", "Chronic diseases", "Immunocompromised"],
        "department": "Infectious Disease / Emergency",
        "severity": "Moderate to Critical",
        "treatment": "Isolation, supportive care, antiviral drugs, oxygen if needed"
    },
    "heart attack": {
        "type": "Cardiovascular emergency",
        "symptoms": ["Chest pain", "Arm pain", "Shortness of breath", "Sweating", "Nausea"],
        "risk_factors": ["High cholesterol", "Smoking", "Diabetes", "Hypertension"],
        "department": "Emergency / Cardiology",
        "severity": "CRITICAL",
        "treatment": "IMMEDIATE emergency care, aspirin, angioplasty, medications"
    }
}

MEDICINES_DATABASE = {
    "paracetamol": {
        "generic_name": "Acetaminophen",
        "uses": ["Fever", "Mild to moderate pain", "Headache"],
        "dosage": "500-1000 mg every 4-6 hours (max 4g/day)",
        "side_effects": ["Rare: liver damage with overdose"],
        "warnings": "Do not exceed 4g per day. Avoid alcohol."
    },
    "ibuprofen": {
        "generic_name": "Ibuprofen",
        "uses": ["Pain relief", "Fever", "Inflammation"],
        "dosage": "200-400 mg every 4-6 hours (max 1200mg/day OTC)",
        "side_effects": ["Stomach upset", "Ulcers", "Kidney issues"],
        "warnings": "Take with food. Avoid if you have stomach ulcers."
    },
    "amoxicillin": {
        "generic_name": "Amoxicillin",
        "uses": ["Bacterial infections", "Respiratory infections", "UTI"],
        "dosage": "250-500 mg every 8 hours (as prescribed)",
        "side_effects": ["Diarrhea", "Nausea", "Allergic reactions"],
        "warnings": "Complete full course. Inform about penicillin allergy."
    },
    "aspirin": {
        "generic_name": "Acetylsalicylic acid",
        "uses": ["Pain relief", "Fever", "Heart attack prevention"],
        "dosage": "325-650 mg every 4 hours (75-100 mg for heart)",
        "side_effects": ["Stomach bleeding", "Ulcers", "Ringing in ears"],
        "warnings": "Not for children under 16. Avoid if bleeding disorders."
    }
}

DEPARTMENTS_INFO = {
    "cardiology": {
        "specialty": "Heart and cardiovascular system",
        "conditions": ["Heart disease", "Hypertension", "Arrhythmia", "Heart attack"],
        "common_procedures": ["ECG", "Echocardiogram", "Angioplasty", "Bypass surgery"]
    },
    "neurology": {
        "specialty": "Brain and nervous system",
        "conditions": ["Stroke", "Epilepsy", "Migraine", "Parkinson's disease"],
        "common_procedures": ["MRI", "EEG", "CT scan", "Lumbar puncture"]
    },
    "orthopedics": {
        "specialty": "Bones, joints, and muscles",
        "conditions": ["Fractures", "Arthritis", "Sports injuries", "Back pain"],
        "common_procedures": ["X-ray", "Joint replacement", "Arthroscopy"]
    },
    "pediatrics": {
        "specialty": "Children's health (0-18 years)",
        "conditions": ["Vaccinations", "Childhood diseases", "Growth issues"],
        "common_procedures": ["Well-baby check", "Immunizations", "Growth monitoring"]
    },
    "emergency": {
        "specialty": "Emergency and trauma care",
        "conditions": ["Accidents", "Heart attacks", "Strokes", "Severe injuries"],
        "common_procedures": ["Triage", "Resuscitation", "Emergency surgery"]
    },
    "general medicine": {
        "specialty": "General health and common illnesses",
        "conditions": ["Fever", "Flu", "Diabetes", "General check-ups"],
        "common_procedures": ["Physical exam", "Blood tests", "Prescriptions"]
    }
}


class MedicalInfoTool(BaseTool):
    """
    Medical information lookup tool.
    Provides information about diseases, medicines, and departments.
    """
    
    name: str = "medical_info"
    description: str = (
        "Useful for looking up medical information including:\n"
        "- Disease information (symptoms, treatment, department)\n"
        "- Medicine details (uses, dosage, side effects)\n"
        "- Department information (specialty, procedures)\n"
        "- Symptom checker\n"
        "Examples: 'disease diabetes', 'medicine paracetamol', 'department cardiology'"
    )
    
    # Track usage
    usage_count: int = Field(default=0)
    
    def _run(self, query: str) -> str:
        """Execute the medical info lookup."""
        try:
            self.usage_count += 1
            logger.info(f"🏥 Medical Info tool called with: {query}")
            
            query = query.strip().lower()
            
            # Route to appropriate lookup
            if "disease" in query or "condition" in query or "illness" in query:
                return self._lookup_disease(query)
            
            if "medicine" in query or "medication" in query or "drug" in query:
                return self._lookup_medicine(query)
            
            if "department" in query or "specialty" in query:
                return self._lookup_department(query)
            
            if "symptom" in query:
                return self._check_symptoms(query)
            
            # Try to detect what user is asking
            for disease in DISEASES_DATABASE:
                if disease in query:
                    return self._lookup_disease(f"disease {disease}")
            
            for medicine in MEDICINES_DATABASE:
                if medicine in query:
                    return self._lookup_medicine(f"medicine {medicine}")
            
            for dept in DEPARTMENTS_INFO:
                if dept in query:
                    return self._lookup_department(f"department {dept}")
            
            return self._show_available_info()
            
        except Exception as e:
            logger.error(f"❌ Medical Info error: {e}")
            return f"❌ Error: {str(e)}"
    
    def _lookup_disease(self, query: str) -> str:
        """Look up disease information."""
        for disease_name, info in DISEASES_DATABASE.items():
            if disease_name in query:
                symptoms_list = "\n     • ".join(info["symptoms"])
                risk_list = "\n     • ".join(info["risk_factors"])
                
                # Add severity emoji
                severity_emoji = "🟢" if "Low" in info["severity"] else "🟡" if "Moderate" in info["severity"] else "🔴"
                
                return (
                    f"🏥 Disease Information: {disease_name.title()}\n"
                    f"   Type: {info['type']}\n"
                    f"   Severity: {severity_emoji} {info['severity']}\n"
                    f"   Department: {info['department']}\n\n"
                    f"   📋 Symptoms:\n     • {symptoms_list}\n\n"
                    f"   ⚠️ Risk Factors:\n     • {risk_list}\n\n"
                    f"   💊 Treatment: {info['treatment']}\n\n"
                    f"   ⚠️ Note: This is general information. Consult a doctor for diagnosis."
                )
        
        available = ", ".join(DISEASES_DATABASE.keys())
        return f"❌ Disease not found in database.\n📋 Available: {available}"
    
    def _lookup_medicine(self, query: str) -> str:
        """Look up medicine information."""
        for med_name, info in MEDICINES_DATABASE.items():
            if med_name in query:
                uses_list = ", ".join(info["uses"])
                effects_list = ", ".join(info["side_effects"])
                
                return (
                    f"💊 Medicine Information: {med_name.title()}\n"
                    f"   Generic Name: {info['generic_name']}\n"
                    f"   Uses: {uses_list}\n"
                    f"   Recommended Dosage: {info['dosage']}\n"
                    f"   Side Effects: {effects_list}\n\n"
                    f"   ⚠️ Warnings: {info['warnings']}\n\n"
                    f"   ⚠️ Note: Always consult a doctor before taking any medication."
                )
        
        available = ", ".join(MEDICINES_DATABASE.keys())
        return f"❌ Medicine not found in database.\n📋 Available: {available}"
    
    def _lookup_department(self, query: str) -> str:
        """Look up department information."""
        for dept_name, info in DEPARTMENTS_INFO.items():
            if dept_name in query:
                conditions_list = "\n     • ".join(info["conditions"])
                procedures_list = "\n     • ".join(info["common_procedures"])
                
                return (
                    f"🏥 Department: {dept_name.title()}\n"
                    f"   Specialty: {info['specialty']}\n\n"
                    f"   📋 Common Conditions Treated:\n     • {conditions_list}\n\n"
                    f"   🔬 Common Procedures:\n     • {procedures_list}"
                )
        
        available = ", ".join(DEPARTMENTS_INFO.keys())
        return f"❌ Department not found.\n📋 Available: {available}"
    
    def _check_symptoms(self, query: str) -> str:
        """Check possible diseases based on symptoms."""
        matches = []
        
        for disease_name, info in DISEASES_DATABASE.items():
            for symptom in info["symptoms"]:
                if symptom.lower() in query:
                    if disease_name not in [m[0] for m in matches]:
                        matches.append((disease_name, info))
        
        if not matches:
            return (
                "❌ No matching conditions found in database.\n"
                "💡 Try being more specific about symptoms.\n"
                "⚠️ For accurate diagnosis, please consult a healthcare professional."
            )
        
        result = f"🔍 Possible Conditions Based on Symptoms:\n\n"
        for disease_name, info in matches[:3]:  # Show top 3
            severity_emoji = "🟢" if "Low" in info["severity"] else "🟡" if "Moderate" in info["severity"] else "🔴"
            result += (
                f"   • {disease_name.title()}\n"
                f"     Severity: {severity_emoji} {info['severity']}\n"
                f"     Department: {info['department']}\n\n"
            )
        
        result += "⚠️ This is not a diagnosis. Please consult a doctor for proper evaluation."
        return result
    
    def _show_available_info(self) -> str:
        """Show what info is available in the database."""
        diseases = ", ".join(DISEASES_DATABASE.keys())
        medicines = ", ".join(MEDICINES_DATABASE.keys())
        departments = ", ".join(DEPARTMENTS_INFO.keys())
        
        return (
            f"📚 Available Medical Information:\n\n"
            f"🏥 Diseases: {diseases}\n\n"
            f"💊 Medicines: {medicines}\n\n"
            f"🏢 Departments: {departments}\n\n"
            f"💡 Ask like: 'disease diabetes' or 'medicine paracetamol'"
        )
    
    async def _arun(self, query: str) -> str:
        """Async version"""
        return self._run(query)
    
    def get_stats(self) -> Dict[str, Any]:
        """Return tool usage statistics"""
        return {
            "tool_name": self.name,
            "usage_count": self.usage_count,
            "total_diseases": len(DISEASES_DATABASE),
            "total_medicines": len(MEDICINES_DATABASE),
            "total_departments": len(DEPARTMENTS_INFO)
        }


# ============================================
# Standalone Testing
# ============================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🏥 Medical Info Tool - Test Suite")
    print("=" * 60 + "\n")
    
    med_tool = MedicalInfoTool()
    
    test_cases = [
        "disease diabetes",
        "disease heart attack",
        "medicine paracetamol",
        "medicine amoxicillin",
        "department cardiology",
        "department emergency",
        "symptoms fever cough",
        "symptoms chest pain shortness of breath",
        "hypertension"  # partial query test
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test}")
        result = med_tool._run(test)
        print(f"{result}\n")
        print("-" * 60 + "\n")
    
    stats = med_tool.get_stats()
    print(f"📊 Total lookups: {stats['usage_count']}")
    print(f"📊 Database: {stats['total_diseases']} diseases, {stats['total_medicines']} medicines, {stats['total_departments']} departments")
    print("=" * 60 + "\n")
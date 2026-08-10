"""
Emergency Tool
==============
Provides emergency contact information, first aid guidance,
and critical procedures for medical emergencies.

Use Cases:
- Get emergency contact numbers
- First aid guidance
- Emergency procedures
- Trauma response protocols
- Poison control information

Author: Team A - Pratik
"""

import logging
from typing import Dict, Any, List
from langchain.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


# ============================================
# Emergency Contacts Database
# ============================================
EMERGENCY_CONTACTS = {
    "ambulance": {
        "number": "108",
        "alternative": "102",
        "description": "24/7 Emergency Medical Services",
        "response_time": "10-15 minutes (urban), 20-30 minutes (rural)"
    },
    "police": {
        "number": "100",
        "alternative": "112",
        "description": "Police emergency for accidents/violence",
        "response_time": "5-15 minutes"
    },
    "fire": {
        "number": "101",
        "alternative": "112",
        "description": "Fire brigade for fires, gas leaks, rescue",
        "response_time": "10-20 minutes"
    },
    "poison control": {
        "number": "1066",
        "alternative": "011-26588663",
        "description": "National Poison Information Centre (AIIMS)",
        "response_time": "Immediate phone consultation"
    },
    "women helpline": {
        "number": "181",
        "alternative": "1091",
        "description": "Women in distress",
        "response_time": "Immediate"
    },
    "child helpline": {
        "number": "1098",
        "alternative": "112",
        "description": "Child abuse and rescue",
        "response_time": "Immediate"
    },
    "national emergency": {
        "number": "112",
        "alternative": "",
        "description": "All-in-one emergency number (India)",
        "response_time": "Varies by service"
    },
    "mental health": {
        "number": "1800-599-0019",
        "alternative": "080-46110007",
        "description": "iCall - Mental Health Helpline",
        "response_time": "Immediate counseling"
    }
}

# ============================================
# First Aid Procedures
# ============================================
FIRST_AID_PROCEDURES = {
    "heart attack": {
        "priority": "🔴 CRITICAL - Call 108 immediately",
        "signs": ["Chest pain/pressure", "Arm/jaw pain", "Shortness of breath", "Cold sweat", "Nausea"],
        "steps": [
            "Call ambulance (108) IMMEDIATELY",
            "Have patient sit down and rest",
            "Loosen tight clothing",
            "Give aspirin 325mg to chew (if not allergic)",
            "If unconscious, begin CPR",
            "Stay with patient until help arrives"
        ],
        "avoid": ["DO NOT leave patient alone", "DO NOT give food/water", "DO NOT let them drive"]
    },
    "stroke": {
        "priority": "🔴 CRITICAL - Call 108 immediately",
        "signs": ["Face drooping", "Arm weakness", "Speech difficulty", "Sudden headache", "Vision problems"],
        "steps": [
            "Call ambulance (108) IMMEDIATELY - note the exact time",
            "Use FAST test: Face-Arms-Speech-Time",
            "Keep patient calm and still",
            "Lay them on side if unconscious",
            "Do NOT give food, water, or medication",
            "Record time symptoms started"
        ],
        "avoid": ["DO NOT give aspirin (could worsen bleeding stroke)", "DO NOT delay - every minute matters"]
    },
    "bleeding": {
        "priority": "🔴 HIGH - Call 108 for severe cases",
        "signs": ["Heavy blood flow", "Wound not clotting", "Blood soaking through cloth"],
        "steps": [
            "Wear gloves if available",
            "Apply DIRECT PRESSURE with clean cloth",
            "Elevate the wound above heart level",
            "Do NOT remove embedded objects",
            "Apply tourniquet only if limb bleeding won't stop",
            "Keep patient warm and calm"
        ],
        "avoid": ["DO NOT remove stuck objects", "DO NOT peek under bandage frequently"]
    },
    "burns": {
        "priority": "🟡 MODERATE to HIGH depending on severity",
        "signs": ["Redness (1st degree)", "Blisters (2nd degree)", "Charred skin (3rd degree)"],
        "steps": [
            "Remove from heat source",
            "Cool with COOL (not cold) water for 10-20 minutes",
            "Remove jewelry/tight clothing before swelling",
            "Cover with sterile non-stick dressing",
            "Do NOT apply ice, butter, or ointments",
            "Seek medical help for burns larger than 3 inches"
        ],
        "avoid": ["DO NOT use ice", "DO NOT apply butter/toothpaste", "DO NOT break blisters"]
    },
    "choking": {
        "priority": "🔴 CRITICAL - Immediate action needed",
        "signs": ["Unable to speak/cough", "Clutching throat", "Blue lips", "Loss of consciousness"],
        "steps": [
            "Ask 'Are you choking?' - if they can cough, encourage them",
            "If severe: Give 5 back blows between shoulder blades",
            "Perform Heimlich Maneuver (5 abdominal thrusts)",
            "Alternate 5 back blows and 5 thrusts",
            "If unconscious, start CPR",
            "Call 108 immediately"
        ],
        "avoid": ["DO NOT use finger sweep in adults", "DO NOT give water"]
    },
    "fracture": {
        "priority": "🟡 MODERATE - Seek medical help",
        "signs": ["Severe pain", "Swelling", "Deformity", "Inability to move", "Bone visible"],
        "steps": [
            "Do NOT move the injured area",
            "Immobilize with splint if possible",
            "Apply ice pack (wrapped in cloth)",
            "Elevate the injury if possible",
            "Cover open fractures with sterile cloth",
            "Transport to hospital immediately"
        ],
        "avoid": ["DO NOT try to straighten the bone", "DO NOT push protruding bone back"]
    },
    "poisoning": {
        "priority": "🔴 CRITICAL - Call Poison Control (1066)",
        "signs": ["Nausea", "Vomiting", "Confusion", "Difficulty breathing", "Unconsciousness"],
        "steps": [
            "Call Poison Control (1066) IMMEDIATELY",
            "Identify the substance if possible",
            "Save container/label for reference",
            "Do NOT induce vomiting unless told to",
            "If unconscious, place in recovery position",
            "Take patient and poison to hospital"
        ],
        "avoid": ["DO NOT induce vomiting", "DO NOT give water/milk without guidance"]
    },
    "unconscious": {
        "priority": "🔴 CRITICAL - Call 108",
        "signs": ["No response", "No breathing", "No pulse", "Pale/blue skin"],
        "steps": [
            "Call ambulance (108) IMMEDIATELY",
            "Check for breathing (10 seconds)",
            "Check pulse at neck",
            "If no breathing: Start CPR (30 compressions, 2 breaths)",
            "Continue CPR until help arrives",
            "If breathing: Place in recovery position"
        ],
        "avoid": ["DO NOT give food/water", "DO NOT leave alone", "DO NOT prop head with pillow"]
    }
}


class EmergencyTool(BaseTool):
    """
    Emergency response tool.
    Provides emergency contacts and first aid procedures.
    """
    
    name: str = "emergency"
    description: str = (
        "Useful for emergency medical situations including:\n"
        "- Emergency contact numbers (ambulance, police, fire, poison control)\n"
        "- First aid procedures (heart attack, stroke, bleeding, burns, etc.)\n"
        "- Critical response protocols\n"
        "- Life-threatening situation guidance\n"
        "Examples: 'ambulance number', 'first aid heart attack', 'emergency bleeding'"
    )
    
    # Track usage
    usage_count: int = Field(default=0)
    
    def _run(self, query: str) -> str:
        """Execute the emergency lookup."""
        try:
            self.usage_count += 1
            logger.warning(f"🚨 Emergency Tool called: {query}")
            
            query = query.strip().lower()
            
            # Check for first aid procedures
            for procedure in FIRST_AID_PROCEDURES:
                if procedure in query:
                    return self._get_first_aid(procedure)
            
            # Check for emergency contacts
            for contact_type in EMERGENCY_CONTACTS:
                if contact_type in query:
                    return self._get_contact(contact_type)
            
            # Check for keywords
            if "contact" in query or "number" in query or "call" in query or "phone" in query:
                return self._show_all_contacts()
            
            if "first aid" in query or "help" in query or "how to" in query:
                return self._show_all_procedures()
            
            # Emergency keywords - show all contacts
            emergency_words = ["emergency", "urgent", "critical", "help", "sos"]
            if any(word in query for word in emergency_words):
                return self._show_emergency_menu()
            
            return self._show_emergency_menu()
            
        except Exception as e:
            logger.error(f"❌ Emergency Tool error: {e}")
            return f"❌ Error: {str(e)}"
    
    def _get_contact(self, contact_type: str) -> str:
        """Get specific emergency contact."""
        info = EMERGENCY_CONTACTS.get(contact_type)
        if not info:
            return f"❌ Contact type '{contact_type}' not found"
        
        alt = f"\n   Alternative: {info['alternative']}" if info['alternative'] else ""
        
        return (
            f"🚨 EMERGENCY CONTACT: {contact_type.upper()}\n"
            f"{'=' * 50}\n"
            f"   📞 PRIMARY NUMBER: {info['number']}{alt}\n"
            f"   📝 Description: {info['description']}\n"
            f"   ⏱️  Response Time: {info['response_time']}\n"
            f"{'=' * 50}\n"
            f"   ⚠️ CALL IMMEDIATELY IF IN DANGER!"
        )
    
    def _get_first_aid(self, procedure: str) -> str:
        """Get first aid procedure."""
        info = FIRST_AID_PROCEDURES.get(procedure)
        if not info:
            return f"❌ Procedure '{procedure}' not found"
        
        signs_list = "\n     • ".join(info["signs"])
        steps_list = "\n     ".join([f"{i+1}. {step}" for i, step in enumerate(info["steps"])])
        avoid_list = "\n     ❌ ".join(info["avoid"])
        
        return (
            f"🚨 FIRST AID: {procedure.upper()}\n"
            f"{'=' * 60}\n"
            f"⚠️ PRIORITY: {info['priority']}\n\n"
            f"📋 SIGNS TO RECOGNIZE:\n     • {signs_list}\n\n"
            f"✅ IMMEDIATE STEPS:\n     {steps_list}\n\n"
            f"⛔ AVOID DOING:\n     ❌ {avoid_list}\n"
            f"{'=' * 60}\n"
            f"📞 CALL 108 IF SITUATION IS SEVERE!"
        )
    
    def _show_all_contacts(self) -> str:
        """Show all emergency contacts."""
        result = "🚨 EMERGENCY CONTACT NUMBERS (INDIA):\n" + "=" * 60 + "\n\n"
        
        for contact_type, info in EMERGENCY_CONTACTS.items():
            result += f"📞 {contact_type.upper()}\n"
            result += f"   Number: {info['number']}"
            if info['alternative']:
                result += f" | Alt: {info['alternative']}"
            result += f"\n   {info['description']}\n\n"
        
        result += "=" * 60 + "\n"
        result += "⚠️ SAVE THESE NUMBERS - THEY CAN SAVE LIVES!\n"
        result += "🆘 National Emergency: 112 (works for all services)"
        return result
    
    def _show_all_procedures(self) -> str:
        """Show all available first aid procedures."""
        procedures = ", ".join(FIRST_AID_PROCEDURES.keys())
        return (
            f"📋 AVAILABLE FIRST AID PROCEDURES:\n"
            f"{'=' * 60}\n"
            f"   {procedures}\n\n"
            f"💡 Ask like: 'first aid heart attack' or 'emergency bleeding'\n"
            f"📞 For immediate help, call 108 (Ambulance) or 112"
        )
    
    def _show_emergency_menu(self) -> str:
        """Show emergency menu with all options."""
        contacts = ", ".join(EMERGENCY_CONTACTS.keys())
        procedures = ", ".join(FIRST_AID_PROCEDURES.keys())
        
        return (
            f"🚨 EMERGENCY RESPONSE SYSTEM\n"
            f"{'=' * 60}\n\n"
            f"📞 QUICK CONTACTS:\n"
            f"   • Ambulance: 108\n"
            f"   • National Emergency: 112\n"
            f"   • Police: 100\n"
            f"   • Fire: 101\n"
            f"   • Poison Control: 1066\n\n"
            f"📋 AVAILABLE CONTACTS: {contacts}\n\n"
            f"🩹 AVAILABLE FIRST AID: {procedures}\n\n"
            f"💡 Ask like:\n"
            f"   • 'ambulance number'\n"
            f"   • 'first aid heart attack'\n"
            f"   • 'emergency bleeding'\n\n"
            f"{'=' * 60}\n"
            f"⚠️ IN EMERGENCY: CALL 112 (works for all services)"
        )
    
    async def _arun(self, query: str) -> str:
        """Async version"""
        return self._run(query)
    
    def get_stats(self) -> Dict[str, Any]:
        """Return tool usage statistics"""
        return {
            "tool_name": self.name,
            "usage_count": self.usage_count,
            "total_contacts": len(EMERGENCY_CONTACTS),
            "total_procedures": len(FIRST_AID_PROCEDURES)
        }


# ============================================
# Standalone Testing
# ============================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🚨 Emergency Tool - Test Suite")
    print("=" * 60 + "\n")
    
    emergency = EmergencyTool()
    
    test_cases = [
        "ambulance number",
        "poison control",
        "first aid heart attack",
        "first aid bleeding",
        "first aid choking",
        "emergency stroke",
        "all contacts",
        "help",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test}")
        result = emergency._run(test)
        print(f"{result}\n")
        print("-" * 60 + "\n")
    
    stats = emergency.get_stats()
    print(f"📊 Total emergency lookups: {stats['usage_count']}")
    print(f"📊 Database: {stats['total_contacts']} contacts, {stats['total_procedures']} procedures")
    print("=" * 60 + "\n")






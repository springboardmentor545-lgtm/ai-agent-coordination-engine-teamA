"""
DateTime Tool
=============
Handles all date and time related operations for medical scheduling.

Use Cases:
- Get current date/time
- Calculate appointment times
- Age calculation from DOB
- Days between dates
- Format dates for display

Author: Team A - Pratik
"""

import logging
import re
from datetime import datetime, timedelta, date
from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


class DateTimeTool(BaseTool):
    """
    DateTime tool for medical scheduling operations.
    Handles current time, date calculations, and appointment scheduling.
    """
    
    name: str = "datetime"
    description: str = (
        "Useful for date and time operations including:\n"
        "- Get current date and time\n"
        "- Calculate age from date of birth\n"
        "- Schedule appointments (add days/hours to current time)\n"
        "- Calculate days between two dates\n"
        "- Format dates for display\n"
        "Examples: 'current time', 'age 1995-05-15', 'appointment in 7 days'"
    )
    
    # Track usage
    usage_count: int = Field(default=0)
    
    def _run(self, query: str) -> str:
        """Execute the datetime operation."""
        try:
            self.usage_count += 1
            logger.info(f"📅 DateTime tool called with: {query}")
            
            query = query.strip().lower()
            
            # Route to appropriate method
            if "current" in query or "now" in query or "today" in query:
                return self._get_current_datetime()
            
            if "age" in query or "birthday" in query or "dob" in query:
                return self._calculate_age(query)
            
            if "appointment" in query or "schedule" in query or "in " in query:
                return self._schedule_appointment(query)
            
            if "between" in query or "difference" in query:
                return self._days_between(query)
            
            if "format" in query:
                return self._format_date(query)
            
            # Default: return current time
            return self._get_current_datetime()
            
        except Exception as e:
            logger.error(f"❌ DateTime error: {e}")
            return f"❌ Error: {str(e)}"
    
    def _get_current_datetime(self) -> str:
        """Get current date and time."""
        now = datetime.now()
        return (
            f"📅 Current Date & Time:\n"
            f"   Date: {now.strftime('%A, %B %d, %Y')}\n"
            f"   Time: {now.strftime('%I:%M:%S %p')}\n"
            f"   ISO Format: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"   Day of Year: {now.timetuple().tm_yday}\n"
            f"   Week: {now.isocalendar()[1]}"
        )
    
    def _calculate_age(self, query: str) -> str:
        """Calculate age from date of birth."""
        try:
            # Extract date pattern (YYYY-MM-DD or DD-MM-YYYY or DD/MM/YYYY)
            date_patterns = [
                r'(\d{4}-\d{1,2}-\d{1,2})',  # YYYY-MM-DD
                r'(\d{1,2}-\d{1,2}-\d{4})',  # DD-MM-YYYY
                r'(\d{1,2}/\d{1,2}/\d{4})',  # DD/MM/YYYY
            ]
            
            dob = None
            for pattern in date_patterns:
                match = re.search(pattern, query)
                if match:
                    date_str = match.group(1)
                    # Try different formats
                    for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']:
                        try:
                            dob = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    if dob:
                        break
            
            if not dob:
                return (
                    "❌ Please provide date of birth in format: YYYY-MM-DD\n"
                    "   Example: 'age 1995-05-15'"
                )
            
            today = date.today()
            age = today.year - dob.year
            
            # Adjust if birthday hasn't occurred this year
            if (today.month, today.day) < (dob.month, dob.day):
                age -= 1
            
            # Calculate days lived
            days_lived = (today - dob).days
            
            # Age category
            if age < 1:
                category = "👶 Infant"
            elif age < 13:
                category = "🧒 Child"
            elif age < 18:
                category = "👦 Teenager"
            elif age < 60:
                category = "👨 Adult"
            else:
                category = "👴 Senior"
            
            return (
                f"🎂 Age Calculation:\n"
                f"   Date of Birth: {dob.strftime('%B %d, %Y')}\n"
                f"   Current Date: {today.strftime('%B %d, %Y')}\n"
                f"   Age: {age} years\n"
                f"   Days Lived: {days_lived:,} days\n"
                f"   Category: {category}"
            )
            
        except Exception as e:
            return f"❌ Age calculation error: {str(e)}"
    
    def _schedule_appointment(self, query: str) -> str:
        """Schedule an appointment X days/hours from now."""
        try:
            # Extract number
            numbers = re.findall(r'\d+', query)
            if not numbers:
                return "❌ Please specify time. Example: 'appointment in 7 days' or 'schedule in 2 hours'"
            
            amount = int(numbers[0])
            now = datetime.now()
            
            # Determine unit
            if "hour" in query:
                appointment_time = now + timedelta(hours=amount)
                unit = "hour(s)"
            elif "minute" in query:
                appointment_time = now + timedelta(minutes=amount)
                unit = "minute(s)"
            elif "week" in query:
                appointment_time = now + timedelta(weeks=amount)
                unit = "week(s)"
            elif "month" in query:
                appointment_time = now + timedelta(days=amount * 30)
                unit = "month(s)"
            else:
                # Default: days
                appointment_time = now + timedelta(days=amount)
                unit = "day(s)"
            
            return (
                f"📅 Appointment Scheduled:\n"
                f"   Current Time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
                f"   Duration: {amount} {unit}\n"
                f"   Appointment: {appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
                f"   ISO: {appointment_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
        except Exception as e:
            return f"❌ Scheduling error: {str(e)}"
    
    def _days_between(self, query: str) -> str:
        """Calculate days between two dates."""
        try:
            date_pattern = r'(\d{4}-\d{1,2}-\d{1,2})'
            matches = re.findall(date_pattern, query)
            
            if len(matches) < 2:
                return (
                    "❌ Please provide 2 dates in format YYYY-MM-DD\n"
                    "   Example: 'days between 2024-01-01 and 2024-12-31'"
                )
            
            date1 = datetime.strptime(matches[0], '%Y-%m-%d').date()
            date2 = datetime.strptime(matches[1], '%Y-%m-%d').date()
            
            diff = abs((date2 - date1).days)
            weeks = diff // 7
            months = diff // 30
            
            return (
                f"📊 Days Between Dates:\n"
                f"   Date 1: {date1.strftime('%B %d, %Y')}\n"
                f"   Date 2: {date2.strftime('%B %d, %Y')}\n"
                f"   Days: {diff:,}\n"
                f"   Weeks: {weeks}\n"
                f"   Months: ~{months}"
            )
            
        except Exception as e:
            return f"❌ Date calculation error: {str(e)}"
    
    def _format_date(self, query: str) -> str:
        """Format a date in different styles."""
        try:
            date_pattern = r'(\d{4}-\d{1,2}-\d{1,2})'
            match = re.search(date_pattern, query)
            
            if not match:
                return "❌ Please provide date in YYYY-MM-DD format"
            
            dt = datetime.strptime(match.group(1), '%Y-%m-%d')
            
            return (
                f"📅 Date Formats:\n"
                f"   ISO Standard   : {dt.strftime('%Y-%m-%d')}\n"
                f"   US Format      : {dt.strftime('%m/%d/%Y')}\n"
                f"   European       : {dt.strftime('%d/%m/%Y')}\n"
                f"   Long Format    : {dt.strftime('%A, %B %d, %Y')}\n"
                f"   Short Format   : {dt.strftime('%b %d, %Y')}\n"
                f"   Medical Record : {dt.strftime('%Y%m%d')}"
            )
            
        except Exception as e:
            return f"❌ Format error: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version (required by BaseTool)"""
        return self._run(query)
    
    def get_stats(self) -> Dict[str, Any]:
        """Return tool usage statistics"""
        return {
            "tool_name": self.name,
            "usage_count": self.usage_count
        }


# ============================================
# Standalone Testing
# ============================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  📅 DateTime Tool - Test Suite")
    print("=" * 60 + "\n")
    
    dt_tool = DateTimeTool()
    
    test_cases = [
        "current time",
        "age 1995-05-15",
        "age 2010-12-25",
        "appointment in 7 days",
        "schedule in 2 hours",
        "appointment in 3 weeks",
        "days between 2024-01-01 and 2024-12-31",
        "format 2025-03-15"
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test}")
        result = dt_tool._run(test)
        print(f"{result}\n")
        print("-" * 60 + "\n")
    
    stats = dt_tool.get_stats()
    print(f"📊 Total operations: {stats['usage_count']}")
    print("=" * 60 + "\n")
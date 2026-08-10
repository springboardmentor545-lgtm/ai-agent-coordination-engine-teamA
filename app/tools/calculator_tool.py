"""
Calculator Tool
===============
Performs mathematical calculations for medical operations.

Use Cases:
- Medicine dosage calculations
- BMI calculation
- Body surface area (BSA)
- Fluid intake/output calculations
- Simple arithmetic

Author: Team A - Pratik
"""

import logging
import math
import re
from typing import Union, Dict, Any
from langchain.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


class CalculatorTool(BaseTool):
    """
    Calculator tool for mathematical operations in medical context.
    
    This tool safely evaluates mathematical expressions and provides
    medical-specific calculations like BMI, dosage, etc.
    """
    
    name: str = "calculator"
    description: str = (
        "Useful for mathematical calculations including:\n"
        "- Basic arithmetic (add, subtract, multiply, divide)\n"
        "- Medical dosage calculations\n"
        "- BMI (Body Mass Index) calculation\n"
        "- Percentage calculations\n"
        "Input should be a mathematical expression like '2 + 2' or 'bmi(70, 1.75)'"
    )
    
    # Track usage
    usage_count: int = Field(default=0)
    
    def _run(self, expression: str) -> str:
        """
        Execute the calculation.
        
        Args:
            expression: Mathematical expression or medical calculation
            
        Returns:
            Result as a string
        """
        try:
            self.usage_count += 1
            logger.info(f"🧮 Calculator called with: {expression}")
            
            # Clean the expression
            expression = expression.strip().lower()
            
            # Check for specific medical calculations
            if "bmi" in expression:
                return self._calculate_bmi(expression)
            
            if "dosage" in expression or "dose" in expression:
                return self._calculate_dosage(expression)
            
            if "percentage" in expression or "%" in expression:
                return self._calculate_percentage(expression)
            
            # Default: safe math evaluation
            return self._safe_calculate(expression)
            
        except Exception as e:
            logger.error(f"❌ Calculator error: {e}")
            return f"❌ Error in calculation: {str(e)}"
    
    def _safe_calculate(self, expression: str) -> str:
        """
        Safely evaluate mathematical expression.
        Only allows basic math operations for security.
        """
        # Remove common non-math words
        expression = expression.replace("what is", "").replace("calculate", "").strip()
        
        # Allow only safe characters (numbers, operators, spaces, parentheses, decimal)
        safe_chars = re.compile(r'^[0-9+\-*/().% \s]+$')
        
        if not safe_chars.match(expression):
            return "❌ Invalid expression. Only basic math operations are allowed."
        
        try:
            # Safe evaluation using eval with restricted globals
            result = eval(expression, {"__builtins__": {}}, {})
            return f"✅ Result: {expression} = {result}"
        except ZeroDivisionError:
            return "❌ Error: Cannot divide by zero"
        except Exception as e:
            return f"❌ Calculation error: {str(e)}"
    
    def _calculate_bmi(self, expression: str) -> str:
        """
        Calculate BMI (Body Mass Index).
        Formula: BMI = weight(kg) / height(m)²
        
        Expected input format: 'bmi(weight, height)' or 'bmi 70 1.75'
        """
        try:
            # Extract numbers from expression
            numbers = re.findall(r'\d+\.?\d*', expression)
            
            if len(numbers) < 2:
                return "❌ BMI needs 2 values: weight(kg) and height(m). Example: 'bmi(70, 1.75)'"
            
            weight = float(numbers[0])
            height = float(numbers[1])
            
            if height <= 0 or weight <= 0:
                return "❌ Weight and height must be positive numbers"
            
            # If height seems to be in cm, convert to m
            if height > 3:
                height = height / 100
                logger.info(f"Converted height from cm to m: {height}")
            
            bmi = weight / (height ** 2)
            
            # Determine category
            if bmi < 18.5:
                category = "Underweight"
                emoji = "⚠️"
            elif bmi < 25:
                category = "Normal weight"
                emoji = "✅"
            elif bmi < 30:
                category = "Overweight"
                emoji = "⚠️"
            else:
                category = "Obese"
                emoji = "🚨"
            
            return (
                f"📊 BMI Calculation:\n"
                f"   Weight: {weight} kg\n"
                f"   Height: {height} m\n"
                f"   BMI: {bmi:.2f}\n"
                f"   Category: {emoji} {category}"
            )
            
        except Exception as e:
            return f"❌ BMI calculation error: {str(e)}"
    
    def _calculate_dosage(self, expression: str) -> str:
        """
        Calculate medicine dosage based on weight.
        Formula: dosage = weight(kg) × dose_per_kg(mg)
        """
        try:
            numbers = re.findall(r'\d+\.?\d*', expression)
            
            if len(numbers) < 2:
                return (
                    "❌ Dosage calculation needs 2 values:\n"
                    "   1. Patient weight (kg)\n"
                    "   2. Dose per kg (mg)\n"
                    "   Example: 'dosage 70 10' for 70kg patient, 10mg/kg dose"
                )
            
            weight = float(numbers[0])
            dose_per_kg = float(numbers[1])
            
            if weight <= 0 or dose_per_kg <= 0:
                return "❌ Weight and dose must be positive numbers"
            
            total_dose = weight * dose_per_kg
            
            return (
                f"💊 Dosage Calculation:\n"
                f"   Patient Weight: {weight} kg\n"
                f"   Dose per kg: {dose_per_kg} mg/kg\n"
                f"   Total Dose: {total_dose} mg\n"
                f"   ⚠️ Always verify with a doctor before administration"
            )
            
        except Exception as e:
            return f"❌ Dosage calculation error: {str(e)}"
    
    def _calculate_percentage(self, expression: str) -> str:
        """Calculate percentage."""
        try:
            numbers = re.findall(r'\d+\.?\d*', expression)
            
            if len(numbers) < 2:
                return "❌ Percentage needs 2 values. Example: '20 percentage of 100'"
            
            value = float(numbers[0])
            total = float(numbers[1])
            
            if total == 0:
                return "❌ Total cannot be zero"
            
            # Determine calculation type
            if "of" in expression:
                # X% of Y
                result = (value / 100) * total
                return f"📊 {value}% of {total} = {result}"
            else:
                # What % is X of Y
                result = (value / total) * 100
                return f"📊 {value} is {result:.2f}% of {total}"
                
        except Exception as e:
            return f"❌ Percentage calculation error: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """Async version (required by BaseTool)"""
        return self._run(expression)
    
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
    print("  🧮 Calculator Tool - Test Suite")
    print("=" * 60 + "\n")
    
    calc = CalculatorTool()
    
    # Test cases
    test_cases = [
        "2 + 2",
        "100 * 5",
        "1000 / 8",
        "bmi(70, 1.75)",
        "bmi 65 170",  # cm should auto-convert
        "dosage 70 10",
        "20 percentage of 500",
        "15 percentage 200"
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test}")
        result = calc._run(test)
        print(f"{result}\n")
        print("-" * 60 + "\n")
    
    # Show stats
    stats = calc.get_stats()
    print(f"📊 Total calculations performed: {stats['usage_count']}")
    print("=" * 60 + "\n")
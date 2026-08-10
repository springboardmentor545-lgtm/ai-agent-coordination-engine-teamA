"""
Tools Package
=============
Contains all custom tools that AI agents can use.

Available Tools:
- CalculatorTool    : Mathematical calculations (dosage, BMI, etc.)
- DateTimeTool      : Date and time operations
- MedicalInfoTool   : Medical information lookup
- EmergencyTool     : Emergency contact information

Usage:
    from app.tools.calculator_tool import CalculatorTool
    calc = CalculatorTool()
    result = calc.run("2 + 2")
"""

__all__ = [
    "calculator_tool",
    "datetime_tool",
    "medical_info_tool",
    "emergency_tool"
]
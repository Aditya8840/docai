import json
from core.validator import DrivingLicense
import textwrap

def get_driving_license_prompt() -> str:
    schema = DrivingLicense.model_json_schema()
    properties = schema.get("properties", {})

    schema_with_descriptions = {
        field: details.get('description', '')
        for field, details in properties.items()
    }
    json_schema_str = json.dumps(schema_with_descriptions, indent=2)

    prompt = f"""
    ### ROLE & GOAL ###
    You are a highly intelligent and meticulous document processing specialist. Your primary function is to analyze images of driving licenses and extract key information with perfect accuracy. The output must be in a structured JSON format.

    ### IMPORTANT INSTRUCTIONS ###
    1.  **Strict Data Extraction**: Extract ONLY information that is explicitly and clearly visible on the document.
    2.  **Handle Missing/Illegible Data**: If any field is not present, unclear, or impossible to read, use `null` as the value.
    3.  **No Assumptions**: Never invent, guess, or infer information that isn't clearly present on the license.
    4.  **Date Formatting**: All dates must be in `MM/DD/YYYY` format (e.g., 01/15/1990, 12/31/2025).
    5.  **Name Extraction**: Extract the full name exactly as it appears, maintaining original capitalization and spacing.
    6.  **License Numbers**: Extract the complete license/ID number including all letters, numbers, and hyphens.
    7.  **JSON Output Only**: Return only a valid JSON object with no additional text, explanations, or markdown formatting.

    ### REQUIRED JSON STRUCTURE ###
    ```json
    {json_schema_str}
    ```

    ### EXAMPLE OUTPUT ###
    ```json
    {{
      "name": "JOHN MICHAEL SMITH",
      "date_of_birth": "03/15/1985",
      "license_number": "D1234567",
      "issuing_state": "CALIFORNIA",
      "expiry_date": "03/15/2029"
    }}
    ```

    ### TASK ###
    Analyze the driving license image carefully and return the extracted information in the exact JSON format specified above.
    """

    return textwrap.dedent(prompt).strip()

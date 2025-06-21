from core.validator import Resume
import json
import textwrap

def get_resume_prompt() -> str:
    schema = Resume.model_json_schema()
    properties = schema.get("properties", {})

    schema_with_descriptions = {
        field: details.get("description", "")
        for field, details in properties.items()
    }

    json_schema_str = json.dumps(schema_with_descriptions, indent=2)

    prompt = f"""
    ### ROLE & GOAL ###
    You are a highly intelligent and meticulous document processing specialist. Your primary function is to analyze images of resumes and extract key information with perfect accuracy. The output must be in a structured JSON format.

    ### IMPORTANT INSTRUCTIONS ###
    1.  **Strict Data Extraction**: Extract ONLY information that is explicitly and clearly visible on the resume.
    2.  **Handle Missing/Illegible Data**: If any field is not present, unclear, or impossible to read, use `null` as the value.
    3.  **No Assumptions**: Never invent, guess, or infer information that isn't clearly present on the resume.
    4.  **JSON Output Only**: Return only a valid JSON object with no additional text, explanations, or markdown formatting.

    ### REQUIRED JSON STRUCTURE ###
    ```json
    {json_schema_str}
    ```

    ### EXAMPLE OUTPUT ###
    ```json
    {{
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "skills": ["Python", "Machine Learning", "Data Analysis"],
        "work_experience": [
            {{
                "company": "Google",
                "role": "Software Engineer",
                "dates": "01/01/2020 - 01/01/2023"
            }}
        ],
        "education": [
            {{
                "institution": "University of California, Los Angeles",
                "degree": "Bachelor of Science in Computer Science",
                "graduation_year": "2020"
            }}
        ]
    }}
    ```

    ### TASK ###
    Analyze the resume image carefully and return the extracted information in the exact JSON format specified above.
    """

    return textwrap.dedent(prompt).strip()

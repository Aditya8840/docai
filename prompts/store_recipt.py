import json
from core.validator import ShopReceipt
import textwrap

def get_store_receipt_prompt() -> str:
    schema = ShopReceipt.model_json_schema()
    properties = schema.get("properties", {})

    schema_with_descriptions = {
        field: details.get("description", "")
        for field, details in properties.items()
    }
    json_schema_str = json.dumps(schema_with_descriptions, indent=2)

    prompt = f"""
    ### ROLE & GOAL ###
    You are a highly intelligent and meticulous document processing specialist. Your primary function is to analyze images of store receipts and extract key information with perfect accuracy. The output must be in a structured JSON format.

    ### IMPORTANT INSTRUCTIONS ###
    1.  **Strict Data Extraction**: Extract ONLY information that is explicitly and clearly visible on the receipt.
    2.  **Handle Missing/Illegible Data**: If any field is not present, unclear, or impossible to read, use `null` as the value.
    3.  **No Assumptions**: Never invent, guess, or infer information that isn't clearly present on the receipt.
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
        "MerchantName": "Walmart",
        "TotalAmount": 100.00,
        "LineItems": [
            {{
                "ItemName": "Apple",
                "Quantity": 1,
                "Price": 1.00
            }}
        ],
        "DateOfPurchase": "01/15/2025",
        "PaymentMethod": "Credit Card"
    }}
    ```

    ### TASK ###
    Analyze the store receipt image carefully and return the extracted information in the exact JSON format specified above.
    """

    return textwrap.dedent(prompt).strip()
"""JSON parsing utilities."""

import json


def parse_json_response(response_content: str) -> dict:
    # Remove markdown code block markers if present
    content = response_content.strip()
    
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
    elif content.startswith("```"):
        content = content[3:]   # Remove ```
        
    if content.endswith("```"):
        content = content[:-3]  # Remove trailing ```
    
    content = content.strip()
    print("Cleaned JSON content:", content)
    
    return json.loads(content)
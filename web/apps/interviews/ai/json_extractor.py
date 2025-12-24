import json
import re
from typing import Optional


class JsonExtractor:
    @staticmethod
    def extract_json(text: str) -> Optional[dict]:
        if not text:
            return None

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        try:
            json_loads = json.loads(match.group())
            return json_loads
        except json.JSONDecodeError:
            return None

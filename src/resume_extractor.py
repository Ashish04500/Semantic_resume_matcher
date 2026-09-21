import json
import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()


class ResumeExtractor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=api_key)

    def extract(self, resume_text: str) -> dict:

        prompt = f"""
Extract structured information from the following resume.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "skills": [],
    "titles": [],
    "employers": [],
    "total_years_experience": null,
    "education": [],
    "certifications": [],
    "location": null,
    "bullets": []
}}

Rules:
- Extract information only from the resume.
- Do not invent missing information.
- Use null when a single value is unavailable.
- Use [] when a list has no available information.
- Keep resume bullets as separate items.
- Extract technical and professional skills.
- Estimate total years of experience only when the resume provides enough evidence.
- Preserve the original meaning of the resume.

Resume:
{resume_text}
"""

        response = None

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt,
                )
                break

            except Exception as e:
                error_message = str(e)

                if "503" in error_message and attempt < 2:
                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying... ({attempt + 1}/2)"
                    )
                    time.sleep(5)
                else:
                    raise

        if response is None:
            raise ValueError("Gemini failed to return a response.")

        content = response.text

        if not content:
            raise ValueError("Gemini returned an empty response.")

        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:
            return json.loads(content)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Gemini returned invalid JSON:\n{content}"
            ) from e
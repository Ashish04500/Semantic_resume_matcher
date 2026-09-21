from pathlib import Path

from src.parser import extract_text
from src.matching.filtering import extract_years_from_text


class ResumeProcessor:

    def process_file(self, file_path: str) -> dict:

        path = Path(file_path)

        text = extract_text(
            str(path)
        )

        if not text.strip():
            raise ValueError(
                f"No text could be extracted "
                f"from: {path.name}"
            )

        return {
            "resume_id": path.stem,
            "filename": path.name,
            "raw_text": text,

            # Extract candidate experience from resume text.
            "structured_data": {
                "total_years_experience": extract_years_from_text(text)
            }
        }

    def process_files(
        self,
        file_paths: list[str]
    ) -> list[dict]:

        results = []

        for file_path in file_paths:

            try:

                result = self.process_file(
                    file_path
                )

                results.append(result)

            except Exception as e:

                results.append({
                    "resume_id":
                        Path(file_path).stem,

                    "filename":
                        Path(file_path).name,

                    "error":
                        str(e)
                })

        return results
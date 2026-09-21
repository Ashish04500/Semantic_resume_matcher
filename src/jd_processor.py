from pathlib import Path

from src.parser import extract_text
from src.jd_extractor import JDRequirementExtractor


class JDProcessor:

    def __init__(self):
        self.extractor = JDRequirementExtractor()

    def process_file(self, file_path: str) -> dict:

        path = Path(file_path)

        text = extract_text(
            str(path)
        )

        if not text.strip():
            raise ValueError(
                f"No text could be extracted: {path.name}"
            )

        requirements = (
            self.extractor.extract_requirements(
                text
            )
        )

        return {
            "job_id": path.stem,
            "filename": path.name,
            "raw_text": text,
            "requirements": requirements
        }

    def process_files(
        self,
        file_paths: list[str]
    ) -> list[dict]:

        results = []

        for file_path in file_paths:

            try:
                results.append(
                    self.process_file(file_path)
                )

            except Exception as e:

                results.append({
                    "job_id": Path(file_path).stem,
                    "filename": Path(file_path).name,
                    "error": str(e)
                })

        return results
import re


class TextChunker:

    def chunk(self, text: str) -> list[str]:

        if not text or not text.strip():
            return []

        lines = [
            self._clean_line(line)
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        chunks = []
        current = ""

        for line in lines:

            if self._is_heading(line):

                if current:
                    chunks.append(
                        current.strip()
                    )
                    current = ""

                continue

            if current:
                current += " " + line
            else:
                current = line

            if len(current) >= 300:

                chunks.append(
                    current.strip()
                )

                current = ""

        if current:
            chunks.append(
                current.strip()
            )

        return self._remove_duplicates(
            chunks
        )

    def _clean_line(self, line: str) -> str:

        line = line.strip()

        line = re.sub(
            r"^[•●▪◦*-]\s*",
            "",
            line
        )

        line = re.sub(
            r"^\d+[\.\)]\s*",
            "",
            line
        )

        return line.strip()

    def _is_heading(self, line: str) -> bool:

        if len(line) > 60:
            return False

        words = line.split()

        if len(words) > 6:
            return False

        common_sections = {
            "experience",
            "work experience",
            "professional experience",
            "education",
            "skills",
            "technical skills",
            "projects",
            "certifications",
            "achievements",
            "summary",
            "profile",
            "objective"
        }

        return line.lower() in common_sections

    def _remove_duplicates(
        self,
        chunks: list[str]
    ) -> list[str]:

        seen = set()
        result = []

        for chunk in chunks:

            normalized = re.sub(
                r"\s+",
                " ",
                chunk.lower()
            ).strip()

            if normalized not in seen:

                seen.add(normalized)
                result.append(chunk)

        return result
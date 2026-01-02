from omnidoc.core.document import Document, Section, Table


class MarkdownExtractor:
    """
    Production-grade Markdown extractor.

    Guarantees:
    - One section per heading
    - Clean separation of heading vs content
    - Semantic-chunk friendly structure
    """

    def extract(self, path: str) -> Document:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        sections: list[Section] = []
        buffer: list[str] = []
        current_heading: str | None = None
        page = 1

        def flush():
            nonlocal buffer, current_heading
            if not buffer:
                return

            text = "\n".join(buffer).strip()
            if text:
                sections.append(
                    Section(
                        page=page,
                        text=text
                    )
                )

            buffer = []

        for line in lines:
            line = line.rstrip()

            # -------------------------
            # Markdown heading detected
            # -------------------------
            if line.startswith("#"):
                flush()

                # Normalize heading
                current_heading = line.lstrip("#").strip()

                # Heading becomes its own section
                sections.append(
                    Section(
                        page=page,
                        text=current_heading
                    )
                )
                continue

            # -------------------------
            # Normal content
            # -------------------------
            if line.strip():
                buffer.append(line)

        flush()

        raw_text = "\n".join(sec.text for sec in sections)

        return Document(
            metadata={
                "file": path,
                "pages": 1,
                "type": "markdown",
            },
            sections=sections,
            tables=[],
            raw_text=raw_text,
        )

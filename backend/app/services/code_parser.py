from pathlib import Path

from app.schemas.code_file import CodeFile
from app.services.python_metadata_extractor import PythonMetadataExtractor


class CodeParser:

    LANGUAGE_MAP = {
        ".py": "Python",
        ".java": "Java",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "React",
        ".jsx": "React",
        ".html": "HTML",
        ".css": "CSS",
        ".json": "JSON",
        ".md": "Markdown",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".xml": "XML",
        ".sql": "SQL",
        ".properties": "Properties",
        ".txt": "Text",
    }

    def __init__(self):

        self.python_extractor = PythonMetadataExtractor()

    def parse_file(self, file_path: Path):

        try:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except Exception:
            content = ""

        language = self.LANGUAGE_MAP.get(
            file_path.suffix.lower(),
            "Unknown",
        )

        imports = []
        classes = []
        functions = []

        if language == "Python":

            metadata = self.python_extractor.extract(content)

            imports = metadata["imports"]
            classes = metadata["classes"]
            functions = metadata["functions"]

        return CodeFile(
            file_name=file_path.name,
            file_path=str(file_path),
            language=language,
            size=file_path.stat().st_size,
            line_count=len(content.splitlines()),
            content=content,
            imports=imports,
            classes=classes,
            functions=functions,
        )
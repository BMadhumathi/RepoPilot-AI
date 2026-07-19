from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py",
    ".java",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".json",
    ".md",
    ".xml",
    ".yaml",
    ".yml",
    ".sql",
    ".properties",
    ".txt",
}

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "__pycache__",
    "venv",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "target",
}


class FileScanner:

    def scan_repository(self, repo_path: Path):

        files = []

        for path in repo_path.rglob("*"):

            if not path.is_file():
                continue

            if any(part in IGNORED_DIRECTORIES for part in path.parts):
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            files.append(path)

        return files
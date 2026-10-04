from pathlib import Path

from app.core.config import settings
from app.core.logger import logger

from app.services.file_scanner import (
    FileScanner,
    SUPPORTED_EXTENSIONS,
    IGNORED_DIRECTORIES,
)


class CodeTools:

    def __init__(self):

        self.scanner = FileScanner()

        self.repositories_root = (
            settings.REPOSITORY_DIR.resolve()
        )

    def _get_repository_path(
        self,
        repository_name: str,
    ) -> Path:

        if not repository_name:

            raise ValueError(
                "Repository name cannot be empty."
            )

        repository_path = (
            self.repositories_root
            / repository_name
        ).resolve()

        try:

            repository_path.relative_to(
                self.repositories_root
            )

        except ValueError:

            raise ValueError(
                "Invalid repository path."
            )

        if not repository_path.exists():

            raise ValueError(
                f"Repository '{repository_name}' "
                "does not exist."
            )

        if not repository_path.is_dir():

            raise ValueError(
                "Repository path is not a directory."
            )

        return repository_path

    def _safe_file_path(
        self,
        repository_path: Path,
        file_path: str,
    ) -> Path:

        if not file_path:

            raise ValueError(
                "File path cannot be empty."
            )

        target = (
            repository_path
            / file_path
        ).resolve()

        try:

            target.relative_to(
                repository_path
            )

        except ValueError:

            raise ValueError(
                "Invalid file path."
            )

        if not target.exists():

            raise ValueError(
                f"File not found: {file_path}"
            )

        if not target.is_file():

            raise ValueError(
                f"Path is not a file: {file_path}"
            )

        return target

    def list_files(
        self,
        repository_name: str,
        directory: str = "",
    ) -> dict:

        logger.info(
            f"Code Agent tool: list_files "
            f"repository={repository_name} "
            f"directory={directory}"
        )

        repository_path = (
            self._get_repository_path(
                repository_name
            )
        )

        search_root = repository_path

        if directory:

            search_root = (
                repository_path
                / directory
            ).resolve()

            try:

                search_root.relative_to(
                    repository_path
                )

            except ValueError:

                raise ValueError(
                    "Invalid directory path."
                )

            if not search_root.exists():

                raise ValueError(
                    f"Directory not found: {directory}"
                )

            if not search_root.is_dir():

                raise ValueError(
                    f"Path is not a directory: {directory}"
                )

        files = []

        for path in search_root.rglob("*"):

            if not path.is_file():
                continue

            if any(
                part in IGNORED_DIRECTORIES
                for part in path.parts
            ):
                continue

            if (
                path.suffix.lower()
                not in SUPPORTED_EXTENSIONS
            ):
                continue

            relative_path = path.relative_to(
                repository_path
            )

            files.append(
                str(relative_path)
            )

        files.sort()

        return {
            "repository": repository_name,
            "directory": directory,
            "count": len(files),
            "files": files[:500],
        }

    def read_file(
        self,
        repository_name: str,
        file_path: str,
        start_line: int = 1,
        end_line: int = 200,
    ) -> dict:

        logger.info(
            f"Code Agent tool: read_file "
            f"repository={repository_name} "
            f"file={file_path} "
            f"lines={start_line}-{end_line}"
        )

        if start_line < 1:

            raise ValueError(
                "start_line must be at least 1."
            )

        if end_line < start_line:

            raise ValueError(
                "end_line must be greater than "
                "or equal to start_line."
            )

        if end_line - start_line > 500:

            raise ValueError(
                "A maximum of 500 lines can be "
                "read at once."
            )

        repository_path = (
            self._get_repository_path(
                repository_name
            )
        )

        target = self._safe_file_path(
            repository_path,
            file_path,
        )

        try:

            content = target.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            raise ValueError(
                "File is not a UTF-8 text file."
            )

        lines = content.splitlines()

        selected_lines = lines[
            start_line - 1:end_line
        ]

        numbered_lines = []

        for index, line in enumerate(
            selected_lines,
            start=start_line,
        ):

            numbered_lines.append(
                f"{index}: {line}"
            )

        return {
            "repository": repository_name,
            "file_path": file_path,
            "start_line": start_line,
            "end_line": min(
                end_line,
                len(lines),
            ),
            "total_lines": len(lines),
            "content": "\n".join(
                numbered_lines
            ),
        }

    def search_code(
        self,
        repository_name: str,
        query: str,
    ) -> dict:

        logger.info(
            f"Code Agent tool: search_code "
            f"repository={repository_name} "
            f"query={query}"
        )

        if not query or not query.strip():

            raise ValueError(
                "Search query cannot be empty."
            )

        repository_path = (
            self._get_repository_path(
                repository_name
            )
        )

        query_lower = query.lower()

        results = []

        files = self.scanner.scan_repository(
            repository_path
        )

        for file_path in files:

            try:

                content = file_path.read_text(
                    encoding="utf-8"
                )

            except (
                UnicodeDecodeError,
                OSError,
            ):

                continue

            for line_number, line in enumerate(
                content.splitlines(),
                start=1,
            ):

                if query_lower in line.lower():

                    results.append(
                        {
                            "file_path": str(
                                file_path.relative_to(
                                    repository_path
                                )
                            ),
                            "line": line_number,
                            "content": line.strip(),
                        }
                    )

                    if len(results) >= 50:

                        return {
                            "repository": repository_name,
                            "query": query,
                            "count": len(results),
                            "results": results,
                        }

        return {
            "repository": repository_name,
            "query": query,
            "count": len(results),
            "results": results,
        }
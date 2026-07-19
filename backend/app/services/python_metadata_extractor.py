import ast


class PythonMetadataExtractor:

    def extract(self, content: str):

        imports = []
        classes = []
        functions = []

        try:
            tree = ast.parse(content)
        except Exception:
            return {
                "imports": [],
                "classes": [],
                "functions": [],
            }

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                module = node.module or ""

                imports.append(module)

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return {
            "imports": imports,
            "classes": classes,
            "functions": functions,
        }
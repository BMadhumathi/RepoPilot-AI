import time

from google import genai
from google.genai import errors
from google.genai import types

from app.core.config import settings
from app.services.code_tools import CodeTools


class CodeAgent:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = "gemini-2.5-flash"

        self.tools = CodeTools()

        self.max_retries = 3

    def _generate(
        self,
        question: str,
        repository_name: str,
    ):

        system_instruction = f"""
You are RepoPilot Code Agent.

You are an AI software repository assistant.

Your job is to investigate the repository using
the tools available to you and answer the user's
question accurately.

Current repository:

{repository_name}

Available tools:

1. list_files
   Use this when you need to discover the repository
   structure or locate files.

2. read_file
   Use this when you need to inspect the actual
   contents of a specific file.

3. search_code
   Use this when you need to find where a class,
   function, variable, configuration, or text appears.

Rules:

1. Use tools when repository information is required.

2. Do not invent code or repository facts.

3. Do not claim to have inspected a file unless
   you actually used a tool to inspect it.

4. Prefer search_code when you do not know where
   something is located.

5. Use read_file when you need detailed context.

6. Use list_files when you need repository structure.

7. When answering, mention relevant file paths
   and line numbers whenever possible.

8. If the repository does not contain enough
   information, clearly say so.

9. Stay focused on the current repository.

10. Do not modify, delete, or execute repository
    files. You are a read-only Code Agent.
"""

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[
                self.tools.list_files,
                self.tools.read_file,
                self.tools.search_code,
            ],
        )

        for attempt in range(
            self.max_retries + 1
        ):

            try:

                return self.client.models.generate_content(
                    model=self.model,
                    contents=question,
                    config=config,
                )

            except errors.ServerError:

                if attempt >= self.max_retries:
                    raise

                delay = 2 ** attempt

                time.sleep(delay)

    def ask(
        self,
        question: str,
        repository_name: str,
    ):

        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        if (
            not repository_name
            or not repository_name.strip()
        ):

            raise ValueError(
                "Repository name cannot be empty."
            )

        response = self._generate(
            question=question,
            repository_name=repository_name,
        )

        return {
            "answer": response.text,
            "repository": repository_name,
        }
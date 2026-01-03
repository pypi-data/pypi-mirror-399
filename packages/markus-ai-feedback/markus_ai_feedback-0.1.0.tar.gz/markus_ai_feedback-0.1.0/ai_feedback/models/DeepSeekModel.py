import json
from pathlib import Path
from typing import Optional, Tuple

import ollama

from ..helpers.model_options_helpers import cast_to_type, ollama_option_schema
from .Model import Model


class DeepSeekModel(Model):

    def __init__(self) -> None:
        """
        Initializes the DeepSeekModel with model name and system instructions.
        """
        self.model = {"model": "deepseek-r1:70b"}

    def generate_response(
        self,
        prompt: str,
        submission_file: Path,
        system_instructions: str,
        model_options: Optional[dict] = None,
        question: Optional[str] = None,
        solution_file: Optional[Path] = None,
        test_output: Optional[Path] = None,
        scope: Optional[str] = None,
        llama_mode: Optional[str] = None,
        json_schema: Optional[str] = None,
    ) -> Optional[Tuple[str, str]]:
        """
        Generate a model response using the prompt and assignment files.

        Args:
            prompt (str): The input prompt provided by the user.
            submission_file (Optional[Path]): The path to the submission file.
            solution_file (Optional[Path]): The path to the solution file.
            test_output (Optional[Path]): The path to the test output file.
            scope (Optional[str]): The scope to use for generating the response.
            question (Optional[str]): An optional question to target specific content.
            system_instructions (str): instructions for the model
            llama_mode (Optional[str]): Optional mode to invoke llama.cpp in.
            json_schema (Optional[str]): Optional json schema to use.
            model_options (Optional[dict]): The optional model options to use for generating the response.

        Returns:
            Optional[Tuple[str, str]]: A tuple containing the prompt and the model's response,
                                       or None if the response was invalid.
        """
        if json_schema:
            schema_path = Path(json_schema)
            if not schema_path.exists():
                raise FileNotFoundError(f"JSON schema file not found: {schema_path}")
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
        else:
            schema = None

        model_options = cast_to_type(ollama_option_schema, model_options)

        response = ollama.chat(
            model=self.model["model"],
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt},
            ],
            format=schema['schema'] if schema else None,
            options=model_options if model_options else None,
        )

        if not response or "message" not in response or "content" not in response["message"]:
            print("Error: Invalid or empty response from Ollama.")
            return None

        return prompt, response["message"]["content"]

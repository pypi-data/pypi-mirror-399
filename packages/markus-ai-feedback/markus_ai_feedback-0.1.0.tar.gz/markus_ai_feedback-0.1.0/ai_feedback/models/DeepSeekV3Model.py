import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv

from .Model import Model

load_dotenv()
LLAMA_MODEL_PATH = os.getenv('LLAMA_MODEL_PATH', '')
LLAMA_CLI_PATH = os.getenv('LLAMA_CLI_PATH', '')
LLAMA_SERVER_URL = os.getenv('LLAMA_SERVER_URL', '').strip()
LLAMA_SERVER_URL = LLAMA_SERVER_URL if LLAMA_SERVER_URL and ":" in LLAMA_SERVER_URL else None
GPU_LAYERS = "40"


class DeepSeekV3Model(Model):
    def __init__(self):
        super().__init__()

    def generate_response(
        self,
        prompt: str,
        submission_file: Path,
        system_instructions: str,
        model_options: Optional[dict] = None,
        solution_file: Optional[Path] = None,
        scope: Optional[str] = None,
        question: Optional[str] = None,
        test_output: Optional[Path] = None,
        llama_mode: Optional[str] = None,
        json_schema: Optional[str] = None,
    ) -> Optional[Tuple[str, str]]:
        """
        Generate a model response using the prompt and assignment files.

        Args:
            prompt (str): The input prompt provided by the user.
            submission_file (Path): Path Object pointing to the submission file.
            solution_file (Path): Path Object pointing to the solution file.
            system_instructions (str): The system instructions provided by the user.
            scope (Optional[str]): Optional scope to use for this model.
            test_output (Optional[Path]): Path Object pointing to the test output file.
            llama_mode (Optional[str]): Optional mode to invoke llama.cpp in.
            question (Optional[str]): An optional question to target specific content.
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

        prompt = f"{system_instructions}\n{prompt}"
        if llama_mode == 'server':
            self._ensure_env_vars('LLAMA_SERVER_URL')
            response = self._get_response_server(prompt, model_options, schema)
        else:
            self._ensure_env_vars('LLAMA_MODEL_PATH', 'LLAMA_CLI_PATH')
            response = self._get_response_cli(prompt, model_options, schema)

        response = response.strip()

        # Remove end of response marker
        end_marker = "[end of text]"
        if response.endswith(end_marker):
            response = response[: -len(end_marker)]
            response = response.strip()

        return prompt, response

    def _ensure_env_vars(self, *names):
        """
        Ensure that each of the given variable names exists in globals() and is truthy.

        Args:
            *names (str): One or more names of environment‐variable strings to validate.

        Raises:
            RuntimeError: If any of the specified variables is missing or has a falsy value.
        """
        missing = [n for n in names if not globals().get(n)]
        if missing:
            raise RuntimeError(f"Error: Environment variable(s) {', '.join(missing)} not set")

    def _get_response_server(
        self, prompt: str, model_options: Optional[dict] = None, schema: Optional[dict] = None
    ) -> str:
        """
        Generate a model response using the prompt

        Args:
            prompt (str): The input prompt provided by the user.
            schema (Optional[dict]): Optional schema provided by the user.
            model_options (Optional[dict]): The optional model options to use for generating the response.

        Returns:
            str: A tuple containing the model response or None if the response was invalid.
        """
        url = f"{LLAMA_SERVER_URL}/v1/completions"

        payload = {"prompt": prompt, **model_options}

        if schema:
            raw_schema = schema.get("schema", schema)
            payload["json_schema"] = raw_schema

        try:
            response = requests.post(url, json=payload, timeout=3000)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"ERROR: Request to llama-server failed: {str(e)}")

        data = response.json()

        try:
            model_output = data["choices"][0]["text"]
        except (KeyError, IndexError):
            print("ERROR: Unexpected JSON format from llama-server:", data, file=sys.stderr, flush=True)
            model_output = ''

        return model_output

    def _get_response_cli(
        self, prompt: str, model_options: Optional[dict] = None, schema: Optional[dict] = None
    ) -> str:
        """
        Generate a model response using the prompt

        Args:
            prompt (str): The input prompt provided by the user.
            schema (Optional[dict]): Optional schema provided by the user.
            model_options (Optional[dict]): The optional model options to use for generating the response.

        Returns:
            str: The model response or None if the response was invalid.
        """
        # Need to add quotes to the prompt since prompts are multiline

        cmd = [
            LLAMA_CLI_PATH,
            "-m",
            LLAMA_MODEL_PATH,
            "--n-gpu-layers",
            GPU_LAYERS,
            "--single-turn",
            "--no-display-prompt",
        ]

        if schema:
            raw_schema = schema["schema"] if "schema" in schema else schema
            cmd += ["--json-schema", json.dumps(raw_schema)]

        for key, value in model_options.items():
            cmd += ["--" + key, value]

        try:
            completed = subprocess.run(
                cmd, input=prompt.encode(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300
            )
        except subprocess.TimeoutExpired as e:
            # If the process hangs for more than 5 minutes, print whatever has been captured so far
            print("ERROR: llama-cli timed out after 5 minutes.", file=sys.stdout, flush=True)
            print("Partial stdout:", e.stdout, file=sys.stdout, flush=True)
            print("Partial stderr:", e.stderr, file=sys.stdout, flush=True)
            raise
        except subprocess.CalledProcessError as e:
            # If llama-cli returns a non-zero exit code, print its stdout/stderr and re-raise
            print("ERROR: llama-cli returned non-zero exit code.", file=sys.stdout, flush=True)
            print("llama-cli stdout:", e.stdout, file=sys.stdout, flush=True)
            print("llama-cli stderr:", e.stderr, file=sys.stdout, flush=True)
            raise RuntimeError(f"llama.cpp failed (code {e.returncode}): {e.stderr.strip()}")

        # Decode with 'replace' so invalid UTF-8 bytes become U+FFFD
        return completed.stdout.decode('utf-8', errors='replace')

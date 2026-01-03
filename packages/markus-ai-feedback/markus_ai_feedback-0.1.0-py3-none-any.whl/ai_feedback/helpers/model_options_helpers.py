def str_to_bool(s: str) -> bool:
    return s.lower() in {"1", "true", "yes", "on"}


def parse_list(s: str) -> list:
    return [x.strip() for x in s.split(",") if x.strip()]


ollama_option_schema = {
    "temperature": float,
    "top_p": float,
    "top_k": int,
    "typical_p": float,
    "repeat_penalty": float,
    "presence_penalty": float,
    "frequency_penalty": float,
    "seed": int,
    "stop": parse_list,
    "num_predict": int,
    "num_keep": int,
    "num_ctx": int,
    "num_batch": int,
    "num_gpu": int,
    "main_gpu": int,
    "use_mmap": str_to_bool,
    "num_thread": int,
    "penalize_newline": str_to_bool,
    "mirostat": int,
    "mirostat_tau": float,
    "mirostat_eta": float,
}

openai_chat_option_schema = {
    "temperature": float,
    "top_p": float,
    "n": int,
    "stream": bool,
    "stop": lambda s: s.split(",") if isinstance(s, str) else s,
    "max_tokens": int,
    "presence_penalty": float,
    "frequency_penalty": float,
    "logit_bias": dict,
    "user": str,
    "seed": int,
    "tools": list,
    "tool_choice": str,
    "response_format": str,
}

claude_option_schema = {
    "max_tokens": int,
    "temperature": float,
    "top_p": float,
    "stop_sequences": parse_list,
    "metadata": dict,
    "tools": list,
    "tool_choice": str,
    "stream": str_to_bool,
}


def cast_to_type(option_schema=dict, model_options=dict):
    """given the option schema casts the values of hyperparams into their respective types"""
    options = {}
    for key, value in model_options.items():
        try:
            if key in option_schema:
                options[key] = option_schema[key](value)
            else:
                options[key] = value
        except Exception as e:
            print(f"Warning: Failed to process model option '{key}' with value '{value}': {e}")
            exit(1)
    return options

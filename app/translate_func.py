from pathlib import Path

import requests


def generate_prompt(prompt_param: str, from_lang_name: str, to_lang_name: str, from_lang_code, to_lang_code,
                    postfix_param: str, prompt_no_think_postfix_param: bool, context: str) -> str:
    prompt = (prompt_param.replace("%%from_lang%%", from_lang_name).replace("%%to_lang%%", to_lang_name)
              .replace("%%from_lang_code%%", from_lang_code).replace("%%to_lang_code%%", to_lang_code))

    if context and len(context.strip()) > 0:
        prompt = prompt.replace("%%context_prompt%%", context)
    else:
        prompt = prompt.replace("%%context_prompt%%", "")

    postfix = get_prompt_postfix(postfix_param, prompt_no_think_postfix_param)

    return prompt + postfix


def get_prompt_postfix(postfix_param: str, prompt_no_think_postfix_param: bool) -> str:
    return postfix_param + " /no_think" if prompt_no_think_postfix_param else ""


def get_open_ai_request(prompt: str, text: str, max_tokens_multiplier: int) -> dict:
    # max_tokens - Sometimes model can "breaks" and generate tokens indefinitely. This parameter limits generation.
    return {
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.0,
        "max_tokens": len(text) * max_tokens_multiplier
    }


def post_request(req: dict, url: str):
    response = requests.post(url, json=req)

    if response.status_code != 200:
        raise ValueError("Response status {0} for request by url {1}".format(response.status_code, url))

    return response.json()


def remove_think_text(text: str) -> str:
    return text.replace("<think>\n\n</think>\n\n", "").strip()


def get_prompt_param_with_external_prompt_support(prompt_param: str) -> str:
    if prompt_param:
        prompt_param_lower = prompt_param.lower()
        if prompt_param_lower.endswith(".json") or prompt_param_lower.endswith(".txt"):
            current_dir: Path = Path(__file__).parent.absolute()
            json_path = current_dir / ".." / "external_prompt" / prompt_param_lower
            if Path.exists(json_path):
                return json_path.read_text()
            else:
                raise ValueError(f'Expected json file in path "{json_path}"')

    return prompt_param

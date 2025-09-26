import requests


def generate_prompt(prompt_param: str, from_lang_name: str, to_lang_name: str,
                    postfix_param: str, prompt_no_think_postfix_param: bool, context: str) -> str:
    prompt = prompt_param.replace("%%from_lang%%", from_lang_name).replace("%%to_lang%%", to_lang_name)
    if context and len(context.strip()) > 0:
        prompt = prompt.replace("%%context%%", context)
    else:
        prompt = prompt.replace("%%context%%", "")

    postfix = get_prompt_postfix(postfix_param, prompt_no_think_postfix_param)

    return prompt + postfix


def get_prompt_postfix(postfix_param: str, prompt_no_think_postfix_param: bool) -> str:
    return postfix_param + " /no_think" if prompt_no_think_postfix_param else ""


def get_open_ai_request(prompt: str, text: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.0
    }


def post_request(req: dict, url: str):
    response = requests.post(url, json=req)

    if response.status_code != 200:
        raise ValueError("Response status {0} for request by url {1}".format(response.status_code, url))

    return response.json()


def remove_think_text(text: str) -> str:
    return text.replace("<think>\n\n</think>\n\n", "").strip()

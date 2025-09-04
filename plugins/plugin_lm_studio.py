import os

import lmstudio
import requests
from lmstudio import LLM, LlmPredictionConfig
from tqdm import tqdm

from app import params
from app.app_core import AppCore
from app.dto import TranslatePluginInitInfo, TranslateStruct
from app.lang_dict import get_lang_by_2_chars_code

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname


def start(core: AppCore):
    manifest = {
        "name": "LM-Studio Translator",  # name
        "version": "1.0",  # version

        "default_options": {
            "custom_url": "http://localhost:1234",  #
            "prompt": "You are professional translator. Translate text from {0} to {1}. Don't add any notes or any additional info in your answer, write only translate. Text: ",
            "prompt_postfix": "",
            "use_library_for_request": True,
        },

        "translate": {
            "lm_studio": (init, translate)  # 1 function - init, 2 - translate
        }
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    params.read_plugin_translate_params(manifest)
    pass


def init(core: AppCore) -> TranslatePluginInitInfo:
    options = core.plugin_options(plugin_name)
    custom_url: str = options['custom_url']
    use_library_for_request = options["use_library_for_request"]
    if use_library_for_request:
        lmstudio.configure_default_client(custom_url.replace("http://", ""))
        loaded_models = lmstudio.list_loaded_models("llm")
        if len(loaded_models) > 0:
            return TranslatePluginInitInfo(plugin_name=plugin_name, model_name=loaded_models[0].identifier)
        else:
            raise ValueError('List loaded models is empty. Please load model before init this plugin')
    else:
        prompt = "You are assistant. " + options["prompt_postfix"]
        model = http_request(custom_url, prompt, "init")["model"]
        return TranslatePluginInitInfo(plugin_name=plugin_name, model_name=model)


def translate(core: AppCore, ts: TranslateStruct) -> TranslateStruct:
    options = core.plugin_options(plugin_name)

    from_lang_name = get_lang_by_2_chars_code(ts.req.from_lang)
    to_lang_name = get_lang_by_2_chars_code(ts.req.to_lang)

    prompt = options["prompt"].format(from_lang_name, to_lang_name) + options["prompt_postfix"]
    use_library_for_request = options["use_library_for_request"]

    model: LLM
    if use_library_for_request:
        model = lmstudio.llm()

    for part in tqdm(ts.parts, unit=params.tp.unit, ascii=params.tp.ascii, desc=params.tp.desc):
        if part.need_to_translate():
            content: str
            if use_library_for_request:
                content = library_request(model, prompt, part.text)
            else:
                content = http_request_content(options['custom_url'], prompt, part.text)

            part.translate = content.replace("<think>\n\n</think>\n\n", "").strip()

    return ts


def library_request(model: LLM, prompt: str, text: str) -> str:
    chat = lmstudio.Chat(prompt)
    chat.add_user_message(text)
    result = model.respond(chat, config=LlmPredictionConfig(temperature=0.0))

    return result.content


# API request
def http_request(base_url: str, prompt: str, text: str) -> dict:
    req = {
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.0
    }
    response = requests.post(base_url + "/v1/chat/completions", json=req)

    if response.status_code != 200:
        raise ValueError("Response status {0} for request by url {1}".format(response.status_code, base_url))

    return response.json()


def http_request_content(url: str, prompt: str, text: str) -> str:
    return http_request(url, prompt, text)["choices"][0]['message']['content']

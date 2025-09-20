import os

import requests
from tqdm import tqdm

from app import params, translate_func, log
from app.app_core import AppCore
from app.dto import TranslatePluginInitInfo, TranslateStruct
from app.lang_dict import get_lang_by_2_chars_code

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname
logger = log.logger()


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "KoboldCpp Translator",  # name
        "version": "1.0",  # version

        "default_options": {
            "custom_url": "http://127.0.0.1:5001",  #
            "prompt": "You are professional translator. Translate text from %%from_lang%% to %%to_lang%%. Don't add any notes or any additional info in your answer, write only translate. Text: ",
            "prompt_postfix": "",
            "prompt_no_think_postfix": False,
        },
        "translate": {
            "kobold_cpp": (init, translate)  # 1 function - init, 2 - translate
        }
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    params.read_plugin_translate_params(manifest)
    pass


def init(core: AppCore) -> TranslatePluginInitInfo:
    options = core.plugin_options(plugin_name)

    url_model = options['custom_url'] + "/api/v1/model"
    response_model = get_json_resp(url_model)

    return TranslatePluginInitInfo(plugin_name=plugin_name, model_name=response_model["result"])


def translate(core: AppCore, ts: TranslateStruct):
    options = core.plugin_options(plugin_name)

    from_lang_name: str = get_lang_by_2_chars_code(ts.req.from_lang)
    to_lang_name: str = get_lang_by_2_chars_code(ts.req.to_lang)

    prompt = translate_func.generate_prompt(options["prompt"], from_lang_name, to_lang_name,
                                            options["prompt_postfix"], options['prompt_no_think_postfix'])

    for part in tqdm(ts.parts, unit=params.tp.unit, ascii=params.tp.ascii, desc=params.tp.desc):
        if part.need_to_translate():
            req = translate_func.get_open_ai_request(prompt, part.text)
            req["model"] = "kcpp"

            resp = translate_func.post_request(req, options['custom_url'] + "/v1/chat/completions")

            content = resp["choices"][0]['message']['content']
            if resp["choices"][0]["finish_reason"] == "length":
                logger.warn("Translate text %s interrupted by max response length.", part.text)
            part.translate = translate_func.remove_think_text(content)

    return ts


def get_json_resp(url: str) -> dict:
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f'Response status {response.status_code} for KoboldCpp request by url {url}')

    return response.json()
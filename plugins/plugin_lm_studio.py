import os

import requests
from tqdm import tqdm

from app import struct
from app.app_core import AppCore
from app.lang_dict import get_lang_by_2_chars_code
from app.struct import TranslateStruct, tp

modname = os.path.basename(__file__)[:-3]  # calculating modname


# start function
def start(core: AppCore):
    manifest = {
        "name": "LM-Studio Translator",  # name
        "version": "1.0",  # version

        "default_options": {
            "custom_url": "http://localhost:1234",  #
            "prompt": "You are professional translator. Translate text from {0} to {1}. Don't add any notes or any additional info in your answer, write only translate. Text: ",
            "prompt_postfix": ""
        },

        "translate": {
            "lm_studio": (init, translate)  # 1 function - init, 2 - translate
        }
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    struct.read_plugin_params(manifest)
    pass


def init(core: AppCore):
    return modname


def translate(core: AppCore, ts: TranslateStruct):
    options = core.plugin_options(modname)

    from_lang_name = get_lang_by_2_chars_code(ts.req.from_lang)
    to_lang_name = get_lang_by_2_chars_code(ts.req.to_lang)

    prompt = options["prompt"].format(from_lang_name, to_lang_name)
    url = options['custom_url'] + "/v1/chat/completions"

    for part in tqdm(ts.parts, unit=tp.unit, ascii=tp.ascii, desc=tp.desc):
        if part.need_to_translate():
            req = {
                "messages": [
                    {"role": "system", "content": prompt + options["prompt_postfix"]},
                    {"role": "user", "content": part.text}
                ],
                "temperature": 0.0
            }

            response = requests.post(url, json=req)

            if response.status_code != 200:
                raise ValueError("Response status {0} for request by url {1}".format(response.status_code, url))

            content: str = response.json()["choices"][0]['message']['content']
            part.translate = content.replace("<think>\n\n</think>\n\n", "").strip()

    return ts

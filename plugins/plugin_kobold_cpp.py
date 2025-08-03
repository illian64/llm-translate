import os

import requests
from tqdm import tqdm

from app import struct
from app.app_core import AppCore
from app.lang_dict import get_lang_by_2_chars_code
from app.struct import TranslateStruct, tp, ModelInitInfo

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname


# start function
def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "KoboldCpp Translator",  # name
        "version": "1.0",  # version

        "default_options": {
            "custom_url": "http://127.0.0.1:5001",  #
            "prompt": "\n### Instruction:\nYou are professional translator. Translate this text from {0} to {1}. Don't add any notes or any additional info in your answer, write only translate. Text: {2}\n### Response:\n"
        },
        "translate": {
            "kobold_cpp": (init, translate)  # 1 function - init, 2 - translate
        }
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    struct.read_plugin_params(manifest)
    pass


def init(core: AppCore) -> ModelInitInfo:
    options = core.plugin_options(plugin_name)
    url = options['custom_url'] + "/api/v1/model"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f'Response status {response.status_code} for request by url {url}')

    return ModelInitInfo(plugin_name=plugin_name, model_name=response.json()["result"])


def translate(core: AppCore, ts: TranslateStruct):
    options = core.plugin_options(plugin_name)

    from_lang_name = get_lang_by_2_chars_code(ts.req.from_lang)
    to_lang_name = get_lang_by_2_chars_code(ts.req.to_lang)

    # prompt = options["prompt"].format(from_lang_name, to_lang_name)
    url = options['custom_url'] + "/api/v1/generate"

    for part in tqdm(ts.parts, unit=tp.unit, ascii=tp.ascii, desc=tp.desc):
        if part.need_to_translate():
            prompt = options["prompt"].format(from_lang_name, to_lang_name, part.text)
            length: int
            min_length = 512
            if len(part.text) * 2 < min_length:
                length = min_length
            else:
                length = len(part.text) * 2
            req = {
                "n": 1,
                "max_context_length": 4096,
                "max_length": length,
                "rep_pen": 1.07,
                "temperature": 0.01,
                "top_p": 0.92,
                "top_k": 100,
                "top_a": 0,
                "typical": 1,
                "tfs": 1,
                "rep_pen_range": 360,
                "rep_pen_slope": 0.7,
                "sampler_order": [6,0,1,3,4,2,5],
                "memory": "",
                "trim_stop": True,
                "genkey": "KCPP9747",
                "min_p": 0,
                "dynatemp_range": 0,
                "dynatemp_exponent": 1,
                "smoothing_factor": 0,
                "nsigma": 0,
                "banned_tokens": [],
                "render_special": False,
                "logprobs": False,
                "presence_penalty": 0,
                "logit_bias": {},
                "prompt": prompt,
                "quiet": True,
                "stop_sequence": ["### Instruction:", "### Response:"],
                "use_default_badwordsids": False,
                "bypass_eos": False
            }

            response = requests.post(url, json=req)

            if response.status_code != 200:
                raise ValueError(f'Response status {response.status_code} for request by url {url}')

            content: str = response.json()["results"][0]['text']
            part.translate = content.strip()

    return ts

# nllb plugin
# author: Vladislav Janvarev

# from https://github.com/facebookresearch/fairseq/tree/nllb
import os

from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app import struct, cuda
from app.app_core import AppCore
from app.lang_dict import lang_2_chars_to_nllb_lang
from app.struct import TranslateStruct, tp

modname = os.path.basename(__file__)[:-3]  # calculating modname

model = None
tokenizers:dict = {}


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "NLLB 200 Translate",  # name
        "version": "1.0",  # version

        "translate": {
            "nllb_200": (init, translate)  # 1 function - init, 2 - translate
        },

        "default_options": {
            "model": "facebook/nllb-200-distilled-600M",  # key model
            "cuda": True,
            "cuda_device_index": 0,

            "text_split_params": {
                "split_by_sentences_only": True,
            }
        },
    }
    return manifest


def start_with_options(core: AppCore, manifest: dict):
    struct.read_plugin_params(manifest)

    return manifest


def init(core: AppCore):
    options = core.plugin_options(modname)

    global model
    model = AutoModelForSeq2SeqLM.from_pretrained(options["model"]).to(cuda.get_device_with_gpu_num(options))

    return modname


def translate(core: AppCore, ts: TranslateStruct):
    options = core.plugin_options(modname)

    from_lang = lang_2_chars_to_nllb_lang[ts.req.from_lang]
    to_lang = lang_2_chars_to_nllb_lang[ts.req.to_lang]
    cuda_device = cuda.get_device_with_gpu_num(options)

    if tokenizers.get(from_lang) is None:
        tokenizers[from_lang] = AutoTokenizer.from_pretrained(options["model"], src_lang=from_lang)
    tokenizer = tokenizers[from_lang]

    for part in tqdm(ts.parts, unit=tp.unit, ascii=tp.ascii, desc=tp.desc):
        if part.need_to_translate():
            inputs = tokenizer(part.text, return_tensors="pt").to(cuda_device)

            translated_tokens = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(to_lang),
                max_length=int(len(part.text) * 5)
            )
            decoded = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            part.translate = decoded

    return ts

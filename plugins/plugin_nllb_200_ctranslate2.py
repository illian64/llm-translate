import os

import ctranslate2
from ctranslate2 import Translator
from tqdm import tqdm
from transformers import AutoTokenizer

from app import cuda, struct
from app.app_core import AppCore
from app.lang_dict import lang_2_chars_to_nllb_lang
from app.struct import TranslateStruct, tp, ModelInitInfo

plugin_name = os.path.basename(__file__)[:-3]

model: Translator
tokenizers:dict = {}


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "NLLB 200 CTranslate2",  # name
        "version": "1.0",  # version

        "translate": {
            "nllb_200_ctranslate2": (init, translate)  # 1 function - init, 2 - translate
        },

        "default_options": {
            "model": "models/nllb-200-3.3B-ct2-float16",  # model
            "compute_type": "bfloat16",
            "cuda": True,  # false if you want to run on CPU, true - if on CUDA
            "cuda_device_index": 0,  # GPU index (if you have more than one GPU)
            "max_batch_size": 16,

            "text_split_params": {
                "split_by_sentences_only": True,
            }
        },
    }

    return manifest


def start_with_options(core: AppCore, manifest:dict):
    struct.read_plugin_params(manifest)

    return manifest


def init(core:AppCore) -> ModelInitInfo:
    options = core.plugin_options(plugin_name)

    global model

    model = ctranslate2.Translator(options["model"], compute_type=options["compute_type"],
                                   device=cuda.get_device(options), device_index=options["cuda_device_index"])

    return ModelInitInfo(plugin_name=plugin_name, model_name=f'{options["model"]}__{options["compute_type"]}')


def translate(core: AppCore, ts: TranslateStruct):
    options = core.plugin_options(plugin_name)

    from_lang = lang_2_chars_to_nllb_lang[ts.req.from_lang]
    to_lang = lang_2_chars_to_nllb_lang[ts.req.to_lang]
    if tokenizers.get(from_lang) is None:
        tokenizers[from_lang] = AutoTokenizer.from_pretrained(options["model"], src_lang=from_lang)
    tokenizer = tokenizers[from_lang]

    # translate_batch not optimal, but there are problems with try to implement batch processing like madlab_ctranslate2
    for part in tqdm(ts.parts, unit=tp.unit, ascii=tp.ascii, desc=tp.desc):
        if part.need_to_translate():
            input_text = part.text
            tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(input_text))

            translate_results = model.translate_batch(
                [tokens], max_batch_size=options["max_batch_size"], beam_size=1, return_scores=False, disable_unk=False,
                target_prefix=[[to_lang]], batch_type="tokens"
            )
            output_tokens = translate_results[0].hypotheses[0]
            decoded_text = tokenizer.decode(tokenizer.convert_tokens_to_ids(output_tokens))
            if to_lang in decoded_text:
                decoded_text = decoded_text.replace(to_lang, "").lstrip()
            part.translate = decoded_text

    return ts

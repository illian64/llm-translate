import os

import ctranslate2
import transformers
from ctranslate2 import Translator
from tqdm import tqdm
from transformers import PreTrainedTokenizerBase

from app import cuda, params
from app.app_core import AppCore
from app.dto import TranslatePluginInitInfo, TranslateStruct

plugin_name = os.path.basename(__file__)[:-3]

model: Translator
tokenizer: PreTrainedTokenizerBase


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "Madlab CTranslate2",  # name
        "version": "1.0",  # version

        "translate": {
            "madlad_400_ctranslate2": (init, translate)  # 1 function - init, 2 - translate
        },

        "default_options": {
            "model": "models/madlad400-10b-mt-ct2-bfloat16",  # key model
            "tokenizer": "models/madlad400-10b-mt-ct2-bfloat16",  # transformers.AutoTokenizer
            "compute_type": "bfloat16",
            "cuda": True,  # false if you want to run on CPU, true - if on CUDA
            "cuda_device_index": 0,  # GPU index (if you have more than one GPU)
            "max_batch_size": 16,  # batch processing requests, increase need to more memory

            "text_split_params": {
                "split_by_sentences_only": True,
            }
        },
    }

    return manifest


def start_with_options(core: AppCore, manifest:dict):
    params.read_plugin_translate_params(manifest)

    return manifest


def init(core:AppCore) -> TranslatePluginInitInfo:
    options = core.plugin_options(plugin_name)

    global model
    global tokenizer

    model = ctranslate2.Translator(options["model"], compute_type=options["compute_type"],
                                   device=cuda.get_device(options), device_index=options["cuda_device_index"])
    tokenizer = transformers.AutoTokenizer.from_pretrained(options["tokenizer"])

    return TranslatePluginInitInfo(plugin_name=plugin_name, model_name=f'{options["model"]}__{options["compute_type"]}')


def translate(core: AppCore, ts: TranslateStruct):
    options = core.plugin_options(plugin_name)

    # # implementation 1: one part - one batch
    # for part in ts.parts:
    #     if not part.text or part.text == "":
    #         part.translate = ""
    #     else:
    #         input_text = "<2" + ts.req.to_lang + ">" + part.text
    #         tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(input_text))
    #         translate_results = model.translate_batch([tokens])
    #         output_tokens = translate_results[0].hypotheses[0]
    #         decoded_text = tokenizer.decode(tokenizer.convert_tokens_to_ids(output_tokens))
    #         part.translate = decoded_text

    # implementation 2: all parts - one batch. It's faster, but depends on amount of batches.
    tokens_list = []
    for part in tqdm(ts.parts, unit=params.tp.unit, ascii=params.tp.ascii, desc=params.tp.desc):
        if part.need_to_translate():
            input_text = "<2" + ts.req.to_lang + ">" + part.text
            tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(input_text))
            tokens_list.append(tokens)

    translate_results = model.translate_batch(
        tokens_list, max_batch_size=options["max_batch_size"], beam_size=1, return_scores=False, disable_unk=False)

    i = 0
    for part in ts.parts:
        if part.text and part.text != "":
            output_tokens = translate_results[i].hypotheses[0]
            decoded_text = tokenizer.decode(tokenizer.convert_tokens_to_ids(output_tokens))
            part.translate = decoded_text
            i += 1
        else:
            part.translate = ""

    return ts

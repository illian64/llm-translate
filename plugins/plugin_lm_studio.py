import os

import lmstudio
from lmstudio import LLM, LlmPredictionConfig
from tqdm import tqdm

from app import params, translate_func
from app.app_core import AppCore
from app.dto import TranslatePluginInitInfo, TranslateStruct
from app.lang_dict import get_lang_by_2_chars_code

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname
llm_model: LLM | None = None
model_name: str = ""


def start(core: AppCore):
    manifest = {
        "name": "LM-Studio Translator",  # name
        "version": "1.0",  # version

        "default_options": {
            "custom_url": "http://localhost:1234",  #
            "prompt": "You are a professional translator. Your task is to translate a text (or word) provided below from %%from_lang%% to %%to_lang%%.\n%%context_prompt%%\nINSTRUCTION:Carefully analyze the context. Pay special attention to Terminology, Style, Consistency. Provide only the translation. Do not include any additional information, explanations, notes, or comments in your response. The output should be the pure translated text only.\nTEXT TO TRANSLATE:",
            "prompt_postfix": "",
            "prompt_no_think_postfix": False,
            "use_library_for_request": True,
            "special_prompt_for_model": {
                "my_model_name": "special prompt"
            },
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

    global model_name
    if use_library_for_request:
        lmstudio.configure_default_client(custom_url.replace("http://", ""))
        loaded_models = lmstudio.list_loaded_models("llm")
        if len(loaded_models) > 0:
            model_name = loaded_models[0].identifier

            global llm_model
            llm_model = lmstudio.llm(model_name)
        else:
            raise ValueError('List loaded models is empty. Please load model before init this plugin')
    else:
        postfix = translate_func.get_prompt_postfix(options["prompt_postfix"], options['prompt_no_think_postfix'])
        prompt = "You are assistant. " + postfix
        req = translate_func.get_open_ai_request(prompt, "init")
        resp = translate_func.post_request(req, options['custom_url'] + "/v1/chat/completions")

        model_name = model_name=resp["model"]

    return TranslatePluginInitInfo(plugin_name=plugin_name, model_name=model_name)


def translate(core: AppCore, ts: TranslateStruct) -> TranslateStruct:
    options = core.plugin_options(plugin_name)

    from_lang_name = get_lang_by_2_chars_code(ts.req.from_lang)
    to_lang_name = get_lang_by_2_chars_code(ts.req.to_lang)

    special_prompt_for_model: str | None = options["special_prompt_for_model"].get(model_name)
    prompt_param = special_prompt_for_model if special_prompt_for_model else options["prompt"]

    prompt = translate_func.generate_prompt(prompt_param=prompt_param, from_lang_name=from_lang_name,
                                            to_lang_name=to_lang_name, postfix_param=options["prompt_postfix"],
                                            prompt_no_think_postfix_param=options['prompt_no_think_postfix'],
                                            context=ts.req.context, )
    use_library_for_request = options["use_library_for_request"]

    for part in tqdm(ts.parts, unit=params.tp.unit, ascii=params.tp.ascii, desc=params.tp.desc):
        if part.need_to_translate():
            content: str
            if use_library_for_request:
                content = library_request(llm_model, prompt, part.text)
            else:
                req = translate_func.get_open_ai_request(prompt, part.text)
                resp = translate_func.post_request(req, options['custom_url'] + "/v1/chat/completions")
                content = resp["choices"][0]['message']['content']

            part.translate = translate_func.remove_think_text(content)

    return ts


def library_request(model: LLM, prompt: str, text: str) -> str:
    chat = lmstudio.Chat(prompt)
    chat.add_user_message(text)
    result = model.respond(chat, config=LlmPredictionConfig(temperature=0.0))

    return result.content

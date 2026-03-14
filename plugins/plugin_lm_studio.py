import os
from concurrent.futures import ThreadPoolExecutor

import lmstudio
from lmstudio import LlmPredictionConfig, LlmLoadModelConfig
from lmstudio._sdk_models import GpuSetting
from tqdm import tqdm

from app import params, translate_func, cuda, parallel_process, log
from app.app_core import AppCore
from app.dto import TranslatePluginInitInfo, TranslateStruct
from app.lang_dict import get_lang_by_2_chars_code

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname
llm_model_list_names: list[str] = []
model_name: str = ""
logger = log.logger()

executor: ThreadPoolExecutor


def start(core: AppCore):
    manifest = {
        "name": "LM-Studio Translator",  # name
        "version": "1.0",  # version

        "default_options": {
            "custom_url": "http://localhost:1234",  #
            "prompt": "You are a professional translator. Your task is to translate a text (or word) provided below from %%from_lang%% to %%to_lang%%.\n%%context_prompt%%\nINSTRUCTION:Carefully analyze the context. Pay special attention to Terminology, Style, Consistency. Provide only the translation. Do not include any additional information, explanations, notes, or comments in your response. The output should be the pure translated text only.\nTEXT TO TRANSLATE:",
            "prompt_postfix": "",
            "prompt_no_think_postfix": False,
            "use_library": {
                "enabled": True,
                "model": "",
                "model_context_length": 8192
            },
            "parallel_processing": {
                "enabled": False,
                "enabled_gpu_numbers": [0, 1]
            },
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


def init_parallel_processing(options: dict) -> None:
    model_name_param = options['use_library']['model']
    gpu_numbers_for_processing: list[int] = options['parallel_processing']["enabled_gpu_numbers"]
    loaded_models = list(map(lambda item: item.identifier, lmstudio.list_loaded_models("llm")))
    client = lmstudio.get_default_client()
    gpu_count = cuda.gpu_count()

    for gpu_number in gpu_numbers_for_processing:
        model_name_parallel = parallel_process.get_model_name_by_gpu_id(model_name_param, gpu_number)
        # Check, maybe model already loaded. If not - try to load.
        if model_name_parallel not in loaded_models:
            # disable all other gpu load, exclude gpu_number
            disabled_gpus: list[int] = list(filter(lambda item: item != gpu_number, list(range(gpu_count))))
            config = LlmLoadModelConfig(
                gpu=GpuSetting(main_gpu=gpu_number, split_strategy="favorMainGpu", disabled_gpus=disabled_gpus),
                context_length=options["use_library"]["model_context_length"])
            logger.info("LM Studio load model: " + model_name_parallel)
            client.llm.load_new_instance(model_name_param, model_name_parallel, config=config, ttl=None)

        # llm_model_list.append(lmstudio.llm(model_name_parallel))
        llm_model_list_names.append(model_name_parallel)

    logger.info("LM Studio load models: " + str(llm_model_list_names))

    global executor
    executor = ThreadPoolExecutor(max_workers=len(llm_model_list_names),
                                  thread_name_prefix=parallel_process.executor_translate_prefix)

    global model_name
    model_name = model_name_param.lower()


def init(core: AppCore) -> TranslatePluginInitInfo:
    options = core.plugin_options(plugin_name)
    custom_url: str = options['custom_url']
    use_library_for_request = options["use_library"]["enabled"]

    global model_name
    if use_library_for_request:
        lmstudio.configure_default_client(custom_url.replace("http://", ""))

        if options['parallel_processing']["enabled"]:
            # if enabled parallel_processing, check loaded models, try to load, if needed model doesn't exist
            init_parallel_processing(options)
        else:
            # if disabled parallel_processing, check loaded models and get name, if found
            loaded_models = lmstudio.list_loaded_models("llm")

            if options['use_library']['model'] != "": # found model name in params. need to check load status
                model_param = [model for model in loaded_models if model.identifier == options['use_library']['model']]
                if len(model_param) == 1: # model name is unique in LLM studio, found loaded model from params
                    llm_model_name = model_param[0].identifier
                    llm_model_list_names.append(llm_model_name)
                    model_name = llm_model_name.lower()
                else:
                    model_name = options['use_library']['model']
                    client = lmstudio.get_default_client()
                    config = LlmLoadModelConfig(context_length=options["use_library"]["model_context_length"])
                    logger.info("LM Studio load model: " + model_name)
                    client.llm.load_new_instance(model_name, model_name, config=config, ttl=None)
            elif options['use_library']['model'] != "":  # loaded model not found - try to load
                model_name = options['use_library']['model']
                client = lmstudio.get_default_client()
                config = LlmLoadModelConfig(context_length=options["use_library"]["model_context_length"])
                logger.info("LM Studio load model: " + model_name)
                client.llm.load_new_instance(model_name, model_name, config=config, ttl=None)
            else:  # loaded model not found - and not model to load - error
                raise ValueError('List loaded models is empty. Please load model before init this plugin')
    else:
        postfix = translate_func.get_prompt_postfix(options["prompt_postfix"], options['prompt_no_think_postfix'])
        prompt = "You are assistant. " + postfix
        req = translate_func.get_open_ai_request(prompt, "init")
        resp = translate_func.post_request(req, options['custom_url'] + "/v1/chat/completions")

        model_name = model_name = resp["model"].lower()

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
    use_library_for_request = options["use_library"]["enabled"]
    # check params and not already parallel work in file processing task
    parallel_process_enabled: bool = (use_library_for_request and options['parallel_processing']["enabled"]
                                      and parallel_process.is_main_thread())

    if parallel_process_enabled:
        # first pass - prepare lists of params
        params_prompt: list[str] = list()
        params_text: list[str] = list()
        params_part_num: list[int] = list()
        for part_num, part in enumerate(ts.parts):
            if part.need_to_translate():
                params_prompt.append(prompt)
                params_text.append(part.text)
                params_part_num.append(part_num)

        # second pass - async execute and get list of results
        async_results: list[parallel_process.AsyncResult] = list(tqdm(executor.map(
            library_request, params_prompt, params_text, params_part_num), total=len(ts.parts),
            unit=params.tp.unit, ascii=params.tp.ascii, desc=params.tp.desc))

        # third pass - set translate to part by part_num
        for async_result in async_results:
            ts.parts[async_result.part_num].translate = async_result.content
    else:
        for part in tqdm(ts.parts, unit=params.tp.unit, ascii=params.tp.ascii, desc=params.tp.desc):
            if part.need_to_translate():
                content: str
            if use_library_for_request:
                content = library_request(prompt, part.text).content
            else:
                req = translate_func.get_open_ai_request(prompt, part.text)
                resp = translate_func.post_request(req, options['custom_url'] + "/v1/chat/completions")
                content = resp["choices"][0]['message']['content']

            part.translate = translate_func.remove_think_text(content)

    return ts


def library_request(prompt: str, text: str, part_num: int = 0) -> parallel_process.AsyncResult:
    # print(f"pid {os.getpid()} ({multiprocessing.current_process().name}) thread: {threading.current_thread().name}")

    thread_num = parallel_process.thread_num()
    if thread_num is None:
        model = lmstudio.llm(model_name)
    else:
        model = lmstudio.llm(llm_model_list_names[thread_num])

    chat = lmstudio.Chat(prompt)
    chat.add_user_message(text)
    result = model.respond(chat, config=LlmPredictionConfig(temperature=0.0))

    return parallel_process.AsyncResult(content=result.content, model=model.identifier, part_num=part_num)

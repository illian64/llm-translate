import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from app import dto, log
from app.app_core import AppCore

logger = log.logger()

model_name_parallel_postfix = "--parallel-gpu#"
executor_translate_prefix = "executor_translate_thread"
executor_file_processing_prefix = "executor_file_processing_thread"


@dataclass
class AsyncResult:
    content: str
    model: str
    part_num: int


def get_model_name_by_gpu_id(model: str, gpu_id: int) -> str:
    return f'{model}{model_name_parallel_postfix}{gpu_id}'


def translate_plugin_support_parallel_gpu_count(core: AppCore, custom_translator_plugin: str) -> int | None:
    """
    If translate plugin support parallel translate with few GPU and parallel processing enabled - return GPU count.
    :param core: core
    :param custom_translator_plugin: translate plugin from request, may be empty
    :return: GPU count if parallel processing enabled or None otherwise.
    """
    translator_plugin = core.get_translator_plugin(custom_translator_plugin)

    if "lm_studio" == translator_plugin:
        plugin_info = core.initialized_translator_engines[translator_plugin]
        options = core.plugin_options(plugin_info.plugin_name)
        if options["use_library"]["enabled"] and options["use_library"]["model"] != "" and options['parallel_processing']["enabled"]:
            enabled_gpu_numbers: list[int] = options['parallel_processing']["enabled_gpu_numbers"]
            return len(enabled_gpu_numbers)

    return None


def thread_num() -> int | None:
    thread_name: str = threading.current_thread().name
    if thread_name.startswith(executor_translate_prefix):
        return int(thread_name.replace(executor_translate_prefix + "_", ""))
    elif thread_name.startswith(executor_file_processing_prefix):
        return int(thread_name.replace(executor_file_processing_prefix + "_", ""))
    else:
        return None


def is_main_thread() -> bool:
    return 'MainThread' == threading.current_thread().name


def start_parallel_processing(gpu_count_for_parallel: int, core: AppCore,
                              translate_params: list[dto.TranslateCommonRequest]) -> list[dto.TranslateResp]:
    with ThreadPoolExecutor(max_workers=gpu_count_for_parallel,
                            thread_name_prefix=executor_file_processing_prefix) as executor:
        async_results: list[dto.TranslateResp] = list(executor.map(core.translate, translate_params))
        logger.info("Finish preprocess parallel task. Requests: " + str(len(async_results)))

        return async_results






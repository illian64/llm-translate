import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app import dto, log
from app.app_core import AppCore
from app.cuda import cuda_info

core: AppCore
logger = log.logger()


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    logger.info("Starting llm-translate")

    app.mount('/', StaticFiles(directory='static', html=True), name='static')
    cuda_info()

    try:
        global core
        core = AppCore()
        core.init_with_translate_plugins()
    except Exception as e:
        log.log_exception("Error init app", e)
        sys.exit(-1)

    yield
    logger.info("Stopping llm-translate")


app = FastAPI(lifespan=lifespan)


@app.get("/translate")
async def translate_get(text: str, from_lang: str = "", to_lang: str = "",
                        translator_plugin: str = "") -> dto.TranslateResp:
    """
       Translate text. GET-request.

       :param str text: text to translate

       :param str from_lang: from language (2 symbols, like "en").
       May be empty (will be replaced to "default_from_lang" from options)

       :param str to_lang: to language (2 symbols, like "en").
       May be empty (will be replaced to "default_to_lang" from options)

       :param str translator_plugin: plugin to use. If blank, default will be used.
        If not initialized (not in "default_translate_plugin" and not in "init_on_start" from options - throw error)

       :return: dto.TranslateResp with translate result and
    """

    request = dto.TranslateCommonRequest(text, from_lang, to_lang, translator_plugin)

    return core.translate(request)


@app.post("/translate")
async def translate_post(req: dto.TranslateReq) -> dto.TranslateResp:
    """
       Translate text. POST-request.

       :param req: object with information to translate:

       req.text: text to translate

       req.from_lang: from language (2 symbols, like "en").
       May be empty (will be replaced to "default_from_lang" from options)

       req.to_lang: to language (2 symbols, like "en").
       May be empty (will be replaced to "default_to_lang" from options)

       req.translator_plugin: to use. If blank, default will be used.
        If not initialized (not in "default_translate_plugin" and not in "init_on_start" from options - throw error)

       :return: dict (result: text)
    """
    request = dto.TranslateCommonRequest(req.text, req.from_lang, req.to_lang, req.translator_plugin)

    return core.translate(request)


@app.get("/process-files-list")
async def process_files_list(recursive_sub_dirs: bool) -> dto.ProcessingFileDirListResp:
    """
    Get lists files to processing task.

    :param recursive_sub_dirs: recursive search files in subdirectories

    :return: input list of files, output list of files, paths to directories
    """
    return core.process_files_list(recursive_sub_dirs)


@app.post("/process-files")
async def process_files(req: dto.ProcessingFileDirReq) -> dto.ProcessingFileDirResp:
    """
    Start processing files.

    :param req: processing params

    :return: result of processing
    """
    return core.process_files(req)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4990, log_level="info", log_config="log_config.yaml", use_colors=False)

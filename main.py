import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from app import dto, log, cuda
from app.app_core import AppCore

APP_VERSION = "0.8.0"


core: AppCore
logger = log.logger()


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    logger.info("Starting llm-translate")

    app.mount('/', StaticFiles(directory='static', html=True), name='static')
    cuda.cuda_info()

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    if core.rest_log_params is not None and core.rest_log_params.translate_validation_errors:
        logger.error(f"Error validating request: {request}: {exc_str}")
    return JSONResponse(content={"error": exc_str}, status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/translate")
async def translate_get(text: str, from_lang: str = "", to_lang: str = "", context: str = None,
                        translator_plugin: str = "") -> dto.TranslateResp:
    """
       Translate text. GET-request.

       :param str text: text to translate

       :param str context: additional context to translate (if model has context support)

       :param str from_lang: from language (2 symbols, like "en").
       May be empty (will be replaced to "default_from_lang" from options)

       :param str to_lang: to language (2 symbols, like "en").
       May be empty (will be replaced to "default_to_lang" from options)

       :param str translator_plugin: plugin to use. If blank, default will be used.
        If not initialized (not in "default_translate_plugin" and not in "init_on_start" from options - throw error)

       :return: dto.TranslateResp with translate result and
    """

    request = dto.TranslateCommonRequest(text=text, context=context, from_lang=from_lang, to_lang=to_lang,
                                         translator_plugin=translator_plugin)

    return core.translate(request)


@app.post("/translate")
async def translate_post(req: dto.TranslateReq) -> dto.TranslateResp:
    """
       Translate text. POST-request.

       :param req: object with information to translate:

       req.text: text to translate

       req.context: additional context to translate (if model has context support)

       req.from_lang: from language (2 symbols, like "en").
       May be empty (will be replaced to "default_from_lang" from options)

       req.to_lang: to language (2 symbols, like "en").
       May be empty (will be replaced to "default_to_lang" from options)

       req.translator_plugin: to use. If blank, default will be used.
        If not initialized (not in "default_translate_plugin" and not in "init_on_start" from options - throw error)

       :return: dict (result: text)
    """
    request = dto.TranslateCommonRequest(text=req.text, context=req.context, from_lang=req.from_lang, to_lang=req.to_lang,
                                         translator_plugin=req.translator_plugin)

    return core.translate(request)


@app.post("/translate/sugoi-like")
async def translate_sugoi_like_post(req: dto.SugoiLikePostReq, from_lang: str = "", to_lang: str = "", context: str = None,
                                    translator_plugin: str = "") -> list[str]:
    """
    Translate text. Request and response like a sugoi translator - https://github.com/leminhyen2/Sugoi-Japanese-Translator
    This allows the query to be used in integration programs such as a Translator++ - http://dreamsavior.net/docs/translator/

    :param req:
        req.content - list of texts to translation.
        req.message - for backward compatibility.

    :param str context: additional context to translate (if model has context support)

    :param str from_lang: from language (2 symbols, like "en").
    May be empty (will be replaced to "default_from_lang" from options)

    :param str to_lang: to language (2 symbols, like "en").
    May be empty (will be replaced to "default_to_lang" from options)

    :param str translator_plugin: plugin to use. If blank, default will be used.
    If not initialized (not in "default_translate_plugin" and not in "init_on_start" from options - throw error)

    :return: list of translated texts
    """
    response_list: list[str] = []
    for text in req.content:
        request = dto.TranslateCommonRequest(text=text, context=context, from_lang=from_lang, to_lang=to_lang,
                                             translator_plugin=translator_plugin)
        translate = core.translate(request)
        if translate.result:
            response_list.append(translate.result)
        else:
            raise ValueError("Error translate text: " + text)

    return response_list


@app.get("/translate/sugoi-like")
async def translate_sugoi_like_post(text: str, from_lang: str = "", to_lang: str = "", context: str = None,
                                    translator_plugin: str = "") -> dto.SugoiLikeGetResp:
    """
    Translate text. Request and response like a sugoi translator - https://github.com/leminhyen2/Sugoi-Japanese-Translator
    This allows the query to be used in integration programs such as a Translator++ - http://dreamsavior.net/docs/translator/

    :param str text: text to translate.

    :param str context: additional context to translate (if model has context support)

    :param str from_lang: from language (2 symbols, like "en").
    May be empty (will be replaced to "default_from_lang" from options)

    :param str to_lang: to language (2 symbols, like "en").
    May be empty (will be replaced to "default_to_lang" from options)

    :param str translator_plugin: plugin to use. If blank, default will be used.
    If not initialized (not in "default_translate_plugin" and not in "init_on_start" from options - throw error)

    :return: list of translated texts
    """
    request = dto.TranslateCommonRequest(text=text, context=context, from_lang=from_lang, to_lang=to_lang,
                                         translator_plugin=translator_plugin)
    translate = core.translate(request)

    return dto.SugoiLikeGetResp(trans=translate.result)


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
    uvicorn.run(app, host="127.0.0.1", port=4990, log_level="info", log_config="resources/log_config.yaml", use_colors=False)

from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
import logging

from starlette.staticfiles import StaticFiles

from app.app_core import AppCore
from app.cuda import cuda_info
from app.dto import TranslateReq
from app.struct import Request
from app.properties import Properties


core: AppCore
logger = logging.getLogger('uvicorn')


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    cuda_info()
    logger.info("Starting llm-translate")
    global core
    core = AppCore()
    core.init_with_plugins()

    yield
    logger.info("Stopping llm-translate")


app = FastAPI(lifespan=lifespan)
properties = Properties()


@app.get("/translate")
async def translate_get(text: str, from_lang: str = "", to_lang: str = "", translator_plugin: str = ""):
    """
       Return translation

       :param str text: text to translate

       :param str from_lang: from language (2 symbols, like "en").
       May be empty (will be replaced to "default_from_lang" from options)

       :param str to_lang: to language (2 symbols, like "en").
       May be empty (will be replaced to "default_to_lang" from options)

       :param str translator_plugin: to use. If blank, default will be used.
        If not initialized (not in "default_translate_plugin" and not in "init_on_start" from options - throw error)

       :param str api_key: api key for access (if service setup in security mode with api keys)

       :return: dict (result: text)
       """

    request = Request(text, from_lang, to_lang, translator_plugin)

    return core.translate(request)


@app.post("/translate")
async def translate_post(req: TranslateReq):
    request = Request(req.text, req.from_lang, req.to_lang, req.translator_plugin)
    return core.translate(request)


if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s %(levelname)s %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s %(levelname)s %(message)s"

    app.mount('/', StaticFiles(directory='static', html=True), name='static')
    uvicorn.run(app, host="127.0.0.1", port=properties.port, log_level="info", log_config=log_config, use_colors=False)
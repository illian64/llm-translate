# No Translate dummy plugin
# author: Vladislav Janvarev

import os

from tqdm import tqdm

from app import params
from app.app_core import AppCore
from app.dto import TranslatePluginInitInfo, TranslateStruct

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname


# start function
def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "No Translate dummy plugin",  # name
        "version": "1.0",  # version

        "translate": {
            "no_translate": (init, translate)  # 1 function - init, 2 - translate
        }
    }

    return manifest


def init(core: AppCore) -> TranslatePluginInitInfo:
    return TranslatePluginInitInfo(plugin_name=plugin_name, model_name="")


def translate(core: AppCore, ts: TranslateStruct):
    for part in tqdm(ts.parts, unit=params.tp.unit, ascii=params.tp.ascii, desc=params.tp.desc):
        part.translate = part.text

    return ts

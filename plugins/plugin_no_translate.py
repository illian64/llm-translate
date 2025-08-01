# No Translate dummy plugin
# author: Vladislav Janvarev

import os

from app.app_core import AppCore
from app.struct import TranslateStruct

modname = os.path.basename(__file__)[:-3]  # calculating modname


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


def init(core: AppCore):
    return modname


def translate(core: AppCore, ts: TranslateStruct):
    for part in ts.parts:
        part.translate = part.text

    return ts

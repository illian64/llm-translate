import requests
from translator.basetranslator import basetrans

# -------------------------------------------------------------------------
# Configuration variables
# -------------------------------------------------------------------------
llm_translate__translate_path = "http://127.0.0.1:4990/translate"
llm_translate__context = "CONTEXT: This text (or word) for translation is the dialogue of characters in a computer game.\n"
llm_translate__use_languages_from_luna_translate = True
llm_translate__from_lang = ""
llm_translate__to_lang = ""
# -------------------------------------------------------------------------


class TS(basetrans):
    def translate(self, content: str):
        req = {
            "text": content,
            "from_lang": self.srclang if llm_translate__use_languages_from_luna_translate else llm_translate__from_lang,
            "to_lang": self.tgtlang if llm_translate__use_languages_from_luna_translate else llm_translate__to_lang,
            "context": llm_translate__context,
        }
        try:
            resp = requests.post(llm_translate__translate_path, json=req).json()

            if resp.get("result"):
                return resp["result"]
            elif resp.get("error"):
                return resp["error"]
            else:
                return "Unknown error"
        except Exception as e:
            raise Exception("Unknown error, text:" + content + ", e: " + str(e))

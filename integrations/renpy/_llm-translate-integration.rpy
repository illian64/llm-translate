init 99 python:
    import sys

    #--------------------------------------------------------------------------
    # Configuration variables
    #--------------------------------------------------------------------------
    llm_translate__translate_path = "http://127.0.0.1:4990/translate"
    llm_translate__preserve_original_text = True
    llm_translate__translate_text_all = False # not recommended
    llm_translate__translate_font_name = "DejaVuSans.ttf"
    llm_translate__translate_font_size = 22
    llm_translate__translate_font_format_tag = "i"
    llm_translate__replace_new_line_to_space = True
    llm_translate__translate_text_delimiter = "\n"
    llm_translate__from_lang = ""
    llm_translate__to_lang = ""
    llm_translate__context = "CONTEXT: This text for translation is the dialogue of characters in a computer game.\n"
    #--------------------------------------------------------------------------
    
    # module variables
    llm_translate__translate_toggle_value = True # enable / disable translate
    llm_translate__translated_text_dict = {} # cache of translated text


    def llm_translate__fill_variables_values(src):
        """
        Set values for variables in text.
        :param src: text
        :return: text with filled variables values
        """
        s = src
        s = renpy.substitutions.substitute(s, scope = None, force = True, translate = False)
        if isinstance(s, (bytes, str)):
            return s
        return s[0]


    #
    def llm_translate__preprocess_text(src):
        """
        Preprocess text - remove tags, fill variables values
        :param src: text
        :return: preprocessed text
        """
        s = src
        if llm_translate__replace_new_line_to_space:
            s = s.replace("{p}", " ")
            s = s.replace("\n", " ")
        else:
            s = s.replace("{p}", "\n")

        s = llm_translate__fill_variables_values(s)
        s = renpy.translation.dialogue.notags_filter(s) #remove tags {}

        return s


    def llm_translate__wrap_text_tag(text, tag, value = None):
        """
        Formatting text with tags.
        :param text: text
        :param tag: tag
        :param value: tag value (optional)
        :return: text with tags
        """
        if tag is None or tag == "":
            return text
        if value is None:
            return "{" + tag + "}" + text + "{/" + tag + "}"
        else:
            return "{" + tag + "=" + str(value) + "}" + text + "{/" + tag + "}"

    # translate request with module requests - for python v3
    def llm_translate__request_python_v3(src, s):
        """
        Request to translate text.
        :param src: source text
        :param s: preprocessed text
        :return: translate result
        """
        import requests
        req = {
            "text": s,
            "llm_translate__from_lang": llm_translate__from_lang,
            "llm_translate__to_lang": llm_translate__to_lang,
            "context": llm_translate__context,
        }
        resp = requests.post(url=llm_translate__translate_path, json=req).json()

        if resp.get("result"):
            translate = resp["result"].replace("\n", "{p}")
            translate_with_tags = translate
            translate_with_tags = llm_translate__wrap_text_tag(translate_with_tags, llm_translate__translate_font_format_tag)
            translate_with_tags = llm_translate__wrap_text_tag(translate_with_tags, "font", llm_translate__translate_font_name)
            translate_with_tags = llm_translate__wrap_text_tag(translate_with_tags, "size", llm_translate__translate_font_size)

            if llm_translate__preserve_original_text:
                result = src + llm_translate__translate_text_delimiter + translate_with_tags
            else:
                result = translate_with_tags
            return result
        else:
            return resp["error"]

    #
    def llm_translate__translate_text(src):
        """
        Main function to translate
        :param src: text
        :return: translate / original text and translate
        """
        s = src
        # text is empty or translate disable - return
        if s is None or s == "" or not llm_translate__translate_toggle_value:
            return s

        # preprocess text and again validate to empty
        s = llm_translate__preprocess_text(s)
        if s is None or s == "":
            return src
    
        dict_translated_value = llm_translate__translated_text_dict.get(s, None)
        if dict_translated_value is None:
            translate_result = llm_translate__request_python_v3(src, s)

            llm_translate__translated_text_dict[s] = translate_result
        else:
            return dict_translated_value

    # enable or disable translate
    def llm_translate__toggle_translate():
        global llm_translate__translate_toggle_value
        value = not llm_translate__translate_toggle_value
        llm_translate__translate_toggle_value = value
        if not value: #clear cache
            llm_translate__translated_text_dict.clear()
    
    # apply replace text
    if llm_translate__translate_text_all:
        config.replace_text = llm_translate__translate_text
    else:
        config.say_menu_text_filter = llm_translate__translate_text


    # translate request with module requests - for python v3
    def llm_translate__request_python_v2(src, s):
        return src


# button to enable or disable translate
screen toggle_tr_button():
    hbox:
        style_prefix "quick"
        xalign 0.0
        yalign 0.0

        textbutton _("Tr: " + str(llm_translate__translate_toggle_value)) action Function(llm_translate__toggle_translate)

init python:
    config.overlay_screens.append("toggle_tr_button")


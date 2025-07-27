async function translateText() {
    const elProgress = document.getElementById('progress');
    const trigger = document.getElementById('trigger');
    const errorText = document.getElementById('errorText');

    const text = document.getElementById('text').value;
    const fromLang = document.getElementById('from_lang_select').value;
    const toLang = document.getElementById('to_lang_select').value;
    const plugin = document.getElementById('plugin').value;

    trigger.disabled = true;
    elProgress.style.display = 'inline';

    const reqBody = JSON.stringify({
        text: text, from_lang: fromLang, to_lang: toLang,
        translator_plugin: plugin
    });
    const reqParam = {
        method: 'POST',
        body: reqBody,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    }
    try {
        const response = await fetch(`/translate`, reqParam);
        const data = await response.json();
        if (data.error) {
            errorText.innerHTML = data.error;
            return "";
        } else {
            const translation = data.result;
            document.getElementById('text_result').value = translation;

            errorText.innerHTML = ""
            return translation;
        }
    } catch (error) {
        errorText.innerHTML = error.message;
        console.error(error.message);
    } finally {
        elProgress.style.display = 'none';
        trigger.disabled = false;
    }
}


window.onload = () => {
    const trigger = document.getElementById('trigger');
    trigger.onmouseup = () => {
        translateText();
    };

    const langDict = {
        'en': 'english',
        'ru': 'russian',
        'ab': 'abkhazian',
        'aa': 'afar',
        'af': 'afrikaans',
        'sq': 'albanian',
        'am': 'amharic',
        'ar': 'arabic',
        'hy': 'armenian',
        'as': 'assamese',
        'ay': 'aymara',
        'az': 'azerbaijani',
        'ba': 'bashkir',
        'eu': 'basque',
        'bn': 'bengali',
        'dz': 'bhutani',
        'bh': 'bihari',
        'bi': 'bislama',
        'br': 'breton',
        'bg': 'bulgarian',
        'my': 'burmese',
        'be': 'byelorussian',
        'km': 'cambodian',
        'ca': 'catalan',
        'zh': 'chinese',
        'co': 'corsican',
        'hr': 'croatian',
        'cs': 'czech',
        'da': 'danish',
        'nl': 'dutch',
        'eo': 'esperanto',
        'et': 'estonian',
        'fo': 'faeroese',
        'fj': 'fiji',
        'fi': 'finnish',
        'fr': 'french',
        'fy': 'frisian',
        'gd': 'gaelic',
        'gl': 'galician',
        'ka': 'georgian',
        'de': 'german',
        'el': 'greek',
        'kl': 'greenlandic',
        'gn': 'guarani',
        'gu': 'gujarati',
        'ha': 'hausa',
        'iw': 'hebrew',
        'hi': 'hindi',
        'hu': 'hungarian',
        'is': 'icelandic',
        'in': 'indonesian',
        'ia': 'interlingua',
        'ie': 'interlingue',
        'ik': 'inupiak',
        'ga': 'irish',
        'it': 'italian',
        'ja': 'japanese',
        'jw': 'javanese',
        'kn': 'kannada',
        'ks': 'kashmiri',
        'kk': 'kazakh',
        'rw': 'kinyarwanda',
        'ky': 'kirghiz',
        'rn': 'kirundi',
        'ko': 'korean',
        'ku': 'kurdish',
        'lo': 'laothian',
        'la': 'latin',
        'lv': 'latvian',
        'ln': 'lingala',
        'lt': 'lithuanian',
        'mk': 'macedonian',
        'mg': 'malagasy',
        'ms': 'malay',
        'ml': 'malayalam',
        'mt': 'maltese',
        'mi': 'maori',
        'mr': 'marathi',
        'mo': 'moldavian',
        'mn': 'mongolian',
        'na': 'nauru',
        'ne': 'nepali',
        'no': 'norwegian',
        'oc': 'occitan',
        'or': 'oriya',
        'om': 'oromo',
        'ps': 'pashto',
        'fa': 'persian',
        'pl': 'polish',
        'pt': 'portuguese',
        'pa': 'punjabi',
        'qu': 'quechua',
        'rm': 'rhaeto-romance',
        'ro': 'romanian',
        'sm': 'samoan',
        'sg': 'sangro',
        'sa': 'sanskrit',
        'sr': 'serbian',
        'sh': 'serbo-croatian',
        'st': 'sesotho',
        'tn': 'setswana',
        'sn': 'shona',
        'sd': 'sindhi',
        'si': 'singhalese',
        'ss': 'siswati',
        'sk': 'slovak',
        'sl': 'slovenian',
        'so': 'somali',
        'es': 'spanish',
        'su': 'sudanese',
        'sw': 'swahili',
        'sv': 'swedish',
        'tl': 'tagalog',
        'tg': 'tajik',
        'ta': 'tamil',
        'tt': 'tatar',
        'te': 'tegulu',
        'th': 'thai',
        'bo': 'tibetan',
        'ti': 'tigrinya',
        'to': 'tonga',
        'ts': 'tsonga',
        'tr': 'turkish',
        'tk': 'turkmen',
        'tw': 'twi',
        'uk': 'ukrainian',
        'ur': 'urdu',
        'uz': 'uzbek',
        'vi': 'vietnamese',
        'vo': 'volapuk',
        'cy': 'welsh',
        'wo': 'wolof',
        'xh': 'xhosa',
        'ji': 'yiddish',
        'yo': 'yoruba',
        'zu': 'zulu',
    };

    const fromLangSelect = document.getElementById('from_lang_select');
    const toLangSelect = document.getElementById('to_lang_select');

    for (const [key, value] of Object.entries(langDict)) {
        fromLangSelect.innerHTML += "<option value='" + key + "'>" + value + "</option>";
        toLangSelect.innerHTML += "<option value='" + key + "'>" + value + "</option>";
    }
    fromLangSelect.value = 'en';
    toLangSelect.value = 'ru';
}
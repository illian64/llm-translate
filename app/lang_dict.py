lang_2_chars_to_name: dict = {
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
    'en': 'english',
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
    'ru': 'russian',
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
}


def get_lang_by_2_chars_code(code: str):
    result = lang_2_chars_to_name.get(code)
    if result:
        return result
    else:
        return code


nllb_200_langlist_str = """
ace_Arab    | Acehnese (Arabic script)
ace_Latn    | Acehnese (Latin script)
acm_Arab    | Mesopotamian Arabic
acq_Arab    | Ta’izzi-Adeni Arabic
aeb_Arab    | Tunisian Arabic
afr_Latn    | Afrikaans
ajp_Arab    | South Levantine Arabic
aka_Latn    | Akan
als_Latn    | Tosk Albanian
amh_Ethi    | Amharic
apc_Arab    | North Levantine Arabic
arb_Arab    | Modern Standard Arabic
arb_Latn    | Modern Standard Arabic (Romanized)
ars_Arab    | Najdi Arabic
ary_Arab    | Moroccan Arabic
arz_Arab    | Egyptian Arabic
asm_Beng    | Assamese
ast_Latn    | Asturian
awa_Deva    | Awadhi
ayr_Latn    | Central Aymara
azb_Arab    | South Azerbaijani
azj_Latn    | North Azerbaijani
bak_Cyrl    | Bashkir
bam_Latn    | Bambara
ban_Latn    | Balinese
bel_Cyrl    | Belarusian
bem_Latn    | Bemba
ben_Beng    | Bengali
bho_Deva    | Bhojpuri
bjn_Arab    | Banjar (Arabic script)
bjn_Latn    | Banjar (Latin script)
bod_Tibt    | Standard Tibetan
bos_Latn    | Bosnian
bug_Latn    | Buginese
bul_Cyrl    | Bulgarian
cat_Latn    | Catalan
ceb_Latn    | Cebuano
ces_Latn    | Czech
cjk_Latn    | Chokwe
ckb_Arab    | Central Kurdish
crh_Latn    | Crimean Tatar
cym_Latn    | Welsh
dan_Latn    | Danish
deu_Latn    | German
dik_Latn    | Southwestern Dinka
dyu_Latn    | Dyula
dzo_Tibt    | Dzongkha
ell_Grek    | Greek
eng_Latn    | English
epo_Latn    | Esperanto
est_Latn    | Estonian
eus_Latn    | Basque
ewe_Latn    | Ewe
fao_Latn    | Faroese
fij_Latn    | Fijian
fin_Latn    | Finnish
fon_Latn    | Fon
fra_Latn    | French
fur_Latn    | Friulian
fuv_Latn    | Nigerian Fulfulde
gaz_Latn    | West Central Oromo
gla_Latn    | Scottish Gaelic
gle_Latn    | Irish
glg_Latn    | Galician
grn_Latn    | Guarani
guj_Gujr    | Gujarati
hat_Latn    | Haitian Creole
hau_Latn    | Hausa
heb_Hebr    | Hebrew
hin_Deva    | Hindi
hne_Deva    | Chhattisgarhi
hrv_Latn    | Croatian
hun_Latn    | Hungarian
hye_Armn    | Armenian
ibo_Latn    | Igbo
ilo_Latn    | Ilocano
ind_Latn    | Indonesian
isl_Latn    | Icelandic
ita_Latn    | Italian
jav_Latn    | Javanese
jpn_Jpan    | Japanese
kab_Latn    | Kabyle
kac_Latn    | Jingpho
kam_Latn    | Kamba
kan_Knda    | Kannada
kas_Arab    | Kashmiri (Arabic script)
kas_Deva    | Kashmiri (Devanagari script)
kat_Geor    | Georgian
kaz_Cyrl    | Kazakh
kbp_Latn    | Kabiyè
kea_Latn    | Kabuverdianu
khk_Cyrl    | Halh Mongolian
khm_Khmr    | Khmer
kik_Latn    | Kikuyu
kin_Latn    | Kinyarwanda
kir_Cyrl    | Kyrgyz
kmb_Latn    | Kimbundu
kmr_Latn    | Northern Kurdish
knc_Arab    | Central Kanuri (Arabic script)
knc_Latn    | Central Kanuri (Latin script)
kon_Latn    | Kikongo
kor_Hang    | Korean
lao_Laoo    | Lao
lij_Latn    | Ligurian
lim_Latn    | Limburgish
lin_Latn    | Lingala
lit_Latn    | Lithuanian
lmo_Latn    | Lombard
ltg_Latn    | Latgalian
ltz_Latn    | Luxembourgish
lua_Latn    | Luba-Kasai
lug_Latn    | Ganda
luo_Latn    | Luo
lus_Latn    | Mizo
lvs_Latn    | Standard Latvian
mag_Deva    | Magahi
mai_Deva    | Maithili
mal_Mlym    | Malayalam
mar_Deva    | Marathi
min_Arab    | Minangkabau (Arabic script)
min_Latn    | Minangkabau (Latin script)
mkd_Cyrl    | Macedonian
mlt_Latn    | Maltese
mni_Beng    | Meitei (Bengali script)
mos_Latn    | Mossi
mri_Latn    | Maori
mya_Mymr    | Burmese
nld_Latn    | Dutch
nno_Latn    | Norwegian Nynorsk
nob_Latn    | Norwegian Bokmål
npi_Deva    | Nepali
nso_Latn    | Northern Sotho
nus_Latn    | Nuer
nya_Latn    | Nyanja
oci_Latn    | Occitan
ory_Orya    | Odia
pag_Latn    | Pangasinan
pan_Guru    | Eastern Panjabi
pap_Latn    | Papiamento
pbt_Arab    | Southern Pashto
pes_Arab    | Western Persian
plt_Latn    | Plateau Malagasy
pol_Latn    | Polish
por_Latn    | Portuguese
prs_Arab    | Dari
quy_Latn    | Ayacucho Quechua
ron_Latn    | Romanian
run_Latn    | Rundi
rus_Cyrl    | Russian
sag_Latn    | Sango
san_Deva    | Sanskrit
sat_Olck    | Santali
scn_Latn    | Sicilian
shn_Mymr    | Shan
sin_Sinh    | Sinhala
slk_Latn    | Slovak
slv_Latn    | Slovenian
smo_Latn    | Samoan
sna_Latn    | Shona
snd_Arab    | Sindhi
som_Latn    | Somali
sot_Latn    | Southern Sotho
spa_Latn    | Spanish
srd_Latn    | Sardinian
srp_Cyrl    | Serbian
ssw_Latn    | Swati
sun_Latn    | Sundanese
swe_Latn    | Swedish
swh_Latn    | Swahili
szl_Latn    | Silesian
tam_Taml    | Tamil
taq_Latn    | Tamasheq (Latin script)
taq_Tfng    | Tamasheq (Tifinagh script)
tat_Cyrl    | Tatar
tel_Telu    | Telugu
tgk_Cyrl    | Tajik
tgl_Latn    | Tagalog
tha_Thai    | Thai
tir_Ethi    | Tigrinya
tpi_Latn    | Tok Pisin
tsn_Latn    | Tswana
tso_Latn    | Tsonga
tuk_Latn    | Turkmen
tum_Latn    | Tumbuka
tur_Latn    | Turkish
twi_Latn    | Twi
tzm_Tfng    | Central Atlas Tamazight
uig_Arab    | Uyghur
ukr_Cyrl    | Ukrainian
umb_Latn    | Umbundu
urd_Arab    | Urdu
uzn_Latn    | Northern Uzbek
vec_Latn    | Venetian
vie_Latn    | Vietnamese
war_Latn    | Waray
wol_Latn    | Wolof
xho_Latn    | Xhosa
ydd_Hebr    | Eastern Yiddish
yor_Latn    | Yoruba
yue_Hant    | Yue Chinese
zho_Hans    | Chinese (Simplified)
zho_Hant    | Chinese (Traditional)
zsm_Latn    | Standard Malay
zul_Latn    | Zulu
"""


#  SEE LANGUAGE CODES in transformers_fb_nllb200distilled600M_text.md
# need to extend this dict from nllb_200_langlist_str
lang_2_chars_to_nllb_lang: dict = {
    'zh': 'zho_Hant',
    'en': 'eng_Latn',
    'fr': 'fra_Latn',
    'de': 'deu_Latn',
    'it': 'ita_Latn',
    'ja': 'jpn_Jpan',
    'ru': 'rus_Cyrl',
    'es': 'spa_Latn',
}
# xunity-autotranslator

## English

Project site: https://github.com/bbepis/XUnity.AutoTranslator

## Русский

Сайт проекта: https://github.com/bbepis/XUnity.AutoTranslator

### Установка

Установка на примере [BepInEx](https://github.com/bbepis/BepInEx).

* Необходимо загрузить `xunity-autotranslator` и `BepInEx`, поместить их в папку с игрой, согласно инструкциям этих проектов.
* Запустить игру и закрыть.
* Если плагины для перевода были установлены правильно, то будет создан файл по пути
`папка_с_игрой/BepInEx/config/AutoTranslatorConfig.ini`
* Необходимо открыть этот файл `AutoTranslatorConfig.ini` в любом текстовом редакторе (для windows можно использовать Блокнот).
* Найти следующие параметры и задать им следующие значения:

Для включения интеграции с llm-translate:
```
[Service]
Endpoint=CustomTranslate
```

Для выбора языков - двухбуквенный код языка оригинала и языка, на который нужно выполнить перевод.
```
[General]
Language=ru
FromLanguage=en
```

Для настройки url приложения llm-translate.
```
[Custom]
Url=http://127.0.0.1:4990/translate/xunity-autotranslator
EnableShortDelay=False
DisableSpamChecks=True
```

В запросе можно передать контекст дял перевода, тогда параметр Url будет выглядеть примерно так:
```
Url=http://127.0.0.1:4990/translate/xunity-autotranslator?context=Context - This text (or word) for translation is the dialogue of characters in a computer game.
```





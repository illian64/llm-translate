# LLM Translate


This is project for offline translate with LLM (Large Language Model) or more specific translate models, like a nllb-200 or madlad-400.

Supports text translation via the web interface or API requests, and files translation too.

---

Сервис, ориентированный на оффлайн перевод текстов и файлов с использованием LLM (Large Language Model) или более специфичных моделей,
таких как nllb-200 или madlad-400.

**Для приемлемой скорости работы перевода необходима видеокарта NVIDIA! 
Работа на других видеокартах или с использованием процессора возможна, но не рекомендуется.**

Поддерживается как перевод текста через веб-интерфейс или запросы к API, так и перевод файлов.

Более подробно - в [документации](doc/ru/_index.md).

Структура проекта:
* `/app` - папка с python-файлами, которые используются плагинами и API-контроллером.
* `/cache` - папка для сохранения файла базы кэша по умолчанию. [Документация](doc/ru/options.md).
* `/doc` - документация
* `/files_processing` - директория для обработки/перевода файлов по умолчанию. 
в `/files_processing/in` помещаются файлы для обработки, в папке `/files_processing/out` создаются результаты обработки.
[Документация](doc/ru/processing_files.md).
* `/models` - папка по умолчанию для размещения моделей для перевода, таких как madlad-400 или nllb-200.
  [Документация](doc/ru/translate_text.md).
* `/options` - папка с настройками сервиса и плагинов. [Документация](doc/ru/options.md).
* `/plugins` - папка с python-файлами плагинов, перевода и обработки файлов.
* `/static` - папка с html, css, js файлами для веб-интерфейса.
* `/test` - файлы unit-тестов для исходного кода.
* `compose.yaml` - файл с настройками для запуска Docker-контейнера. [Документация](doc/ru/install.md).
* `Dockerfile` - файл с настройками создания Docker-контейнера. [Документация](doc/ru/install.md).
* `jaa.py` - библиотека управления плагинами.
* `log_config.yaml` - конфигурация логов.
* `requirements.txt` - список внешних зависимостей проекта.

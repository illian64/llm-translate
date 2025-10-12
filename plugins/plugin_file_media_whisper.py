import gc
import os

import torch
import whisper
from whisper import utils

from app import file_processor, cuda
from app.app_core import AppCore
from app.dto import ProcessingFileDirReq, ProcessingFileResp, FileProcessingPluginInitInfo, ProcessingFileStruct

plugin_name = os.path.basename(__file__)[:-3]  # calculating modname

model: whisper.Whisper | None = None


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "Subtitle extractor for media files (Whisper)",  # name
        "version": "1.0",  # version

        "default_options": {
            "enabled": True,
            "model": "large-v3-turbo",
            "cuda": True,
            "cuda_device_index": 0,
            "unload_model_after_processing": True,
            "translate_after_processing": True,

            "temperature": [0.0, 0.2, 0.4, 0.6],
            "condition_on_previous_text": False,
            "no_speech_threshold": 0.6,
            "word_timestamps": True,
            "hallucination_silence_threshold": 1,
            "carry_initial_prompt": False,
            "initial_prompt": "",
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1.0,

            "output_file_name_template": "%%source%%.src_sub",

            "default_extension_processor": {
                "mpeg": True,
                "mpg": True,
                "mp4": True,
                "mp3": True,
                "avi": True,
                "wav": True,
                "mkv": True,
                "vob": True,
                "ac3": True,
                "mpa": True,
                "ogg": True,
            },
        },

        "file_processing": {
            "file_media_whisper_processing": (init, file_processing, processed_file_name, after_processing)
        },
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    pass


def init(core: AppCore) -> FileProcessingPluginInitInfo:
    ext = {"mpeg", "mpg", "mp3", "mp4", "avi", "wav", "mkv", "vob", "ac3", "mpa", "ogg"}

    return FileProcessingPluginInitInfo(plugin_name=plugin_name, supported_extensions=ext)


def file_processing(core: AppCore, file_struct: ProcessingFileStruct, req: ProcessingFileDirReq) -> ProcessingFileResp:
    options = core.plugin_options(plugin_name)

    global model
    if model is None:
        model = whisper.load_model(name=options["model"], device=cuda.get_device_with_gpu_num(options))

    temperature: list[float] = options["temperature"]
    transcribe = model.transcribe(audio=file_struct.path_file_in(), language=req.from_lang, verbose=False,
                                  temperature=tuple(temperature),
                                  condition_on_previous_text=options["condition_on_previous_text"],
                                  no_speech_threshold=options["no_speech_threshold"],
                                  word_timestamps=options["word_timestamps"],
                                  hallucination_silence_threshold=options["hallucination_silence_threshold"],
                                  carry_initial_prompt=options["carry_initial_prompt"],
                                  initial_prompt=options["initial_prompt"],
                                  compression_ratio_threshold=options["compression_ratio_threshold"],
                                  logprob_threshold=options["logprob_threshold"]
                                  )

    if transcribe:
        out_file_name = processed_file_name(core=core, file_struct=file_struct, req=req)
        writer = utils.get_writer('srt', file_struct.path_out)
        writer(transcribe, out_file_name, {})

        if options["translate_after_processing"]:
            return translate_after_processing(core=core, req=req, file_name_ext=out_file_name)
        else:
            return file_processor.get_processing_file_resp_ok(file_struct=file_struct, file_out=out_file_name)
    else:
        return file_processor.get_processing_file_resp_error(
            file_in=file_struct.file_name_ext, path_in=file_struct.path_in, error_msg="Can't get transcribe")


def processed_file_name(core: AppCore, file_struct: ProcessingFileStruct, req: ProcessingFileDirReq) -> str:
    options = core.plugin_options(plugin_name)
    template: str = options["output_file_name_template"]

    return file_processor.file_name_from_predefined_template(file_struct=file_struct, req=req,
                                                             template=template, replace_ext="srt")


def translate_after_processing(core: AppCore, req: ProcessingFileDirReq, file_name_ext: str) -> ProcessingFileResp:
    return core.process_file(req=req, root=req.directory_out, file_name=file_name_ext)


def after_processing(core: AppCore) -> None:
    options = core.plugin_options(plugin_name)
    global model

    if options["unload_model_after_processing"] and model is not None:
        model = None
        if options["cuda"]:
            torch.cuda.empty_cache()
        else:
            gc.collect()

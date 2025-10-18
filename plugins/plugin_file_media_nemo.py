import datetime
import gc
import os

import torch
from nemo.collections.asr.models import ASRModel, EncDecRNNTModel
from pydub import AudioSegment

from app import file_processor, cuda, log
from app.app_core import AppCore
from app.dto import ProcessingFileDirReq, ProcessingFileResp, FileProcessingPluginInitInfo, ProcessingFileStruct

logger = log.logger()
plugin_name = os.path.basename(__file__)[:-3]  # calculating modname

model: EncDecRNNTModel | None = None


def start(core: AppCore):
    manifest = {  # plugin settings
        "name": "Subtitle extractor for media files (Nemo)",  # name
        "version": "1.0",  # version

        "default_options": {
            "enabled": True,
            "model": "nvidia/canary-1b-v2",
            "cuda": True,
            "cuda_device_index": 0,
            "unload_model_after_processing": True,
            "translate_after_processing": True,

            "batch_size": 4,

            "output_file_name_template": "%%source%%.src_sub",

            "default_extension_processor": {
            },
        },

        "file_processing": {
            "file_media_nemo_processing": (init, file_processing, processed_file_name, after_processing)
        },
    }

    return manifest


def start_with_options(core: AppCore, manifest: dict):
    pass


def init(core: AppCore) -> FileProcessingPluginInitInfo:
    ext = {"mpeg", "mpg", "mp3", "mp4", "avi", "wav", "mkv", "vob", "ac3", "mpa", "ogg"}

    return FileProcessingPluginInitInfo(plugin_name=plugin_name, supported_extensions=ext)


def format_srt_time(seconds: float) -> str:
    """Converts seconds to SRT time format HH:MM:SS,mmm using datetime.timedelta"""
    sanitized_total_seconds = max(0.0, seconds)
    delta = datetime.timedelta(seconds=sanitized_total_seconds)
    total_int_seconds = int(delta.total_seconds())

    hours = total_int_seconds // 3600
    remainder_seconds_after_hours = total_int_seconds % 3600
    minutes = remainder_seconds_after_hours // 60
    seconds_part = remainder_seconds_after_hours % 60
    milliseconds = delta.microseconds // 1000

    return f"{hours:02d}:{minutes:02d}:{seconds_part:02d},{milliseconds:03d}"


def generate_srt_content(segment_timestamps: list) -> str:
    """Generates SRT formatted string from segment timestamps."""
    srt_content = []
    for i, ts in enumerate(segment_timestamps):
        start_time = format_srt_time(ts['start'])
        end_time = format_srt_time(ts['end'])
        text = ts['segment']
        srt_content.append(str(i + 1))
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")
    return "\n".join(srt_content)


def file_processing(core: AppCore, file_struct: ProcessingFileStruct, req: ProcessingFileDirReq) -> ProcessingFileResp:
    options = core.plugin_options(plugin_name)

    global model
    if model is None:
        model = ASRModel.from_pretrained(model_name=options["model"])
        model.to(cuda.get_device_with_gpu_num(options))

    audio = AudioSegment.from_file(file_struct.path_file_in())
    # supports only one channel and 16 000 frame rate
    resampled_audio_file = f'{file_struct.path_out}{os.sep}{file_struct.file_name}_resampled.wav'
    audio.export(resampled_audio_file, format="wav", parameters=["-ar", "16000", "-ac", "1"])

    try:

        try: # canary model supports "source_lang", parapet model - doesn't
            transcribe = model.transcribe(audio=[resampled_audio_file], source_lang=req.from_lang, target_lang=req.from_lang,
                                          timestamps=True, batch_size=options["batch_size"])
        except Exception as possible_param_exc:
            if "argument 'source_lang'" in str(possible_param_exc) or "argument 'target_lang'" in str(possible_param_exc):
                logger.info("It seems the model " + options["model"] + " does not support source_lang / target_lang params. Result text wiil be in english. Try to repeat request without params.")
                transcribe = model.transcribe(audio=[resampled_audio_file],
                                                timestamps=True, batch_size=options["batch_size"])
            else:
                log.log_exception("Error transcribe.", possible_param_exc)
                transcribe = None

        if not transcribe or not isinstance(transcribe, list) or not transcribe[0] or not hasattr(transcribe[0], 'timestamp') or not transcribe[0].timestamp or 'segment' not in transcribe[0].timestamp:
            return file_processor.get_processing_file_resp_error(
                file_in=file_struct.file_name_ext, path_in=file_struct.path_in, error_msg="Can't get transcribe")

        segment_timestamps = transcribe[0].timestamp['segment'] # segment level timestamps
        if segment_timestamps:
            srt_content = generate_srt_content(segment_timestamps)

            out_file_name = processed_file_name(core=core, file_struct=file_struct, req=req)
            with open(file_struct.path_file_out(out_file_name), "w") as f:
                f.write(srt_content)
            if options["translate_after_processing"] and req.from_lang != req.to_lang:
                return translate_after_processing(core=core, req=req, file_name_ext=out_file_name)
            else:
                return file_processor.get_processing_file_resp_ok(file_struct=file_struct, file_out=out_file_name)
        else:
            return file_processor.get_processing_file_resp_error(
                file_in=file_struct.file_name_ext, path_in=file_struct.path_in, error_msg="Can't get segment timestamps")
    finally:
        if os.path.exists(resampled_audio_file):
            os.remove(resampled_audio_file)


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
            del model
        gc.collect()

        model = None

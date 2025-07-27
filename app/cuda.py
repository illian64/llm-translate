import logging

import torch

logger = logging.getLogger('uvicorn')


def cuda_info():
    cuda_is_available = torch.cuda.is_available()
    device_count = torch.cuda.device_count()
    current_device = torch.cuda.current_device()

    logger.info("CUDA info: is available={0}, device count={1}, current_device={2}. Devices:"
                .format(cuda_is_available, device_count, current_device))

    for i in range(device_count):
        logger.info("GPU #%d: %s", i, torch.cuda.get_device_name(i))


def get_device(options: dict):
    cuda_opt = options["cuda"]
    if cuda_opt:
        return "cuda"
    else:
        return "cpu"

def get_device_with_gpu_num(options: dict):
    cuda_opt = options["cuda"]
    if cuda_opt:
        return "cuda:{0}".format(options["cuda_device_index"])
    else:
        return "cpu"

import numpy as np
from enum import Enum

try:
    import cupy as cp
    _has_cuda = cp.cuda.is_available()
except ImportError:
    cp = None
    _has_cuda = False
    print("Cupy is not installed or no CUDA device is available. Falling back to NumPy.")


class Device(Enum):
    """Device types supported by NeuralEngine."""
    CPU = "cpu"
    CUDA = "cuda"


xp = np # Backend array provider. Default to NumPy
_current_device: Device = Device.CPU # Default device is CPU


def set_device(device: Device) -> None:
    """Sets the current device for tensor operations.
    @param device: The device to set, either Device.CPU or Device.CUDA
    """
    global xp, _current_device
    if device == Device.CPU:
        xp = np
    elif device == Device.CUDA:
        if not _has_cuda:
            raise RuntimeError("Cupy is not installed or no CUDA device is available.")
        xp = cp
    else:
        raise ValueError("device must be either Device.CPU or Device.CUDA")
    _current_device = device


def get_device() -> Device:
    """Returns the current device being used for tensor operations.
    @return: The current device, either Device.CPU or Device.CUDA
    """
    return _current_device


class DType():
    """Data types supported by NeuralEngine."""
    FLOAT16 = xp.float16
    FLOAT32 = xp.float32
    FLOAT64 = xp.float64
    INT8 = xp.int8
    INT16 = xp.int16
    INT32 = xp.int32
    INT64 = xp.int64
    UINT8 = xp.uint8
    UINT16 = xp.uint16
    UINT32 = xp.uint32
    UINT64 = xp.uint64
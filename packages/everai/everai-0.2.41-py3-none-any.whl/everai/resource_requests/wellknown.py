from enum import Enum


class CPU(Enum):
    Intel_I5 = 1
    Intel_I7 = 2
    Amd_XX = 30


class GPU(Enum):
    Nvidia_3090 = 1
    Nvidia_3090T = 2
    Nvidia_4090 = 3


class CUDA(Enum):
    CUDA_11_01 = 1


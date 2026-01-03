"""""" # start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'tmg_hmc.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

__version__ = "0.1.3"

try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

class _TensorPlaceholder(object):
        pass

def get_torch():
    if not _TORCH_AVAILABLE:
        return None
    return torch

def get_tensor_type():
    if not _TORCH_AVAILABLE:
        return _TensorPlaceholder
    return torch.Tensor

from .sampler import TMGSampler

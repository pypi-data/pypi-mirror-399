from typing import Literal
import logging

# TOML parsing:
# - Python 3.11+: `tomllib` (stdlib)
# - Python 3.10 and below: use `tomli` as a drop-in replacement
try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

logger = logging.getLogger("ostristraining")

GPU = Literal[
    "RTX 4090", "RTX 5090", "RTX 6000 Ada", "A40", "H100", "A100", "B200", "H200", "Unknown GPU"
]

class GPUMonitor:
    def __init__(self):
        # GPU monitoring is optional in this project.
        # We import NVML lazily because:
        # - some environments don't have it,
        # - `pynvml` is deprecated and can spam warnings,
        # - most workflows don't need GPU name detection.
        try:
            import pynvml  # type: ignore
        except ModuleNotFoundError as e:  # pragma: no cover
            raise RuntimeError(
                "GPU monitoring requires `pynvml` (or an NVML-compatible setup). "
                "Install it, or avoid using `GPUMonitor`."
            ) from e

        self._pynvml = pynvml

        self._pynvml.nvmlInit()
        self.gpu_count = self._pynvml.nvmlDeviceGetCount()
        self.gpu_name = self.get_gpu_name()
        self._pynvml.nvmlShutdown()

    def get_gpu_name(self) -> GPU:
        handle = self._pynvml.nvmlDeviceGetHandleByIndex(0)  # type: ignore
        name = self._pynvml.nvmlDeviceGetName(handle)  # type: ignore
        if isinstance(name, bytes):
            name = name.decode("utf-8")
        name = str(name)

        match name:
            case _ if "4090" in name:
                return "RTX 4090"
            case _ if "5090" in name:
                return "RTX 5090"
            case _ if "6000 Ada" in name:
                return "RTX 6000 Ada"
            case _ if "A40" in name:
                return "A40"
            case _ if "H100" in name:
                return "H100"
            case _ if "A100" in name:
                return "A100"
            case _ if "B200" in name:
                return "B200"
            case _ if "H200" in name:
                return "H200"
            case _:
                return "Unknown GPU"


class OstrisTraining:
    def __init__(self):
        print("OstrisTraining initialized")

    def train(self):
        pass
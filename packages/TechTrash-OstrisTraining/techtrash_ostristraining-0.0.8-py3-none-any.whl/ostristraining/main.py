from typing import Literal
import logging
from pathlib import Path
import tempfile
import os

# Local helpers.
from .dataset_utils import prepare_dataset_from_zip_url
from .config_utils import ConfigContext, apply_config_overrides

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
    def __init__(self, user_name: str, absolute_path_ostris: str, absolute_path_racine: str, gender: Literal["woman", "man"]):
        self.user_name = user_name
        self.absolute_path_ostris = absolute_path_ostris
        self.absolute_path_ostris_dataset_folder = os.path.join(self.absolute_path_ostris, "dataset", self.user_name)
        self.gender = gender
        self.path_racine = absolute_path_racine
        # Default location for the user's config file.
        # We keep this deterministic so every run for the same user lands in the same place.
        self.absolute_path_config_yaml = os.path.join(self.path_racine, f"config-{self.user_name}.yaml")

        print("================================================")
        print(f"OstrisTraining initialized for user {self.user_name}")
        print("================================================")

    def _create_config_file(self, config_yaml_content: object):
        """
        Create (or overwrite) the YAML config file for this user.

        The API caller provides the YAML content as a string, and we persist it
        to disk so downstream training code can read it from disk.

        Notes:
        - We create parent directories if they don't exist.
        - We write atomically (temp file + replace) to avoid partial files.
        - We always write UTF-8 text with a trailing newline for POSIX friendliness.
        """
        if not isinstance(config_yaml_content, str):
            # Keep the error clear for API callers: they can fix their payload.
            raise TypeError("config_yaml_content must be a str containing YAML text.")

        # Central place to patch/override config behavior.
        # Today this mostly supports placeholders and optional overrides.
        # Later we will implement your exact "auto edits" here without touching
        # the rest of the training pipeline.
        config_context = ConfigContext(
            user_name=self.user_name,
            absolute_path_ostris=self.absolute_path_ostris,
            absolute_path_racine=self.path_racine,
            absolute_path_dataset_folder=self.absolute_path_ostris_dataset_folder,
            absolute_path_config_yaml=self.absolute_path_config_yaml,
            gender=self.gender,
        )
        config_yaml_content = apply_config_overrides(
            config_yaml_content=config_yaml_content,
            context=config_context,
            overrides=None,  # add dotted-path overrides here later if needed
        )

        target_path = Path(self.absolute_path_config_yaml).expanduser()
        if not target_path.is_absolute():
            # We expect `absolute_path_racine` to be absolute, so this should not happen.
            # But we keep this check to avoid writing files in surprising locations.
            raise ValueError(
                f"absolute_path_config_yaml must be an absolute path. Got: {self.absolute_path_config_yaml}"
            )

        # Ensure the folder exists (e.g. .../runs/xyz/config.yaml).
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Make the file slightly nicer to inspect in terminals by ensuring newline at EOF.
        content_to_write = config_yaml_content
        if content_to_write and not content_to_write.endswith("\n"):
            content_to_write += "\n"

        # Atomic write:
        # - write to a temp file in the same directory
        # - fsync to reduce chance of losing the file in sudden shutdowns
        # - replace the target (atomic on POSIX filesystems)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=str(target_path.parent),
            prefix=f".{target_path.name}.",
            suffix=".tmp",
        ) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(content_to_write)
            tmp.flush()
            try:
                os.fsync(tmp.fileno())
            except Exception:  # pragma: no cover
                pass

        tmp_path.replace(target_path)
        logger.info("Wrote config YAML to %s (%d bytes)", str(target_path), len(content_to_write))
        return str(target_path)

    def _create_dataset_folder(self, url_zip_dataset: str):
        """
        Download a public ZIP dataset and normalize it for Ostris training.

        Expected ZIP content (root of the zip):
        - images (png/jpg/...) + matching captions (txt) with same base name
          e.g. photobelle.png + photobelle.txt

        Output folder (`self.absolute_path_ostris_dataset_folder`):
        - image_0.<ext> + image_0.txt
        - image_1.<ext> + image_1.txt
        ...
        """
        imported_pairs, skipped_images_without_caption = prepare_dataset_from_zip_url(
            url_zip_dataset=url_zip_dataset,
            output_dir=self.absolute_path_ostris_dataset_folder,
        )
        logger.info(
            "Prepared dataset in %s (imported_pairs=%d, skipped_images_without_caption=%d)",
            self.absolute_path_ostris_dataset_folder,
            imported_pairs,
            skipped_images_without_caption,
        )
        # No return: this method's job is to create the dataset on disk.
        return None


    def _train_model(self) -> str:
        """
        Train the model using the Ostris AI-Toolkit.
        """
        print("================================================")
        print("Training the model...")
        print("================================================")
        return "path/to/the/trained/model.safetensors"

    def train(self, url_zip_dataset: str, config_yaml_content: str) -> str:
        self._create_dataset_folder(url_zip_dataset)
        self._create_config_file(config_yaml_content)
        
        return self._train_model()
## Libs-Ostris (TechTrash_OstrisTraining)

This package provides a small Python wrapper around an Ostris training workflow.

The main entrypoint is **`OstrisTraining.train()`**.

### What `train()` does

- **Download + prepare dataset** from a public ZIP URL
  - ZIP root must contain image files + matching caption files (`.txt`)
  - Example pair: `photobelle.png` + `photobelle.txt`
  - Output: files are normalized to `image_0.<ext>`, `image_0.txt`, `image_1.<ext>`, `image_1.txt`, ...
- **Write config YAML** from a string into a deterministic file:
  - `{absolute_path_racine}/config-{user_name}.yaml`
  - Before writing, we **patch the YAML automatically**:
    - `config.name` is forced to `user_name`
    - `config.process[*].datasets[*].folder_path` is forced to the prepared dataset folder
    - `config.process[*].trigger_word` is forced to:
      - `"ohwx woman"` if `gender="woman"`
      - `"ohwx man"` if `gender="man"`
- **Run training**
  - Calls `run.py` inside `absolute_path_ostris` with the generated config path
- **Cleanup on success**
  - Deletes the prepared dataset folder + generated config yaml
  - Keeps the produced `.safetensors` model file

### Install (local dev)

From this folder:

```bash
pip install -e .
```

### Usage (recommended)

The best reference is `src/ostristraining/example.py`.

You can run it directly after installing:

```bash
python3 -m ostristraining.example
```

Or copy/paste this minimal usage:

```python
from ostristraining.main import OstrisTraining

trainer = OstrisTraining(
    user_name="demo_user",
    absolute_path_ostris="/tmp/ostris_project",
    absolute_path_racine="/tmp/ostris_runs",
    gender="woman",  # "woman" or "man"
    absolute_path_output="/tmp/ostris_output",
)

# Public ZIP URL containing images + captions at the ZIP root.
url_zip_dataset = "https://example.com/dataset.zip"

# YAML config must be a STRING. Newlines + indentation matter in YAML.
# Tip: start from `src/ostristraining/example_config.yaml` and customize it.
config_yaml_content = """
job: "extension"
config:
  name: "will_be_overwritten"
  process:
    - type: "diffusion_trainer"
      trigger_word: "will_be_overwritten"
      datasets:
        - folder_path: "will_be_overwritten"
"""

trained_model_path = trainer.train(
    url_zip_dataset=url_zip_dataset,
    config_yaml_content=config_yaml_content,
)

print(trained_model_path)
```

### Logging

This library uses Python `logging` (logger name: `ostristraining`).

In your app/handler you typically enable logs like:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Dataset ZIP format (important)

At the **root of the ZIP**, you must have:

- images: `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif`
- captions: `.txt`

And each image must have a caption with the **same base name**:

- `photo001.png` + `photo001.txt`
- `photo002.jpg` + `photo002.txt`

If an image has no matching `.txt`, it is **skipped**.

### Config patching rules (quick recap)

If you send a config similar to `src/ostristraining/example_config.yaml`, the library will ensure:

- `config.name == user_name`
- `config.process[*].datasets[*].folder_path == {absolute_path_ostris}/dataset/{user_name}`
- `config.process[*].trigger_word == "ohwx woman" | "ohwx man"` based on `gender`

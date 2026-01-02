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
- **Run training**
  - Currently `_train_model()` is a stub in `main.py` (replace with real training call)

### Install (local dev)

From this folder:

```bash
pip install -e .
```

### Usage (recommended)

The best reference is `src/ostristraining/example.py`.

You can run it directly after installing:

```bash
python -m ostristraining.example
```

Or copy/paste this minimal usage:

```python
from ostristraining.main import OstrisTraining

trainer = OstrisTraining(
    user_name="demo_user",
    absolute_path_ostris="/tmp/ostris_project",
    absolute_path_racine="/tmp/ostris_runs",
)

# Public ZIP URL containing images + captions at the ZIP root.
url_zip_dataset = "https://example.com/dataset.zip"

# YAML config must be a STRING. Newlines + indentation matter in YAML.
config_yaml_content = \"\"\"\
model:
  name: my_model
training:
  steps: 1000
\"\"\"

trained_model_path = trainer.train(
    url_zip_dataset=url_zip_dataset,
    config_yaml_content=config_yaml_content,
)

print(trained_model_path)
```

### Dataset ZIP format (important)

At the **root of the ZIP**, you must have:

- images: `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif`
- captions: `.txt`

And each image must have a caption with the **same base name**:

- `photo001.png` + `photo001.txt`
- `photo002.jpg` + `photo002.txt`

If an image has no matching `.txt`, it is **skipped**.


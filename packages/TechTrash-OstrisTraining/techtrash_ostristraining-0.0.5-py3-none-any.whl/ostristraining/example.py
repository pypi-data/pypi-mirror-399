"""
Example usage for `OstrisTraining`.

Goal: call `train()` with:
- a public URL to a ZIP dataset
- a YAML config as a string

This file is meant to be copy-pasted and adapted.
"""

from __future__ import annotations

import os

from ostristraining.main import OstrisTraining


def main() -> None:
    # You can hardcode these values, or pass them via env vars.
    # We default to /tmp paths to keep the example safe to run locally.
    user_name = os.getenv("OSTRIS_USER_NAME", "demo_user")
    absolute_path_ostris = os.getenv("OSTRIS_ABSOLUTE_PATH_OSTRIS", "/tmp/ostris_project")
    absolute_path_racine = os.getenv("OSTRIS_ABSOLUTE_PATH_RACINE", "/tmp/ostris_runs")

    # Public ZIP URL containing images + captions at the ZIP root.
    # Example:
    # - photobelle.png
    # - photobelle.txt
    url_zip_dataset = os.getenv("OSTRIS_URL_ZIP_DATASET", "https://example.com/dataset.zip")

    # YAML config sent by your API as a STRING.
    # Important: YAML relies on indentation + newlines.
    config_yaml_content = """\
# Minimal example config (replace with the real Ostris AI-Toolkit config)
model:
  name: my_model
dataset:
  folder: dataset/demo_user
training:
  steps: 1000
"""

    trainer = OstrisTraining(
        user_name=user_name,
        absolute_path_ostris=absolute_path_ostris,
        absolute_path_racine=absolute_path_racine,
    )

    # This will:
    # - download/extract the ZIP into: {absolute_path_ostris}/dataset/{user_name}
    # - create the YAML config into:   {absolute_path_racine}/config-{user_name}.yaml
    # - run the training (currently a stub returning a placeholder path)
    trained_model_path = trainer.train(
        url_zip_dataset=url_zip_dataset,
        config_yaml_content=config_yaml_content,
    )

    print("================================================")
    print("Training finished.")
    print(f"Trained model path: {trained_model_path}")
    print("================================================")


if __name__ == "__main__":
    main()


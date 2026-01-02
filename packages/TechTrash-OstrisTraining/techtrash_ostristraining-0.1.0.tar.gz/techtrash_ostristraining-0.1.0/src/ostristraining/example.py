"""
Example usage for `OstrisTraining`.

Goal: call `train()` with:
- a public URL to a ZIP dataset
- a YAML config as a string

This file is meant to be copy-pasted and adapted.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Literal, cast

from ostristraining.main import OstrisTraining


def main() -> None:
    # Configure logs for the example run.
    # In production you will usually configure logging in your app/handler instead.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    # You can hardcode these values, or pass them via env vars.
    # We default to /tmp paths to keep the example safe to run locally.
    user_name = os.getenv("OSTRIS_USER_NAME", "demo_user")
    absolute_path_ostris = os.getenv("OSTRIS_ABSOLUTE_PATH_OSTRIS", "/tmp/ostris_project")
    absolute_path_racine = os.getenv("OSTRIS_ABSOLUTE_PATH_RACINE", "/tmp/ostris_runs")
    absolute_path_output = os.getenv("OSTRIS_ABSOLUTE_PATH_OUTPUT", "/tmp/ostris_output")
    # Keep this explicitly typed for type-checkers.
    # Valid values: "woman" or "man".
    gender_env = os.getenv("OSTRIS_GENDER", "woman").strip().lower()
    if gender_env not in {"woman", "man"}:
        raise ValueError("OSTRIS_GENDER must be 'woman' or 'man'.")
    gender: Literal["woman", "man"] = cast(Literal["woman", "man"], gender_env)

    # Public ZIP URL containing images + captions at the ZIP root.
    # Example:
    # - photobelle.png
    # - photobelle.txt
    url_zip_dataset = os.getenv("OSTRIS_URL_ZIP_DATASET", "https://example.com/dataset.zip")

    # YAML config sent by your API as a STRING.
    # Recommended: start from `example_config.yaml` and customize it.
    #
    # Note: when INSTALLED as a wheel, the template file must be included as package data.
    # We handle that in `pyproject.toml`.
    template_path = Path(__file__).with_name("example_config.yaml")
    config_yaml_content = template_path.read_text(encoding="utf-8")

    trainer = OstrisTraining(
        user_name=user_name,
        absolute_path_ostris=absolute_path_ostris,
        absolute_path_racine=absolute_path_racine,
        gender=gender,  # "woman" or "man"
        absolute_path_output=absolute_path_output,
    )

    # This will:
    # - download/extract the ZIP into: {absolute_path_ostris}/dataset/{user_name}
    # - create the YAML config into:   {absolute_path_racine}/config-{user_name}.yaml
    # - patch config values:
    #   - config.name -> user_name
    #   - config.process[*].datasets[*].folder_path -> dataset folder
    #   - config.process[*].training_folder -> absolute_path_output
    #   - config.process[*].trigger_word -> "ohwx woman"|"ohwx man"
    # - run the training (calls `run.py` inside `absolute_path_ostris`)
    trained_model_path = trainer.train(
        url_zip_dataset=url_zip_dataset,
        config_yaml_content=config_yaml_content,
    )

    logging.getLogger("ostristraining.example").info("Training finished. Model: %s", trained_model_path)


if __name__ == "__main__":
    main()


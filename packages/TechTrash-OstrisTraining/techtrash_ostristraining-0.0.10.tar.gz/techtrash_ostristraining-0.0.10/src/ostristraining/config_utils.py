"""
Config utilities for Ostris training.

Why this file exists
--------------------
Users send a `config.yaml` content as a STRING from an API.
In practice we often need to "patch" that YAML before training:
- inject absolute paths (dataset folder, output folder, etc.)
- enforce some defaults
- override a few keys depending on the runtime environment

We keep this logic isolated here so:
- `main.py` stays simple,
- Serverless/Pod/local runs share the exact same behavior,
- it's easy to unit-test later (pure string in -> string out).
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

Gender = str  # expected values: "woman" | "man"


@dataclass(frozen=True)
class ConfigContext:
    """
    Small set of values that are frequently needed when patching configs.

    Feel free to add fields as your training pipeline grows.
    """

    user_name: str
    absolute_path_ostris: str
    absolute_path_racine: str
    absolute_path_dataset_folder: str
    absolute_path_config_yaml: str
    gender: Gender


def _apply_placeholders(yaml_text: str, context_map: dict[str, str]) -> str:
    """
    Replace simple placeholders in a YAML string.

    Supported placeholder formats:
    - `${KEY}`
    - `{{KEY}}` or `{{ KEY }}` (spaces allowed)

    This is intentionally conservative. It does NOT try to parse YAML.
    It just does string replacement, which is very safe and dependency-free.
    """
    out = yaml_text
    for key, value in context_map.items():
        out = out.replace(f"${{{key}}}", value)
        # Important: do NOT use `str.format()` here.
        # This regex intentionally contains "{" / "}" to match the template markers `{{ ... }}`,
        # and `format()` would treat them as formatting tokens and can crash with:
        #   ValueError: unexpected '{' in field name
        placeholder_pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
        out = re.sub(placeholder_pattern, value, out)
    return out


def _maybe_yaml_module():
    """
    Optional dependency: PyYAML.

    We do not list it as a hard dependency here because some environments may already
    provide it (e.g. AI-toolkit images), and some may not.
    """
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return None
    return yaml


def _deep_set(mapping: dict[str, Any], dotted_path: str, value: Any) -> None:
    """
    Set a nested dict key using a dotted path, creating intermediate dicts.

    Example:
      _deep_set(data, "training.steps", 1000)
    """
    parts = [p for p in dotted_path.split(".") if p]
    if not parts:
        raise ValueError("Override key cannot be empty.")

    cur: dict[str, Any] = mapping
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt

    cur[parts[-1]] = value


def apply_config_overrides(
    *,
    config_yaml_content: object,
    context: ConfigContext,
    overrides: dict[str, Any] | None = None,
) -> str:
    """
    Apply "patching" logic to a YAML config string and return the patched YAML string.

    Today this function provides:
    - placeholder substitution (works without any YAML library)
    - optional dotted-path overrides (requires PyYAML to parse + dump YAML)

    Later, when you tell me your exact rules, we will implement them HERE.
    This keeps the rest of the codebase unchanged.
    """
    if not isinstance(config_yaml_content, str):
        raise TypeError("config_yaml_content must be a str containing YAML text.")

    # 1) Always do placeholder substitution first.
    #    This is useful if the user sends something like:
    #      dataset_dir: "{{ABSOLUTE_PATH_DATASET_FOLDER}}"
    # Trigger word logic: your current convention is:
    # - woman -> "ohwx woman"
    # - man   -> "ohwx man"
    if context.gender == "woman":
        trigger_word = "ohwx woman"
    elif context.gender == "man":
        trigger_word = "ohwx man"
    else:
        raise ValueError(f"gender must be 'woman' or 'man'. Got: {context.gender!r}")

    context_map = {
        "USER_NAME": context.user_name,
        "ABSOLUTE_PATH_OSTRIS": context.absolute_path_ostris,
        "ABSOLUTE_PATH_RACINE": context.absolute_path_racine,
        "ABSOLUTE_PATH_DATASET_FOLDER": context.absolute_path_dataset_folder,
        "ABSOLUTE_PATH_CONFIG_YAML": context.absolute_path_config_yaml,
        "TRIGGER_WORD": trigger_word,
    }
    patched_yaml = _apply_placeholders(config_yaml_content, context_map)

    # 2) Your config edits are easiest + safest by parsing YAML.
    #    If PyYAML is missing, we can *only* support placeholder-based configs.
    yaml = _maybe_yaml_module()
    if yaml is None:
        # If the user relied on placeholders, we can still succeed without parsing.
        # Otherwise we must fail, because updating nested list fields safely without
        # a YAML parser is brittle.
        placeholder_hint_tokens = (
            "ABSOLUTE_PATH_DATASET_FOLDER",
            "USER_NAME",
            "TRIGGER_WORD",
        )
        if any(tok in config_yaml_content for tok in placeholder_hint_tokens):
            return patched_yaml

        raise RuntimeError(
            "PyYAML is required to patch this config automatically (it edits nested fields like "
            "`config.process[].datasets[].folder_path`). Install `pyyaml`, or use placeholders like:\n"
            '- folder_path: "{{ABSOLUTE_PATH_DATASET_FOLDER}}"\n'
            '- name: "{{USER_NAME}}"\n'
            '- trigger_word: "{{TRIGGER_WORD}}"'
        )

    loaded = yaml.safe_load(patched_yaml)
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise ValueError("Top-level YAML must be a mapping (dict) to apply overrides.")

    # 3) Apply your current fixed rules (based on example_config.yaml):
    # - config.name -> user_name
    # - config.process[*].trigger_word -> depends on gender
    # - config.process[*].datasets[*].folder_path -> absolute dataset folder
    cfg = loaded.get("config")
    if not isinstance(cfg, dict):
        cfg = {}
        loaded["config"] = cfg

    cfg["name"] = context.user_name

    process_list = cfg.get("process")
    if isinstance(process_list, list):
        for proc in process_list:
            if not isinstance(proc, dict):
                continue

            # Update trigger word on each process item that supports it.
            proc["trigger_word"] = trigger_word

            datasets = proc.get("datasets")
            if isinstance(datasets, list):
                for ds in datasets:
                    if not isinstance(ds, dict):
                        continue
                    ds["folder_path"] = context.absolute_path_dataset_folder

    # 4) Optional: user-specified overrides (dotted-path) go last.
    if overrides:
        for dotted_key, value in overrides.items():
            _deep_set(loaded, dotted_key, value)

    # Dump back to YAML. We keep unicode so paths like 'qualité' are readable.
    dumped = yaml.safe_dump(loaded, sort_keys=False, allow_unicode=True)
    return dumped



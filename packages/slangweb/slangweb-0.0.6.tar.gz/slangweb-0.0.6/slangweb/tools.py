"""Utility functions for slangweb."""

import ast
import json
import logging
import os
from pathlib import Path

from .constants import LOOKUPS_FOLDER, MODELS_FOLDER, MODELS_LOOKUP_FILE, SLANG_FOLDER

logger = logging.getLogger(__name__)


def read_config(folder: str = SLANG_FOLDER, relative_to: Path | None = None) -> dict:
    """Read the config file from the specified folder.

    Args:
        folder (str): Folder where the config file is located.
        relative_to (Path | None): Path to which the folder is relative. If None, uses current working directory.

    Returns:
        dict: Configuration dictionary.
    """
    here = Path(relative_to or os.getcwd())
    config_file = here / folder / "config.json"
    if not config_file.exists():
        logger.error(
            f"Config file '{config_file}' does not exist. Create it first by running 'slangweb create-config'."
        )
        return {}
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    return {
        "models_lookup_file": here / folder / config.get("models_lookup_file", MODELS_LOOKUP_FILE),
        "models_folder": here / folder / config.get("models_folder", MODELS_FOLDER),
        "lookups_folder": here / folder / config.get("lookups_folder", LOOKUPS_FOLDER),
        "default_language": config.get("default_language", "en"),
        "encoding": config.get("encoding", "utf-8"),
        "source_folders": config.get("source_folders", ["."]),
        "supported_languages": config.get("supported_languages", ["es"]),
        "translator_class": config.get("translator_class", "SW"),
    }


def get_model_folder(model_name: str) -> str:
    """Get the name of the model folder for the given model name.

    Args:
        model_name (str): Name of the model.
    """
    return f"models--{model_name.replace('/', '--')}"


def available_languages(models_lookup_file: Path, models_folder: Path) -> dict[str, str]:
    """Return a list of available languages based on existing lookup files and model existence.

    Args:
        models_lookup_file (Path): Path to the models lookup file.
        models_folder (Path): Path to the models folder.
    """
    if not models_lookup_file.exists():
        logger.error(
            f"Models lookup file '{models_lookup_file}' does not exist. Create it by running 'slangweb generate-models-lookup-file'."
        )
        return {}
    with open(models_lookup_file, "r", encoding="utf-8") as f:
        models_lookup = json.load(f)
    languages = []
    lang_expanded = []
    for language, data in models_lookup.items():
        file = data.get("model")
        if not file:
            continue
        lang_expanded.append(data.get("name", language))
        model_folder = get_model_folder(file)
        model_path = models_folder / model_folder
        if model_path.exists() and model_path.is_dir():
            languages.append(language)
    return dict(zip(languages, lang_expanded))


def find_translator_usages(py_file: Path, translator_class: str = "SW") -> list[str]:
    """Find usages of the Translator class in the given Python file.

    Args:
        py_file (Path): Path to the Python file to analyze.
        translator_class (str): Name of the translator class to look for. Default is "SW".
    """
    with open(py_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=py_file)
    usages = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and hasattr(node.func, "id")
            and node.func.id == translator_class
        ):
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Str):
                    usages.append(str(arg.s))
                elif isinstance(arg, ast.Name):
                    usages.append(str(arg.id))
                else:
                    usages.append(str(ast.dump(arg)))
    return usages

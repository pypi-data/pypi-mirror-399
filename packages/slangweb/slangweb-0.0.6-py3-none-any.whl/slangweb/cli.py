"""CLI entry point for slangweb package."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import click
from transformers import MarianMTModel, MarianTokenizer

from .constants import ENCODING, LOOKUPS_FOLDER, MODELS_FOLDER, MODELS_LOOKUP_FILE, SLANG_FOLDER
from .tools import available_languages, find_translator_usages, read_config
from .translator import Translator


@click.group()
def cli():
    """Translation Dev Tools CLI."""
    pass


def _create_config_file(folder: Path, overwrite: bool = False):
    """Create the config file in the specified folder.

    Args:
        folder (Path): Folder where to create the config file.
        overwrite (bool): Whether to overwrite existing config file.
    """
    folder.mkdir(parents=True, exist_ok=True)
    source_folders = ["."]
    # exclude hidden folders, __pycache__, docs, tests, etc.
    exclude_folders = {folder.name, "__pycache__", "docs", "tests", "dist", "venv"}
    for item in os.listdir(folder):
        item_path = folder / item
        if item_path.is_dir() and item not in exclude_folders and not item.startswith("."):
            source_folders.append(item)
    config = {
        "models_lookup_file": MODELS_LOOKUP_FILE,
        "models_folder": MODELS_FOLDER,
        "lookups_folder": LOOKUPS_FOLDER,
        "default_language": "en",
        "encoding": ENCODING,
        "source_folders": source_folders,
        "supported_languages": ["es"],
        "translator_class": "SW",
    }
    config_file = folder / "config.json"
    if config_file.exists() and not overwrite:
        click.echo(
            f"Configuration file already exists at '{config_file}'. Use overwrite=True to overwrite."
        )
        return
    with open(config_file, "w", encoding=ENCODING) as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    click.echo(f"Configuration file created at '{config_file}'")


@cli.command()
@click.argument("folder", default=SLANG_FOLDER, type=str)
@click.option("--overwrite", is_flag=True, help="Overwrite existing config file if it exists.")
def create_config(folder, overwrite):
    """Create the config file in the specified folder, relative to the current working directory.

    The configuration file contains the following structure:

    {
        "models_lookup_file": "models_lookup.json",
        "models_folder": "models",
        "lookups_folder": "lookups",
        "default_language": "en",
        "encoding": "utf-8",
        "source_folders": ["."], # you can modify
        "supported_languages": ["es"], # you can modify
        "translator_class": "SW"
    }
    """
    # this command MUST be run in the project root folder
    here = Path(os.getcwd())
    _create_config_file(here / folder, overwrite)


def _create_models_lookup_file(output_file: Path, overwrite: bool = False):
    """Create a models lookup file with predefined content."""
    content = {
        "fr": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "French"},
        "fr_be": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "French (Belgium)"},
        "fr_ch": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "French (Switzerland)"},
        "fr_ca": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "French (Canada)"},
        "fr_fr": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "French (France)"},
        "wa": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Walloon"},
        "frp": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Arpitan"},
        "oc": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Occitan"},
        "ca": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Catalan"},
        "rm": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Romansh"},
        "lld": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Ladin"},
        "fur": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Friulian"},
        "lij": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Ligurian"},
        "lmo": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Lombard"},
        "es": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish"},
        "es_ar": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Argentina)"},
        "es_cl": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Chile)"},
        "es_co": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Colombia)"},
        "es_cr": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Costa Rica)"},
        "es_do": {
            "model": "Helsinki-NLP/opus-mt-en-ROMANCE",
            "name": "Spanish (Dominican Republic)",
        },
        "es_ec": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Ecuador)"},
        "es_es": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Spain)"},
        "es_gt": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Guatemala)"},
        "es_hn": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Honduras)"},
        "es_mx": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Mexico)"},
        "es_ni": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Nicaragua)"},
        "es_pa": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Panama)"},
        "es_pe": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Peru)"},
        "es_pr": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Puerto Rico)"},
        "es_sv": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (El Salvador)"},
        "es_uy": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Uruguay)"},
        "es_ve": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Spanish (Venezuela)"},
        "pt": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Portuguese"},
        "pt_br": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Portuguese (Brazil)"},
        "pt_pt": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Portuguese (Portugal)"},
        "gl": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Galician"},
        "lad": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Ladino"},
        "an": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Aragonese"},
        "mwl": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Mirandese"},
        "it": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Italian"},
        "it_it": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Italian (Italy)"},
        "co": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Corsican"},
        "nap": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Neapolitan"},
        "scn": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Sicilian"},
        "vec": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Venetian"},
        "sc": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Sardinian"},
        "ro": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Romanian"},
        "la": {"model": "Helsinki-NLP/opus-mt-en-ROMANCE", "name": "Latin"},
    }
    if output_file.exists() and not overwrite:
        click.echo(
            f"Models lookup file already exists at '{output_file}'. Use overwrite=True to overwrite."
        )
        return
    with open(output_file, "w", encoding=ENCODING) as f:
        json.dump(content, f, indent=4, ensure_ascii=False)
    click.echo(f"Models lookup file created at '{output_file}'")


@cli.command()
@click.argument("folder", default=SLANG_FOLDER, type=str)
@click.option(
    "--overwrite", is_flag=True, help="Overwrite existing models lookup file if it exists."
)
def create_models_lookup_file(folder: str = SLANG_FOLDER, overwrite: bool = False):
    """Generate models lookup file.

    The location and name of the file will be taken from the config file if provided.
    """
    config = read_config(folder)
    _create_models_lookup_file(config["models_lookup_file"], overwrite)


@cli.command()
@click.argument("folder", default=SLANG_FOLDER, type=str)
def init(folder: str = SLANG_FOLDER):
    """Initialize the slangweb project structure."""
    here = Path(os.getcwd())
    folder_path = here / folder
    _create_config_file(folder_path, overwrite=False)
    config = read_config(folder)
    _create_models_lookup_file(config["models_lookup_file"], overwrite=False)
    (folder_path / LOOKUPS_FOLDER).mkdir(parents=True, exist_ok=True)
    (folder_path / MODELS_FOLDER).mkdir(parents=True, exist_ok=True)
    click.echo(f"Initialized slangweb project structure in folder '{folder}'.")


def _available_languages(folder: str = SLANG_FOLDER) -> dict[str, str]:
    """Return a list of available languages with downloaded models."""
    config = read_config(folder)
    return available_languages(config["models_lookup_file"], config["models_folder"])


@cli.command()
@click.option(
    "--folder",
    default=SLANG_FOLDER,
    required=False,
    help="Folder where the config file is located.",
)
def list_languages(folder):
    """List available languages with downloaded models."""
    languages = _available_languages(folder)
    if not languages:
        click.echo("No languages with downloaded models found.")
        return
    click.echo("Available languages with downloaded models:")
    for lang, expanded in languages.items():
        click.echo(f"- {lang} ({expanded})")


def _download_model(language: str, config: dict):
    """Download a translation model by name (HuggingFace)."""
    with open(config["models_lookup_file"], "r", encoding="utf-8") as f:
        models_lookup = json.load(f)
    model_data = models_lookup.get(language)
    if not model_data:
        click.echo(f"Unsupported language code: {language}", err=True)
        sys.exit(1)
    model_name = model_data.get("model")
    lang = model_data.get("name", language)
    click.echo(f"Downloading model '{model_name}' for language '{language} ({lang})'...")
    MarianMTModel.from_pretrained(model_name, cache_dir=config["models_folder"])
    MarianTokenizer.from_pretrained(model_name, cache_dir=config["models_folder"])


@cli.command()
@click.option(
    "--folder",
    default=SLANG_FOLDER,
    required=False,
    help="Folder where the config file is located.",
)
def download_models(folder):
    """Download a translation model by name (HuggingFace)."""
    config = read_config(folder)
    supported_languages = config.get("supported_languages", [])
    with open(config["models_lookup_file"], "r", encoding="utf-8") as f:
        models_lookup = json.load(f)
    languages = [lang for lang in models_lookup.keys() if lang in supported_languages]
    print(languages)
    for language in languages:
        _download_model(language, config)


def _sync(file: Path, language: str, config: dict) -> None:
    """Sync translations found in the given Python file."""
    if not file.exists():
        click.echo(f"File or folder '{file}' does not exist.", err=True)
        return None
    if not file.is_file():
        click.echo(f"Only Python files are supported. '{file}' is not a file.", err=True)
        return None
    if file.suffix != ".py":
        click.echo(f"Only Python files are supported. '{file}' is not a Python file.", err=True)
        return None
    click.echo(f"Syncing translations in: {file}")
    SW = Translator(base_folder=config.get("base_folder", SLANG_FOLDER))
    to_translate = find_translator_usages(file, config.get("translator_class", "SW"))
    click.echo(f"Translations for language '{language}':")
    SW.set_language(language)
    if SW.can_be_translated():
        for text in to_translate:
            translation = SW(text)
            click.echo(f"- {text} => {translation}")
    return None


@cli.command()
@click.argument("file", default=None, required=False, type=str)
@click.option(
    "--folder",
    default=SLANG_FOLDER,
    required=False,
    help="Folder where the config file is located.",
)
def sync(file, folder):
    """Sync translations found in the given Python file."""
    here = Path(os.getcwd())
    config = read_config(folder)
    languages = _available_languages(folder).keys()
    supported_languages = config.get("supported_languages", [])
    languages = [lang for lang in languages if lang in supported_languages]
    for lang in languages:
        if file is None:
            # Sync all Python files in the source folders
            for fold in config.get("source_folders", []):
                folder_path = here / fold
                print(folder_path)
                if not folder_path.exists() or not folder_path.is_dir():
                    click.echo(
                        f"Source folder '{folder_path}' does not exist or is not a directory.",
                        err=True,
                    )
                    continue
                for item in folder_path.glob("*.py"):
                    _sync(item, lang, config)
        else:
            file = here / file
            if not file.exists():
                click.echo(f"File or folder '{file}' does not exist.", err=True)
                sys.exit(1)
            if file.is_file() and file.suffix != ".py":
                click.echo(f"File '{file}' is not a Python file.", err=True)
                sys.exit(1)
            _sync(file, lang, config)


@cli.command()
def create_flask_example():
    """Create a Flask example file.

    This command will create a folder called 'slangweb_flask_example' in the current working directory,
    containing a simple Flask application that demonstrates how to use the slangweb Translator class.
    """
    here = Path(os.getcwd())
    example_folder = here / "slangweb_flask_example"
    example_folder.mkdir(parents=True, exist_ok=True)
    # copy the flask_example.py content
    # flask_example_path = example_folder / "flask_example.py"
    # with open(flask_example_path, 'w', encoding='utf-8') as f:
    #     f.write(flask_example)
    shutil.copy(
        Path(__file__).parent / "examples" / "flask_example.py", example_folder / "flask_example.py"
    )
    click.echo(f"Flask example created at '{example_folder / 'flask_example.py'}'")


@cli.command()
@click.argument("example_name")
def install_example(example_name):
    """Install an example from the repository.

    This command downloads the specified example from the slangweb GitHub repository
    and installs it in the current working directory.

    EXAMPLE_NAME: The name of the example to install (e.g., 'dash').
    """
    repo_url = "https://github.com/fitoprincipe/slangweb.git"
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repo shallowly
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, temp_dir],
                check=True,
                capture_output=True,
                text=True,
            )
            example_path = Path(temp_dir) / "examples" / example_name
            if not example_path.exists():
                click.echo(f"Example '{example_name}' not found in the repository.", err=True)
                return
            dest = Path.cwd() / f"slangweb_{example_name}_example"
            if dest.exists():
                click.echo(
                    f"Destination folder '{dest}' already exists. Please remove it first.", err=True
                )
                return
            shutil.copytree(example_path, dest)
            click.echo(f"Example '{example_name}' installed at '{dest}'")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to clone repository: {e.stderr}", err=True)
    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

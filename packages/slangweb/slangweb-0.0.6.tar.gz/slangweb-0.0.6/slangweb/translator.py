"""Translations in Dash applications.

Only translates from English to other languages for now.
"""

import json
import os
from logging import getLogger
from pathlib import Path

from transformers import MarianMTModel, MarianTokenizer

from .constants import (
    DEFAULT_LANGUAGE,
    ENCODING,
    SLANG_FOLDER,
)
from .tools import read_config

logger = getLogger(__name__)


def lang_from_path(path: str) -> str | None:
    """Extract the language code from the given URL path."""
    parts = (path or "").strip("/").split("/")
    return parts[0] if parts else DEFAULT_LANGUAGE


class Translator:
    """A simple translator class to manage translations."""

    def __init__(
        self,
        base_folder: str = SLANG_FOLDER,
        relative_to: Path | None = None,
    ):
        """Initialize the Translator.

        There are 2 kind of lookup files:
        1. Models lookup file: maps language codes to model names.
        2. Translation lookup files: per-language files that map source texts to translated texts.

        If the model lookup file does not exist, it must be created using the cli tool.

        >slangweb generate-models-lookup-file

        Args:
            base_folder (str): Base directory for slangweb data.
            relative_to (Path | None): Path to which the base folder is relative. If None, uses current working directory.
        """
        self.here = Path(relative_to or os.getcwd())
        self.language: str | None = None
        self.base_folder = self.here / base_folder
        self.config = read_config(base_folder, relative_to=self.here)
        self._models_lookup: dict | None = None
        self._translation_lookup_file: Path | None = None
        self._model = None
        self._tokenizer = None

    @property
    def models_folder(self) -> Path | None:
        """Get the models folder path."""
        folder = self.config.get("models_folder")
        if folder is None:
            logger.error("Models folder path is not set in the configuration.")
        return folder

    @property
    def lookup_folder(self) -> Path | None:
        """Get the lookup folder path."""
        folder = self.config.get("lookups_folder")
        if folder is None:
            logger.error("Lookups folder path is not set in the configuration.")
        return folder

    @property
    def models_lookup_file(self) -> Path | None:
        """Get the models lookup file path."""
        file = self.config.get("models_lookup_file")
        if file is None:
            logger.error("Models lookup file path is not set in the configuration.")
        return file

    @property
    def default_language(self) -> str:
        """Get the default language."""
        return self.config.get("default_language", DEFAULT_LANGUAGE)

    @property
    def models_lookup(self) -> dict:
        """Load the models configuration from the models file."""
        if self.models_lookup_file is None:
            return {}

        if not self.models_lookup_file.exists():
            logger.error(f"Models lookup file not found: {self.models_lookup_file}")
            return {}

        if self._models_lookup is None:
            try:
                with open(self.models_lookup_file, "r", encoding="utf-8") as f:
                    models = json.load(f)
            except Exception as e:
                logger.error(f"Error loading models lookup file: {e}")
                models = {}
            self._models_lookup = models

        return self._models_lookup

    def supported_languages(self) -> list[str]:
        """Get the list of supported languages.

        Gets the supported languages from the config file and checks the models lookup file.
        """
        supported = self.config.get("supported_languages", [])
        # Filter supported languages to those present in models lookup
        supported = [lang for lang in supported if lang in self.models_lookup]
        supported.append(self.default_language)
        return supported

    def set_language(self, language: str | None) -> None:
        """Set the current language for translation."""
        language = language.lower() if language else None

        if language not in self.supported_languages():
            logger.warning(f"Language '{language}' is not supported.")
            return None

        if self.language != language:
            self.language = language
            # reset model and tokenizer
            self._model = None
            self._tokenizer = None

    @property
    def language_name(self) -> str | None:
        """Get the language name for the current language."""
        name = self.models_lookup.get(self.language, {}).get("name")
        if not name:
            logger.warning(f"Language '{self.language}' not found in models lookup.")
        return name

    @property
    def model_name(self) -> str | None:
        """Get the model name for the current language."""
        model_name = self.models_lookup.get(self.language, {}).get("model")
        if not model_name:
            logger.warning(f"Language '{self.language}' not found in models lookup.")
        return model_name

    def is_language_in_lookup(self) -> bool:
        """Check if the current language is in the lookup file."""
        if self.language is None or self.language == DEFAULT_LANGUAGE:
            return False
        is_in_lookup = self.language in self.models_lookup
        if not is_in_lookup:
            logger.error(f"Language '{self.language}' not found in models lookup.")
        return is_in_lookup

    @property
    def model_filename(self) -> Path | None:
        """Get the model directory for the current language."""
        if self.model_name is None or self.models_folder is None:
            return None
        model_fn = self.models_folder / f"models--{self.model_name.replace('/', '--')}"
        return model_fn

    def is_model_available(self) -> bool:
        """Check if the model for the current language is available."""
        if self.model_filename is None:
            return False
        return self.model_filename.is_dir()

    @property
    def translation_lookup_file(self) -> Path | None:
        """Get the translation lookup file for the current language."""
        if self.lookup_folder is None:
            logger.error("Lookup folder is not set in the configuration.")
            return None
        fn = self.lookup_folder / f"{self.language}.json"
        if not fn.exists():
            logger.info(f"Creating new lookup file: {fn}")
            try:
                fn.parent.mkdir(parents=True, exist_ok=True)
                with open(fn, "w", encoding=ENCODING) as f:
                    json.dump({}, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error creating translation lookup file: {e}")
                return None
        return fn

    @property
    def translation_lookup(self) -> dict:
        """Get the translation lookup for the current language."""
        if self.translation_lookup_file is None:
            return {}
        try:
            with open(self.translation_lookup_file, "r", encoding=ENCODING) as f:
                lookup = json.load(f)
        except Exception as e:
            logger.error(f"Error loading translation lookup file: {e}")
            lookup = {}
        return lookup

    def get_tokenizer(self) -> MarianTokenizer | None:
        """Get the tokenizer for the current language."""
        if self._tokenizer is not None:
            return self._tokenizer

        if self.is_model_available() and self.is_language_in_lookup():
            self._tokenizer = MarianTokenizer.from_pretrained(
                self.model_name, cache_dir=self.models_folder, local_files_only=True
            )
            return self._tokenizer
        else:
            return None

    def get_model(self) -> MarianMTModel | None:
        """Get the translation model for the current language."""
        if self._model is not None:
            return self._model

        if self.is_model_available() and self.is_language_in_lookup():
            import torch

            # Disable low_cpu_mem_usage to avoid meta device
            self._model = MarianMTModel.from_pretrained(
                self.model_name,
                cache_dir=self.models_folder,
                local_files_only=True,
                dtype=torch.float32,
                low_cpu_mem_usage=False,
            )
            return self._model
        else:
            return None

    def can_be_translated(self) -> bool:
        """Check if the current language can be translated."""
        # config missing
        if not self.config:
            logger.error("Configuration not loaded properly.")
            return False

        # exit: no language set
        if self.language is None:
            logger.warning("No language set. Make sure to set it using 'set_language' method.")
            return False

        # exit: default language
        if self.language == DEFAULT_LANGUAGE:
            logger.info(f"Default language set ({self.language}), no translation needed.")
            return False

        # exit: language not in lookup
        if self.models_lookup_file is None:
            return False

        # exit: model lookup file missing
        if not self.models_lookup_file.exists():
            logger.error(
                f"Models lookup file not found: {self.models_lookup_file}. Create using the CLI application."
            )
            return False

        # exit: model not available
        if not self.is_model_available():
            logger.error(
                f"Model for language '{self.language}' not available. Download it using the CLI application."
            )
            return False

        return True

    def translate(self, text: str) -> str:
        """Translate the given text to the current language, directly using the model.

        Since this is the main function, check related to translation using the model will be performed here.

        Args:
            text (str): The text to translate.
        """
        if not self.can_be_translated():
            return text

        try:
            # translate using model
            tokenizer = self.get_tokenizer()
            model = self.get_model()
            if tokenizer is None or model is None:
                logger.error("Tokenizer or model not available for translation.")
                return text
            if self.model_name == "Helsinki-NLP/opus-mt-en-ROMANCE":
                # for romance languages, lowercase the text to improve results
                tgt_lang = f">>{self.language}<<"
                inputs = tokenizer(f"{tgt_lang} {text}", return_tensors="pt", padding=True)
            else:
                inputs = tokenizer(text, return_tensors="pt", padding=True)
            translated = model.generate(**inputs)
            tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
            translation = tgt_text[0] if tgt_text else ""
            return translation
        except Exception as e:
            logger.error(f"Error during translation: {e}")
            return text

    def get_translation_from_lookup(self, text: str) -> str | None:
        """Get translation from the lookup file.

        Since this is a main function, check related to the lookup file will be performed here.

        Args:
            text (str): The text to translate.
        """
        return self.translation_lookup.get(text)

    def save_translation(self, text: str, translated_text: str) -> None:
        """Save the translated text to the lookup file."""
        if self.translation_lookup_file is None:
            logger.error("Translation lookup file is not available.")
            return None
        with open(self.translation_lookup_file, "r", encoding=ENCODING) as f:
            lookup = json.load(f)
        lookup[text] = translated_text
        with open(self.translation_lookup_file, "w", encoding=ENCODING) as f:
            json.dump(lookup, f, indent=4, ensure_ascii=False)

    def get_translation(self, text: str) -> str:
        """Get translation from lookup or translate and save it to lookup.

        Args:
            text (str): The text to translate.
        """
        translation = self.get_translation_from_lookup(text)
        if translation == text:
            return text
        if translation is None:  # not found in lookup
            translation = self.translate(text)
            # update lookup file
            self.save_translation(text, translation)
        return translation

    def __call__(self, text: str) -> str:
        """Translate the given text using the translator instance."""
        return self.get_translation(text)

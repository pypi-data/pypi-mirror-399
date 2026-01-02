"""Test the tools module."""

from slangweb import tools


def test_get_model_folder():
    """Test get_model_folder function."""
    model_name = "Helsinki-NLP/opus-mt-en-ROMANCE"
    expected_folder = "models--Helsinki-NLP--opus-mt-en-ROMANCE"
    assert tools.get_model_folder(model_name) == expected_folder

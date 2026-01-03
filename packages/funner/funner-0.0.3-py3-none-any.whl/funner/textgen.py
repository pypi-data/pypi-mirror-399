"""
textgen functions help produce text using template and data (dict).

"""

import os
from pathlib import Path

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader, BaseLoader


def generate_from_string(template_string: str, template_data: dict) -> str:
    """Render together template and data using Jinja2 way.
    """
    template = Environment(loader=BaseLoader()).from_string(template_string)
    return template.render(template_data)


def generate_from_file(template_dir: str|Path|os.PathLike, template_file: str, template_data: dict) -> str:
    """
    """
    template_dir = os.path.realpath(template_dir)
    loader = FileSystemLoader(template_dir, encoding="utf-8")
    env = Environment(loader=loader)
    template = env.get_template(template_file)
    return template.render(template_data)


def generate_html(template_dir: str|Path|os.PathLike, template_file: str, template_data: dict) -> str:
    """Old wrapper."""
    return generate_from_file(template_dir, template_file, template_data)

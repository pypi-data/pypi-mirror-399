"""
Dynamically find modules from packages. Find files (resources) "compiled" into packages.
Sometimes we have some descriptor or binary file included into package and package consumer wants use exactly this file.

find_module_name is yet too "non-general", it relies on some (hidden) convention about modules_def dict. must think.
"""

from types import ModuleType
from typing import Callable
from importlib import import_module
import os
from pathlib import Path

from loguru import logger

def prepare_function(module_short_alias: str, function_name: str, modules_cache: dict|None = None, modules_defs: dict|None = None) -> Callable|None:
    """Return object of type function/Callable."""
    the_module: ModuleType|None = prepare_module(module_short_alias, modules_cache, modules_defs) # see mäping annab teada õige mooduli
    if the_module is None:
        logger.error(f"No module for {module_short_alias}")
        return None
    if not hasattr(the_module, function_name):
        logger.error(f"No function ({function_name}) in module ({the_module.__name__}) for {module_short_alias}")
        logger.error(the_module)
        return None
    the_function = getattr(the_module, function_name)
    return the_function # returns the function from module

def prepare_module(module_short_alias: str, modules_cache: dict|None, modules_defs: dict|None = None) -> ModuleType|None:
    """Return module where some functionality resides. Import module if not already loaded (own cache).

    Parameter module_short_alias is reference string kept in database or file (sort of safeguard)
    Read https://docs.python.org/3/library/importlib.html
    """
    # if cache dict is given try cache
    if modules_cache and module_short_alias in modules_cache:
        logger.debug(f"Module for command {module_short_alias} is returned from cache")
        return modules_cache[module_short_alias]
    module_long_name = find_module_name(module_short_alias, modules_defs)
    the_module: ModuleType|None = None
    if module_long_name is None or module_long_name.startswith('.') or module_long_name.endswith('.'):
        logger.error(f"Module for {module_short_alias} is not defined or is not allowed, {module_long_name}")
        return None
    try: # lets try to import module
        the_module = import_module(module_long_name)
        #logger.debug(f"Module {module_long_name} is loaded")
        if modules_cache:
            modules_cache[module_short_alias] = the_module # changes input dict (python, here we actually need this feature)
            #logger.debug(f"Module {module_long_name} is cached as {module_short_alias}")
    except Exception as e1:
        logger.error(f"Cannot import module {module_long_name}, {e1}")
        return None
    return the_module

def find_module_name(action_alias: str, modules_defs: dict|None = None) -> str|None:
    """From action alias and some special dict, calculates somehow module full name."""
    trusted_agent: dict|None = modules_defs.get(action_alias) if modules_defs is not None else None
    if not trusted_agent:
        return None
    return f"{trusted_agent['package']}.{trusted_agent['module']}"

def read_package_file(module_name: str, file_name: str) -> str|None:
    """Backward compatibility wrapper."""
    return read_content_of_package_file(module_name=module_name, file_name=file_name)

def read_content_of_package_file(module_name: str, file_name: str) -> str:
    """
    Return content of one resource file included into named package. 
    Eg. core versioning scripts, module mappings, ...
    Subdir must have (empty) __init__.py file inside and so it can pointed as module (dot-notation).  
    And dirs/files must be built in during package build (edit pyproject.toml if problems arise).  
    File_name must be flat, no backslashes (must directly sit inside submodule) 
        - up to 3.12
        - 3.13+ allows multi-pathnames
    Reads file with 'r' key (not 'rb'). Returns UTF-8 string
    """
    from importlib.resources import files # needs 3.7+, actually 3.9+
    try:
        # old way, deprecated in 3.11:
        # with importlib.resources.open_text(module_name, file_name, encoding="UTF-8") as file:
        # new way, needs py 3.9, encoding="utf-8" is default (from 3.13 must used as kw-arg)
        with files(module_name).joinpath(file_name).open('r', encoding="utf-8") as handler: # 3.9+ 
            content = handler.read()
        return content # utf-8 string
    except Exception as e1:
        logger.error(f"Resource file {file_name} problem: {e1}")
        return ""

def copy_from_package_to_file(source_module_name: str, source_file_name: str, target_file_name: str|os.PathLike|Path) -> None:
    """
    Create new file from file packed inside mentioned package/module.

    Source file name must be flat (no backslashes).
    Target file name must be full (overwise taken as relative and result is unpredictable).

    Uses binary mode. Before deletes target file if exists.
    """
    from importlib.resources import files # needs 3.7+, actually 3.9+
    try:
        os.makedirs(os.path.dirname(target_file_name), exist_ok=True)
        if os.path.exists(target_file_name):
            os.remove(target_file_name)
        to_handler = open(target_file_name, "xb") # x = new file! (w - may need file to exist)
        with files(source_module_name).joinpath(source_file_name).open('rb') as from_handler:
            to_handler.write(from_handler.read())
    except Exception as e1:
        logger.error("From-package-to-filesystem-copy-error")
        logger.error(str(e1))

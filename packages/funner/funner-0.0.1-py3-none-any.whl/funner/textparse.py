"""
Module textpar help parsing text as data. Currently YAML. Possible idea to add here JSON and TOML... or even XML...
"""

from typing import Any

import yaml


def dict_from_yaml(yaml_string: str) -> dict | None:
    """Return dict from YAML string.
    
    Try make error situations as dict. None and empty string (and spaces only string) will result {}.
    If string contains one-element list and first elemen is dict, then return this dict.
    Parsing error results as None.
    """
    if yaml_string is None or yaml_string.strip() == "":
        return {}
    try:
        structure = yaml.load(yaml_string, Loader=yaml.Loader)
    except Exception as e1:
        return None # technical error (never happens?)
    
    if structure is None:
        return {}
    if isinstance(structure, dict):
        return structure # this is dict
    if isinstance(structure, list):
        if len(structure) == 1 and isinstance(structure[0], dict): 
            return structure[0] # one-element list where element is dict
        else:
            return None # bad list for dict (actually it can be transformed into dict[int, Any])
    # what else it can be? int/float/str/bool
    return None # on wrong content

def list_from_yaml(yaml_string: str) -> list | None:
    """Return list from YAML string.
    
    Try make error situations as list. None and empty string (and spaces only string) will result [].
    If string contains dict, make whole dict as one and only element of list.
    Parsing error results as None.
    """
    if yaml_string is None or yaml_string == "":
        return []
    try:
        structure = yaml.load(yaml_string, Loader=yaml.Loader)
    except Exception as e1:
        return None # technical error (never happens?)
    
    if structure is None:
        return []
    if isinstance(structure, list):
        return structure # this is list
    if isinstance(structure, dict):
        return [structure] # this is one-element list (contains dict)
    if isinstance(structure, str):
        return [structure] # list containing one string
    # int/float/bool?
    return None # on wrong content



#### old stuff (lets call then deprecated)

def yaml_string_to_dict(yaml_content_string: str, make_to_dict: str='root') -> dict | None:
    return interpret_string_as_yaml(yaml_content_string, make_to_dict=make_to_dict) # type: ignore

def yaml_string_to_structure(yaml_content_string: str) -> Any:
    return interpret_string_as_yaml(yaml_content_string, make_to_dict=None)

def interpret_string_as_yaml(yaml_content_string: str | None, make_to_dict: str|None='root') -> dict | list | None:
    """
    Transform yaml string content as dict (or list??)
        (can we avoid yaml files with arrays at the highest level?)
    Param make_to_dict if not empty then non-dict is transformed to dict using that key
    """
    if yaml_content_string is None:
        return None
    if yaml_content_string == "":
        return {}
    structure = yaml.load(yaml_content_string, Loader = yaml.Loader) or None
    if structure is None or isinstance(structure, dict):
        return structure
    # if not dict:
    if make_to_dict:
        new_dict: dict = {make_to_dict : structure}
        return new_dict
    return structure # as is (whatever yaml.load gives to us)

"""
Class Storable is base class for data.
Purpose is to make data declaration as simple as possible.
"""

__all__ = ["Storable"]

import json
from uuid import uuid4

from loguru import logger

class Storable():
    """Data class. More tolerable/simpler then pydantic, problably less powerful. 
    
    Not meant for ORM. 
    Is meant for storing-loading data object using the key.
    Data element can be list or dict (giving us hierarchy)
    Data element (property) can be reference to other dataobject but this meaning is irrelevant here.
    In subclass declare properties as class level attributes, annotate.
    """

    key: str # important! key! all subclasses will have it w/o explicit declaration

    def __init__(self, json_str: str | None = None, **kwargs) -> None:
        """Create object from JSON string, using defaults from kwargs.

        Ignore values in JSON what are not in class definition.
        "key" can be amoungst kwargs or JSON. If not then will be created randomly.
        """
        magic: dict = _grab(self.__class__)
        json_data: dict = {}
        if isinstance(json_str, str) and json_str: # try to load non-empty string as JSON
            json_data = self.deserialize(json_str) # emits logger error, continues on error
        init_data: dict = kwargs | json_data # merges dicts, right side overrides
        for key, value in magic.items():
            if key in init_data.keys():
                setattr(self, key, init_data[key])
            else:
                setattr(self, key, value)
        self._magic = [key for key in magic.keys()] # magic private variable
        if not self.key:
            self.key = str(uuid4())

    def get_key(self) -> str:
        """Return key of object. If not exists, generate one using uuid techinque."""
        if not self.key:
            self.key = str(uuid4())
        return self.key
    
    def set_key(self, key: str):
        """Set key manually. For caces then key must be same as in somewhere else."""
        self.key = key
    
    def get_type(self) -> str:
        """Return objects own classname"""
        return self.__class__.__name__

    def serialize(self) -> str:
        """Return unicode JSON string of current object
        
        Uses internal magic dict collected during init.
        """
        new_dict: dict = {}
        for attr in self._magic:
            value = getattr(self, attr)
            new_dict[attr] = value
        return json.dumps(new_dict, indent=None, ensure_ascii=False)
    
    def deserialize(self, text: str) -> dict:
        """Returns dict got from json.loadstring. Empty dict on error. Emits logger error.

        No use of self, but since its oposite to serialize, let it be class method.
        Future plans: extend function to parse as yaml, toml, xml etc until some result.
        Maybe add argument for hint (ordered list of possible formats to try).
        """
        data: dict = {}
        try:
            data = json.loads(text)
        except Exception as e1:
            logger.error(str(e1))
        return data

    def __str__(self) -> str:
        """For nice printout. Multiline. 3-spaced."""
        cls = self.__class__
        vars = self.__dict__
        delim = "\n"+3*" "
        attribs = delim.join([f"{key}={value}" for key, value in vars.items() if key != '_magic' ])
        return f"{cls.__module__}.{cls.__qualname__}: {delim}{attribs}"
        

def _grab(cls, result: dict | None = None) -> dict:
    """Internal helper for recursive work.
    
    Collects public properties of given class and steps through class's inheritance tree (upwards).
    Finds as well non-valued but annotated properties. 
    Trick: if value is not defined then vars(cls) won't return it. So we use annotations to find them.
    """
    if result is None:
        result = {}
    class_vars: dict = dict(vars(cls))
    annotations: dict = class_vars["__annotations__"] if '__annotations__' in class_vars else {}
    for key, value in class_vars.items():
        if key.startswith("_"): # lets not include "privates" and "magics"
            continue
        if key.startswith("__"): # now already covered by previous
            continue
        if callable(getattr(cls, key)): # lets not include methods
            continue
        if key not in result or result[key] is None:
            result[key] = value
    for key in annotations.keys():
        if key not in result:
            result[key] = None
    for base in cls.__bases__:
        _grab(base, result) # TODO: detect why I didnt make this line as "result = grab(base, result)" !!!! python way "by ref" ??
    return result

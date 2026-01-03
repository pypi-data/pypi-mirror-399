"""Collection of generally useful functions. Sometimes even classes.

datefun is module containing functions which treat string as date. ISO-dates like YYYY-MM-DD as they are usually communicated with datebase.
(just now tring only import them from already ready package "datefun", may-be its overkill and we shall keep them nicely separated)
packfun is for finding resources from packages
filefun is file system operations wrappers (incl contextmanager for opening file and creating full path dirs on its way)
textgen is module wrapped over Jinja to produce text using template and data
textparse is module containing functions (parsers) to interpret text as data, currently yaml-text
storable is module containing base class Storable with methods to (un)serialize objects (without methods, pure data).

storing  will be module to save storables (or at least base class for them), implementation subclasses probably have lot of dependecies, so let's keep them separate?

"""
# __all__ = ["datefun"] # why "is not present in module"? here we have package level, things here are modules by themselves => so how to define allowed/known modules? no need?

from datefun import datefun

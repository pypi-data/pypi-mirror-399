"""Collection of generally useful functions. Sometimes even classes.

packfun is for finding resources from packages
filefun is file system operations wrappers (incl contextmanager for opening file and creating full path dirs on its way)
textgen is module wrapped over Jinja to produce text using template and data
textparse is module containing functions (parsers) to interpret text as data, currently yaml-text
storable is module containing base class Storable with methods to (un)serialize objects (without methods, pure data).

storing  will be module to save storables (or at least base class for them), implementation subclasses probably have lot of dependecies, so let's keep them separate?

"""

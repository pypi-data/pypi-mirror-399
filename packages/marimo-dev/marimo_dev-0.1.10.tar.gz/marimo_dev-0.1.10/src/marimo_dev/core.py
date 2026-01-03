import ast, re, tomllib, json
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field

class Kind(Enum):
    "Types of nodes in parsed code"
    IMP='import'    # Import statement
    CONST='const'   # Constant definition
    EXP='export'

@dataclass
class Param:
    name: str                # parameter name
    anno: str|None = None    # type annotation
    default: str|None = None # default value
    doc: str = ''

@dataclass 
class Node:
    "A parsed code node representing an import, constant, or exported function/class."
    kind: Kind       # type of node (import/const/export)
    name: str        # identifier name
    src: str         # source code
    doc: str = ''    # docstring text
    params: list[Param] = field(default_factory=list)    # function/class parameters
    methods: list = field(default_factory=list)          # class methods (for class nodes)
    ret: tuple[str,str]|None = None

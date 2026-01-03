"""
CHILL Compiler - ITU-T Z.200 CHILL to C Transpiler

Because GCC removed CHILL support in 2001, and someone had to do something.
"""

__version__ = "1.0.0"

from .parser import parse, ParseError
from .semantic import analyze, SemanticError
from .codegen import generate

__all__ = ['parse', 'analyze', 'generate', 'ParseError', 'SemanticError']

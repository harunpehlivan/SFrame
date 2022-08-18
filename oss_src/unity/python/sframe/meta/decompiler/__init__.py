'''
Decompiler module.

This module can decompile arbitrary code objects into a python ast. 
'''

from .instructions import make_module, make_function

import _ast
import struct
import time
import sys
import marshal



def decompile_func(func):
    '''
    Decompile a function into ast.FunctionDef node.
    
    :param func: python function (can not be a built-in)
    
    :return: ast.FunctionDef instance.
    '''
    code = func.func_code if hasattr(func, 'func_code') else func.__code__
    return make_function(code, defaults=[], lineno=code.co_firstlineno)

def compile_func(ast_node, filename, globals, **defaults):
    '''
    Compile a function from an ast.FunctionDef instance.
    
    :param ast_node: ast.FunctionDef instance
    :param filename: path where function source can be found. 
    :param globals: will be used as func_globals
    
    :return: A python function object
    '''

    funcion_name = ast_node.name
    module = _ast.Module(body=[ast_node])

    ctx = {f'{key}_default': arg for key, arg in defaults.items()}

    code = compile(module, filename, 'exec')

    eval(code, globals, ctx)

    return ctx[funcion_name]

#from imp import get_magic
#
#def extract(binary):
#    
#    if len(binary) <= 8:
#        raise Exception("Binary pyc must be greater than 8 bytes (got %i)" % len(binary))
#    
#    magic = binary[:4]
#    MAGIC = get_magic()
#    
#    if magic != MAGIC:
#        raise Exception("Python version mismatch (%r != %r) Is this a pyc file?" % (magic, MAGIC))
#    
#    modtime = time.asctime(time.localtime(struct.unpack('i', binary[4:8])[0]))
#
#    code = marshal.loads(binary[8:])
#    
#    return modtime, code

def decompile_pyc(bin_pyc, output=sys.stdout):
    '''
    decompile apython pyc or pyo binary file.
    
    :param bin_pyc: input file objects
    :param output: output file objects
    '''
    
    from graphlab.meta.asttools import python_source
    
    bin = bin_pyc.read()
    
    code = marshal.loads(bin[8:])
    
    mod_ast = make_module(code)
    
    python_source(mod_ast, file=output)

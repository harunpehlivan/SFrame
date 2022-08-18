#!/usr/bin/python
import re
import sys
import os
print "patching ", sys.argv[1]
includestring = re.compile("#include\s?<(.*hp*)>")

def remap_line(i):
    if t := includestring.match(i):
        g = t.group(1)
        g = t.group(1)
        if os.path.isfile(f'graphlab/{g}'):
            return f"#include <graphlab/{g}" + ">\n"
    return i

lines = file(sys.argv[1], 'r').readlines()
lines = [remap_line(l) for l in lines]
nf = file(sys.argv[1], 'w')
nf.writelines(lines)
nf.close()
print

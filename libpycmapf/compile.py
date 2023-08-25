from cffi import FFI
import re
import os.path
ffibuilder = FFI()

path = os.path.dirname(os.path.abspath(__file__))

cnt = []
with open(os.path.join(path, '..', 'libcmapf', 'include', 'cmapf.h')) as f:
    for line in f:
        if not re.match(r' *(#|//|extern *"C" *{|}$|$)', line):
            cnt.append(re.sub(r'[A-Z_]+_VISIBILITY_DEFAULT ', '', line).strip())
code = '\n'.join(cnt)

# TODO: have to add relevant clingo forwards
ffibuilder.cdef(f'''\
typedef struct clingo_control clingo_control_t;
typedef struct clingo_symbolic_atoms clingo_symbolic_atoms_t;
{code}
''')

ffibuilder.set_source("_cmapf", """\
#include "cmapf.h"
""")

ffibuilder.emit_c_code('_cmapf.c')

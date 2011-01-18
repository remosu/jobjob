"""..."""

import os
import numpy as np
from functools import wraps
import glob


def copy_input(src, dst, **input_vars):
    """..."""
    lines = []
    for line in open(src):
        values = line.split()
        if values and values[0] in input_vars:
            var, _, comment = line.rpartition(values[1])
            line = var + str(input_vars[values[0]]) + comment
            del input_vars[values[0]]
        lines.append(line)
    lines.append('\n#----\n')
    for var, value in input_vars.items():
        lines.append('%s %s\n' % (var, value))
    open(dst, 'w').writelines(lines)
    
def change_input(src, **input_vars):
    copy_input(src, src, **input_vars)
            
            
def get_value(str_value):
    try:
        return int(str_value)
    except:
        try:
            return float(str_value)
        except:
            return str_value


def read_vars(input_filename):
    """..."""
    for line in open(input_filename):
        values = line.split()
        if values and not values[0].startswith('#'):
            yield (values[0], get_value(values[1]))
            

def cache_result(filename=None): 
    """cache data decorator""" 
    def foo(f):
        #@wraps(f)
        def cache_wrapper(*args, **kwds):
            cache_filename = filename
            if filename is None:
                cache_filename = f.func_name
                if args:
                    cache_filename += ''.join([str(v) for v in args[1:]])
                cache_filename += ''.join([k+str(v) for k,v in kwds.items()])
                cache_filename += '.dat'
            job = args[0] if args else kwds['sim']
            cache_filename_abs = os.path.join(job.path, cache_filename)
            if os.path.exists(cache_filename_abs):
                #print cache_filename
                return np.loadtxt(cache_filename_abs)
            result = f(*args, **kwds)
            print 'caching data to:', cache_filename_abs
            with open(cache_filename_abs, 'w') as cache_file:
                np.savetxt(cache_file, result, fmt='%f', delimiter=' ')
            return result
        return cache_wrapper
    return foo

class Cds(object):
    def __init__(self, filename):
        def _point(line):
            return np.array(map(float, line.split()))

        with open(filename) as cds:
            def _int_at_end():
                return int(cds.readline().split()[-1])
            def _point():
                return np.array(map(float, cds.readline().split()))

            self.nio = _int_at_end()
            self.io_index = _int_at_end()
            self.N_colloid = _int_at_end()
            self.nlocal = _int_at_end()
            self.a0, self.ah, self.index = _point()
            self.index = int(self.index)
            self.pos = _point()
            self.vel = _point()
            self.omega = _point()
            self.magnetic_dipole = _point()
            self.deltaphi = float(cds.readline())



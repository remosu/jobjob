"""..."""

import os
import numpy as np
from functools import wraps
import glob
import itertools


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

def mk_jobdir(input_vars):
    reprv = dict(D_minus='D', ch_objects='Q')
    launch_tmpl = '''
    #!/bin/bash
    #PBS -l nodes=1
    #PBS -N %(STRING)s
    #PBS -q exe 

    pbstmp=$scratch/$PBS_JOBID
    mkdir out
    mkdir $pbstmp
    cp *.bin par_* $pbstmp/
    touch $PBS_JOBID
    cd $pbstmp

    elb %(INFILE)s > log_%(INFILE)s

    scp  * nodo0:$PBS_O_WORKDIR/out/
    '''
    for values in itertools.product(*input_vars.values()):
        a = dict(zip(input_vars.keys(), values))
        jobname = ''.join('%s%s'%(reprv.get(k,k), v) 
                          for k, v in a.items() if k != 'restart')
        a['D_plus'] = a['D_minus']
        a['output'] = jobname
        print jobname
        if not os.path.exists(jobname):
            os.mkdir(jobname)
        par_filename = 'par_'+jobname
        launch_filename = 'launch_'+jobname+'.sh'
        dst = os.path.join(jobname, par_filename)
        copy_input('par_tmpl', dst, **a)
        launch_text = launch_tmpl % {'INFILE':par_filename, 
                                     'STRING':'elb_'+jobname}
        open(os.path.join(jobname, launch_filename), 'w').write(launch_text)
        os.system('chmod +x '+os.path.join(jobname, launch_filename))
      
            
            
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
    #print input_filename
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
                #print cache_filename_abs
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


def job_name_from_log(log_filename):
    return os.path.split(log_filename)[-1][8:]


def get_jobs_from_tmpl(tmpl):
    return [jobjob.jobs.Job(*os.path.split(input))
            for input in glob.glob(tmpl)]

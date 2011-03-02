#!/usr/bin/env python

import sys
import os
from glob import glob
import itertools
from collections import namedtuple

import numpy as np
#import pylab

vs = dict(('v'+''.join(str(u_x).split('.')), u_x) for u_x in (0.1, 0.5, 0.01, 0.05, 0.001, 0.005))


starts = [' '.join(values) for values in itertools.product(('1', '100'), ('1', '100'), ('0', '99'))]

def get_input(input_file):
    def f(name):
        r = os.popen('grep %s %s '%(name, input_file))
        data = r.read()
        print data
        return data.split()[-1]
    return f

if len(sys.argv) < 2:
    print "usage: %s -[xyz] logfile" % (sys.argv[0])
    sys.exit(1)


columns = {'x':'9', 'y':'10', 'z':'11'}
column = 9
if sys.argv[1].startswith('-'):
    column = columns.get(sys.argv[1][1:], 9)
    del sys.argv[1]

values = []

for directory in sys.argv[1:]:
    value = dict()
    out_dir = os.path.join(directory, '')
    input_files = glob(os.path.join(out_dir, 'par_*'))
    input_files.sort()
    input_file = input_files[0] if input_files else None
    log_files = glob(os.path.join(out_dir, 'log_par_*'))
    log_file = log_files[0] if log_files else None
    print log_file
    #velocidades en las esquinas
    #data_filename_mask = os.path.join(out_dir, 'oelb_lattice_*.elb')
    #data_filenames = glob(data_filename_mask)
    #data_filenames.sort()
    #data_filename = data_filenames[-1]
    #print data_filename
    #data = open(data_filename)
    #vs = np.array([float(line.split()[3]) for line in data if any(line.startswith(s) for s in starts)])
    #value['vs'] = vs
	
	

    #valores en el input
    #get_value = get_input(input_file)
    #u_x = get_value('u_x')
    #D_minus = get_value('D_minus')
    #D_plus = get_value('D_plus')
    #r_eff = get_value('r_eff')
    #Q = get_value('ch_objects')
    #value['u_x'] = float(u_x)
    #value['D_minus'] = float(D_minus)
    #value['D_plus'] = float(D_plus)
    #value['r_eff'] = float(r_eff)
	
    #print u_x, D_minus, D_plus
    #img_file = os.path.join(out_dir, 'u_x%sD_minus%sQ%s.png' % (u_x, D_minus, Q))
    
	#Pe
    #r_eff = float(r_eff)
    #D = float(D_minus)
    #value['Pe'] = vs.mean() * r_eff / D

    #fuerzas electrostaticas
    ef10_filename = os.path.join(out_dir, 'ElForce_c10.dat')
    ef11_filename = os.path.join(out_dir, 'ElForce_c11.dat')
    if not os.path.exists(ef10_filename) or not os.path.exists(ef11_filename):
        for comm in  ["grep -a 'oid %(part)s ele' %(log_file)s | awk '{print $%(column)s}'  > %(out)s/ElForce_c%(part)s.dat" 
                % {'part':particle, 'log_file':log_file, 'out':out_dir, 'column':column} for particle in ('10', '11')]:
            print '>>>: ', comm
            os.system(comm)

    #fuerzas hidrodinamicas
    hf10_filename = os.path.join(out_dir, 'HydroForce_c10.dat')
    hf11_filename = os.path.join(out_dir, 'HydroForce_c11.dat')
    print hf10_filename, hf11_filename
    if not os.path.exists(hf10_filename) or not os.path.exists(hf11_filename):
        for comm in ["grep -a 'to colloid %(part)s' %(log_file)s | awk '{print $%(column)s}'  > %(out)s/HydroForce_c%(part)s.dat"
                % {'part':particle, 'log_file':log_file, 'out':out_dir, 'column':column} for particle in ('10', '11')]:
            print '>>>: ', comm
            os.system(comm)


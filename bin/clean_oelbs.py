#!/usr/bin/env python


import sys
import os
import glob
import shutil


if __name__ == '__main__':
    for directory in sys.argv[1:]:
        new_dir = os.path.join(directory, 'by')
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        print 'in:', directory
        for oelb_file in glob.glob(os.path.join(directory, 
                                         'oelb_lattice_*.elb')):
            basename = os.path.basename(oelb_file)
            step = int(os.path.splitext(basename)[0].split('_')[-1])
            if step !=0 and step < 20000:
                new_oelb_file = os.path.join(new_dir, basename)
                shutil.move(oelb_file, new_oelb_file)
                print '  move %s to %s' % (oelb_file, new_oelb_file)
            else:
                print '  nothing', oelb_file
                

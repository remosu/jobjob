#!/usr/bin/env python


import sys
import os
import jobjob.utils
import glob



def main():
    for log_filename in sys.argv[1:]:
        #grp_dir_name = 'grps'
        #if not os.path.exists(grp_dir_name):
        #    os.mkdir(grp_dir_name)
        job_name = jobjob.utils.job_name_from_log(log_filename)
        #new_dir = os.path.join(grp_dir_name, job_name)
        new_dir = job_name
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        out_dir = os.path.join(new_dir, 'out')
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        os.system('mv *_{0}* {1}'.format(job_name, out_dir))
        #for fn in glob.glob('*_%s*'%job_name):
        #    os.system('ln -s {0} {1}/{2}'.format(os.path.abspath(fn), 
        #                                         out_dir, fn))


if __name__ == '__main__':
    main()

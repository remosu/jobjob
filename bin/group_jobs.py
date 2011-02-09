#!/usr/bin/env python


import sys
import os
import jobjob.utils



def main():
    for log_filename in sys.argv[1:]:
        job_name = jobjob.utils.job_name_from_log(log_filename)
        if not os.path.exists(job_name):
            os.mkdir(job_name)
        out_dir = os.path.join(job_name, 'out')
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        os.system('mv *_{0}* {1}'.format(job_name, out_dir))


if __name__ == '__main__':
    main()

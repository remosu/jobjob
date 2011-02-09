#!/usr/bin/env python

import os
import glob
import numpy as np
import pylab
import jobjob.jobs
import jobjob.utils
from matplotlib.colors import LogNorm


#jobsu0 = [jobjob.jobs.Job(*os.path.split(path)) 
#          for path in glob.glob('/mnt/elb_data/D0.0*/out/out/par_*')]
#dd = dict((job.input, job) for job in jobsu0)

#jobs_orig = [jobjob.jobs.Job(*os.path.split(input)) 
#             for input in glob.glob('/media/DATA/ELB/D0.0*/out/par_*')]

def get_jobs_from_tmpl(tmpl):
    return [jobjob.jobs.Job(*os.path.split(input))
            for input in glob.glob(tmpl)]

jobs_tmpls = (
    '/home/rene/Work/ELB_data/ELB_data_in_HDD/r20/Q10*/out/par_*',
    '/home/rene/Work/ELB_data/ELB_data_in_HDD/r20/Q50*/out/par_*',
    '/home/rene/Work/ELB_data/ELB_data_in_HDD/r20/Q200*/out/par_*',
    #'/home/rene/Work/ELB_data/vertical/u_y*/par_*',
    )
jobs_orig = []
for tmpl in jobs_tmpls:
    jobs_orig += get_jobs_from_tmpl(tmpl)

tmplQ0 = '/home/rene/Work/ELB_data/ELB_data_in_HDD/r20/Q0*/out/par_*'
jobs_ch0 = [jobjob.jobs.Job(*os.path.split(input)) 
            for input in glob.glob(tmplQ0)]
dd_ch0 = dict((job.make_key('u_x', 'D_minus', 'D_plus'), job) for job in jobs_ch0)             

tmplu0 = '/home/rene/Work/ELB_data/ELB_data_in_HDD/r20u0/Q*/out/par_*'
jobs_u0 = get_jobs_from_tmpl(tmplu0)
dd = dict((job.make_key('ch_objects', 'D_minus'), job) 
          for job in jobs_u0)
def update_forces():
    """docstring for update_forces"""
    for job in jobs_orig:
        dd_key = job.make_key('ch_objects', 'D_minus')
        dd_job = dd.get(dd_key)
        job.job_u0 = dd_job
        if dd_job is not None:
            hf_eq10 = np.mean(dd[dd_key].HydroForce_c10[-1000:])
            hf_eq11 = np.mean(dd[dd_key].HydroForce_c11[-1000:])

            hf10 = job.HydroForce_c10 - hf_eq10
            hf11 = job.HydroForce_c11 - hf_eq11
            
            ef10 = job.ElForce_c10 + hf_eq10
            ef11 = job.ElForce_c11 + hf_eq11
            job.ef10, job.ef11, job.hf10, job.hf11 = ef10, ef11, hf10, hf11
            job.hf_eq10, job.hf_eq11 = hf_eq10, hf_eq11
        
        job.job_ch0 = dd_ch0.get(job.make_key('u_x', 'D_minus', 'D_plus'), None)


    jobs_orig = [job for job in jobs_orig if all((job.job_ch0, job.job_u0))]


def mk_jobs_u0():
    print ""
    print "new jobs: u_x = 0.0 ..."
    ujobs = dict()
    jobs = [job for job in jobs_orig if job.ch_objects != 0]
    for job in jobs:
        key = job.make_key('ch_objects', 'D_minus', 'r_pair')
        ujobs[key] = job
    for job in ujobs.values():
        #binfile = os.path.basename(job.get_binfile())
        binfile = 'oelb_lattice_Eq_Ch_field_%s.bin' % job.output
        jobjob.utils.mk_jobdir({'u_y':[0.0],
                                'D_minus':[job.D_minus], 
                                'ch_objects':[job.ch_objects], 
                                'r_pair':[job.r_pair],
                                'restart':[binfile]})
        #src = os.path.join(job.path, job.input)
        #dstdir = os.path.join('/home/rene/Work/ELB_data/r20u0',
        #                      'Q%sD%s' % (job.ch_objects, job.D_minus))
        #os.system('cp "%s" "%s"' % (job.get_binfile(), dstdir))
        #print
        #print 'old sim <<', job.path    
        #new_name = 'Q%sD%sr_pair%s' %(job.ch_objects, 
        #                              job.D_minus, job.r_pair)
        #print 'new sim >>', os.path.join(os.path.dirname(job.path), new_name)
    #if not os.path.exists()    
    #print len(jobs), len(jobs_orig)        
        


def plot_forces():
    for job in jobs_orig:
        pylab.clf()    

        pylab.subplot(211)
        pylab.title(r'$u_x=%.4f,\  D_{-}=%.4f,\  D_{+}=%.4f,\ ch=%i$' % 
                    (job.u_x, job.D_minus, job.D_plus, job.ch_objects))

        pylab.plot(job.ef10, label='particle 10')
        pylab.plot(job.ef11, label='particle 11')
        pylab.legend(loc='best')
        pylab.ylabel('elec force')

        pylab.subplot(212)
        pylab.plot(job.hf10, label='particle 10')
        pylab.plot(job.hf11, label='particle 11')
        #~ pylab.legend(loc='best')
        pylab.ylabel('hydro force')
        
        #imgfilename = 'u_x%.4fD%.4fch%03i.png' % (job.u_x, job.D_minus, job.ch_objects)
        imgfilename = 'plot_forces_%s.png' % job.job_id
        pylab.savefig(imgfilename)
        
def plot_pp(var):
    jobs_orig.sort(key=lambda job: getattr(job, var))
    pylab.subplot(211)
    for ch in (10, 50, 200):
        xs = [getattr(job, var) for job in jobs_orig if job.ch_objects == ch]
        if xs:
            pylab.plot(xs, 
                       [(job.ef11[-1] + job.ef10[-1]) / job.ef11[0] 
                        for job in jobs_orig if job.ch_objects==ch], 
                       'o-', label=r'$ch=%.0f$'%ch)
            pylab.xscale('log')
    pylab.xlabel(r'$%s$'%(var,))
    pylab.ylabel(r'$(ef_{11}^n+ef_{10}^n)/ef_{11}^0$')
    pylab.legend(loc='best')
    
    pylab.subplot(212)
    for ch in (10, 50, 200):
        xs = [getattr(job, var) for job in jobs_orig if job.ch_objects == ch]
        if xs:
            pylab.plot(xs, 
                       [job.hf_eq11 / job.ef11[-1] for job in jobs_orig if job.ch_objects==ch], 
                       'o-', label=r'$ch=%.0f$'%ch)
            pylab.xscale('log')
    pylab.xlabel(r'$%s$'%(var,))
    pylab.ylabel(r'$hf{11}^n(Q=0) / ef_{11}^n$')
    pylab.legend(loc='best')
    pylab.savefig(var+'.png')
    

def plot_hfch0ef():
    jobs_orig.sort(key=lambda job: job.Pe)
    for ch in (10, 50, 200):
        xs = [job.Pe for job in jobs_orig if job.job_ch0 and job.ch_objects == ch]
        factor = 0.005 if ch == 10 else 0.1 if ch == 50 else 1.0
        if xs:
            pylab.plot(xs, 
                       [job.job_ch0.HydroForce_c11[-1] / job.ef11[-1] * factor
                        for job in jobs_orig if job.job_ch0 and job.ch_objects==ch], 
                       'o-', label=r'$ch=%.0f\ [*%.3f]$'%(ch, factor))
            pylab.xscale('log')
    pylab.xlabel(r'$Pe$')
    pylab.ylabel(r'$hf_{11}^n(Q=0) / ef_{11}^n$')
    pylab.legend(loc='best')
    pylab.savefig('hfch0overef.png')
    
def plot_ef_hfch0():
    jobs_orig.sort(key=lambda job: job.Pe)
    for ch in (10, 50, 200):
        xs = [job.Pe for job in jobs_orig if job.job_ch0 and job.ch_objects == ch]
        if xs:
            pylab.plot(xs, 
                       [(job.ef11[-1] - job.ef10[-1]) / job.job_ch0.HydroForce_c11[-1]
                        for job in jobs_orig if job.job_ch0 and job.ch_objects==ch], 
                       'o-', label=r'$ch=%.0f$'%ch)
            pylab.xscale('log')
    pylab.xlabel(r'$Pe$')
    pylab.ylabel(r'$ (ef_{11}^n - ef_{10}^n) / hf_{11}^n(Q=0) $')
    pylab.legend(loc='best')
    pylab.savefig('ef11minusef10overhfch0.png')
    

def plot_dip(dipfun):
    jobs_orig.sort(key=lambda job: job.Pe)
    for ch in (10, 50, 200):
        xs = [job.Pe for job in jobs_orig if job.job_ch0 and job.ch_objects == ch]
        if xs:
            pylab.plot(xs, 
                       [(getattr(job, dipfun)**2).sum()**0.5
                        for job in jobs_orig if job.job_ch0 and job.ch_objects==ch], 
                       'o-', label=r'$ch=%.0f$'%ch)
            pylab.xscale('log')
    pylab.xlabel(r'$Pe$')
    pylab.ylabel(r'$ dip $')
    pylab.legend(loc='best')
    pylab.savefig(dipfun+'.png')
    
def plot_ch():
    for job in jobs_orig:
        print "plane of", job.path
        pylab.clf()
        x_center = int((job.position(0)[0] + job.position(1)[0])/2)
        x_final = 50 + x_center
        #plane = np.concatenate((job.plane(y=50)[:, x_final:], 
        #                        job.plane(y=50)[:, :x_final]), axis=1)
        plane = job.plane(y=50)
        myplane = plane[plane < 0.0]
        p0 = myplane.min()
        p12 = np.median(myplane)
        p14 = np.median(myplane[myplane<p12])
        p34 = np.median(myplane[myplane>p12])
        p1 = myplane.max()
        contour_values = (p0, p14, p12, p34, p1)
        pylab.title(r'$u_x=%.4f,\  D_{-}=%.4f,\  D_{+}=%.4f,\ ch=%i$ ' %
                    (job.u_x, job.D_minus, job.D_plus, job.ch_objects))
        car = pylab.imshow(plane, vmin=-0.001, vmax=0.0, 
                           interpolation='nearest')
        pylab.contour(plane, contour_values, linestyles='dashed', 
                                             colors='white')
        pylab.grid(True)
        pylab.colorbar(car)
        #imgfilename = 'plane_r20-y50-u_x%.4fD%.4fch%03i.png' % \
        #              (job.u_x, job.D_minus, job.ch_objects)
        imgfilename = 'plane_%s.png' % job.job_id
        pylab.savefig(imgfilename)
        
def plot_ch_chq0():
    for job in jobs_orig:
        if job.job_ch0:
            pylab.clf()
            pylab.title(r'$u_x=%.4f,\  D_{-}=%.4f,\  D_{+}=%.4f,\ ch=%i$' % 
                        (job.u_x, job.D_minus, job.D_plus, job.ch_objects))

            pylab.plot((job.hf10/job.job_ch0.HydroForce_c10)[100:], label='hf/hf(Q=0) -- 10')
            #pylab.plot(job.hf10, label='hf -- 10')
            #pylab.plot(job.job_ch0.HydroForce_c10, label='hf(Q=0) -- 10')
            pylab.plot((job.hf11/job.job_ch0.HydroForce_c11)[100:], label='hf/hf(Q=0) -- 11')
            #pylab.plot(job.hf11, label='hf -- 11')
            #pylab.plot(job.job_ch0.HydroForce_c11, label='hf(Q=0) -- 11')
            #pylab.ylim(-20, 20)
            pylab.legend(loc='best')
            pylab.ylabel('hydro force / hydro force(Q=0)')
            #imgfilename = 'hf_hfq0-u_x%.4fD%.4fch%03i.png' % (job.u_x, job.D_minus, job.ch_objects)
            imgfilename = 'hf_hfq0-%s.png' % job.job_id
            pylab.savefig(imgfilename)
            
def plot_totalcharge():
    jobs_orig.sort(key=lambda job: job.Pe)
    for ch in (10, 50, 200):
        xs = [job.Pe for job in jobs_orig if job.ch_objects == ch]
        if xs:
            pylab.plot(xs, 
                       [job.totalcharge[0]
                        for job in jobs_orig if job.ch_objects==ch], 
                       'o-', label=r'$Q=%.0f$ particle 10'%ch)
            pylab.plot(xs, 
                       [job.totalcharge[1]
                        for job in jobs_orig if job.ch_objects==ch], 
                       'o-', label=r'$Q=%.0f$ particle 11'%ch)
    pylab.xscale('log')
    pylab.xlabel(r'$Pe$')
    pylab.ylabel(r'charge')
    pylab.legend(loc='best')
    pylab.savefig('totalcharge.png')
    
    
def main():
    print 'working here'
    plot_dip('dip_norm')


if __name__ == '__main__':
    main()

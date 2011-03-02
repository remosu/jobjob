#!/usr/bin/env python

import sys
import os
import glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import pylab
from matplotlib.colors import LogNorm

import jobjob.jobs
import jobjob.utils


#jobsu0 = [jobjob.jobs.Job(*os.path.split(path)) 
#          for path in glob.glob('/mnt/elb_data/D0.0*/out/out/par_*')]
#dd = dict((job.input, job) for job in jobsu0)

#jobs_orig = [jobjob.jobs.Job(*os.path.split(input)) 
#             for input in glob.glob('/media/DATA/ELB/D0.0*/out/par_*')]

def get_jobs_from_tmpl(tmpl):
    return [jobjob.jobs.Job(*os.path.split(input))
            for input in glob.glob(tmpl)]

jobs_tmpls = (
    'r[127]*/Dist_[127]*_vertical_Flux/*Q10*/out/par_*',
    'r[127]*/Dist_[127]*_vertical_Flux/*Q50*/out/par_*',
    'r[127]*/Dist_[127]*_vertical_Flux/*Q200*/out/par_*',
    )
#print 'jobs_tmpls', jobs_tmpls
jobs_orig = []
for tmpl in jobs_tmpls:
    jobs_orig += get_jobs_from_tmpl(tmpl)

tmplQ0 = 'r[127]*/Dist_[127]*_vertical_Flux/*Q0*/out/par_*'
jobs_ch0 = [jobjob.jobs.Job(*os.path.split(input)) 
            for input in glob.glob(tmplQ0)]
dd_ch0 = dict((job.make_key('u_y', 'D_minus', 'D_plus', 'r_pair'), job) for job in jobs_ch0)             


workdir = os.getcwd()
#tmplu0 = os.path.join(workdir.rsplit('_', 2)[0]+'_NoFlux','*Q*', 'out', 'par_*')
#print tmplu0
#jobs_u0 = get_jobs_from_tmpl(tmplu0)
tmplu0 = 'r[127]*/Dist_[127]*_NoFlux/*Q*/out/par_*'
jobs_u0 = [jobjob.jobs.Job(*os.path.split(input)) 
            for input in glob.glob(tmplu0)]
dd_ch0 = dict((job.make_key('u_y', 'D_minus', 'D_plus', 'r_pair'), job) for job in jobs_ch0)             
dd = dict((job.make_key('ch_objects', 'D_minus', 'r_pair'), job) 
          for job in jobs_u0)

for job in jobs_orig:
    print job.path
    dd_key = job.make_key('ch_objects', 'D_minus', 'r_pair')
    dd_job = dd.get(dd_key)
    job.job_u0 = dd_job
    if dd_job is not None:
        print '    >>>', dd_job.path
        hf_eq10 = np.mean(dd[dd_key].HydroForce_c10[-1000:])
        hf_eq11 = np.mean(dd[dd_key].HydroForce_c11[-1000:])

        hf10 = job.HydroForce_c10 - hf_eq10
        hf11 = job.HydroForce_c11 - hf_eq11
        
        ef10 = job.ElForce_c10 + hf_eq10
        ef11 = job.ElForce_c11 + hf_eq11
        job.ef10, job.ef11, job.hf10, job.hf11 = ef10, ef11, hf10, hf11
        job.hf_eq10, job.hf_eq11 = hf_eq10, hf_eq11
    
    job.job_ch0 = dd_ch0.get(job.make_key('u_y', 'D_minus', 'D_plus', 'r_pair'), None)

#jobs_orig = [job for job in jobs_orig if all((job.job_ch0, job.job_u0))]
jobs_orig = [job for job in jobs_orig if job.job_u0]

print len(jobs_orig), len(jobs_ch0), len(jobs_u0)

def mk_jobs_u0():
    print ""
    print "new jobs: u_x = 0.0 ..."
    ujobs = dict()
    for job in jobs_orig:
        key = job.make_key('ch_objects', 'D_minus', 'r_pair')
        ujobs[key] = job
    for job in ujobs.values():
        #binfile = os.path.basename(job.get_binfile())
        #print """
        #mk_jobdir({'D_minus':[%s], 
        #           'ch_objects':[%s], 
        #           'restart':['%s']})
        #""" % (job.D_minus, job.ch_objects, binfile)
        #src = os.path.join(job.path, job.input)
        dstdir = os.path.join('/home/rene/Work/ELB_data/r20u0',
                              'Q%sD%s' % (job.ch_objects, job.D_minus))
        os.system('cp "%s" "%s"' % (job.get_binfile(), dstdir))
        

def plot_forces_orig():
    for job in jobs_orig:
        pylab.clf()    

        pylab.subplot(211)
        pylab.title(r'$u=%.4f,\  D=%.4f,\ Q=%i$' % 
                    (job.u_abs, job.D_minus, job.ch_objects))

        pylab.plot(job.ElForce_c10, label='particle 10')
        pylab.plot(job.ElForce_c11, label='particle 11')
        pylab.legend(loc='best')
        pylab.ylabel('elec force')

        pylab.subplot(212)
        pylab.plot(job.HydroForce_c10, label='particle 10')
        pylab.plot(job.HydroForce_c11, label='particle 11')
        #~ pylab.legend(loc='best')
        pylab.ylabel('hydro force')
        
        #imgfilename = 'u_x%.4fD%.4fch%03i.png' % (job.u_x, job.D_minus, job.ch_objects)
        imgfilename = 'plot_forces_orig_%s.png' % job.job_id
        pylab.savefig(imgfilename)

def plot_forces():
    for job in jobs_orig:
        pylab.clf()    

        pylab.subplot(211)
        pylab.title(r'$u=%.4f,\  D=%.4f,\ Q=%i$' % 
                    (job.u_abs, job.D_minus, job.ch_objects))

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
                       'o-', label=r'Q=%.0f\ [*%.3f]'%(ch, factor))
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
                       'o-', label=r'$Q=%.0f$'%ch)
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
        pylab.title(r'$u=%.4f,\  D=%.4f,\ Q=%i$ ' %
                ((job.u_x**2+job.u_y**2)**0.5, job.D_minus, job.ch_objects))
        car = pylab.imshow(plane, vmin=-0.001, vmax=0.0, 
                           interpolation='nearest')
        pylab.contour(plane, contour_values, linestyles='dashed', 
                                             colors='white')
        print job.u_x, job.u_y
        pylab.grid(True)
        pylab.colorbar(car)
        pylab.arrow(1, 1, 2*job.u_x/(job.u_x if job.u_x else 1.0), 2*job.u_y/(job.u_y if job.u_y else 1.0), width=0.5)
        #imgfilename = 'plane_r20-y50-u_x%.4fD%.4fch%03i.png' % \
        #              (job.u_x, job.D_minus, job.ch_objects)
        imgfilename = 'plane_%s.png' % job.job_id
        pylab.savefig(imgfilename)
        
def plot_ch_chq0():
    for job in jobs_orig:
        if job.job_ch0:
            pylab.clf()
            pylab.title(r'$u=%.4f,\  D=%.4f,\ ch=%i$' % 
                        (job.u_abs, job.D_minus, job.ch_objects))

            print job.path, len(job.hf10), len(job.job_ch0.HydroForce_c10)
            start = 1000
            end = min(len(job.hf10), len(job.job_ch0.HydroForce_c10))
            print end
            ys = (job.hf10[:end]/job.job_ch0.HydroForce_c10[:end])[start:]
            xs = range(start, start+len(ys))
            pylab.plot(xs, ys, label='hf/hf(Q=0) -- 10')
            end = min(len(job.hf11), len(job.job_ch0.HydroForce_c11))
            print end
            ys = (job.hf11[:end]/job.job_ch0.HydroForce_c11[:end])[start:]
            xs = range(start, start+len(ys))
            pylab.plot(xs, ys, label='hf/hf(Q=0) -- 11')
            pylab.legend(loc='best')
            pylab.ylabel('hydro force / hydro force(Q=0)')
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
                       'o-', label=r'Q=%.0f particle 10'%ch)
            pylab.plot(xs, 
                       [job.totalcharge[1]
                        for job in jobs_orig if job.ch_objects==ch], 
                       'o-', label=r'Q=%.0f particle 11'%ch)
    pylab.xscale('log')
    pylab.xlabel(r'$Pe$')
    pylab.ylabel(r'charge')
    pylab.legend(loc='best')
    pylab.savefig('totalcharge.png')

def plot_foo():
    """docstring for plot_foo"""
    print len(jobs_orig)
    jobs_orig.sort(key=lambda job: job.Pe)
    jobs_orig.sort(key=lambda job: job.r_pair)
    for ch in [10, 50, 200]:
        pylab.clf()
        #print [jobi for jobi in jobs_orig if jobi.ch_objects==ch]
        jobs_to_plot = {}
        for job in [jobi for jobi in jobs_orig if int(jobi.ch_objects)==int(ch)]:
            grp = jobs_to_plot.setdefault(job.make_key('D_minus', 'u_y', ), [])
            grp.append(job)
        for grp in jobs_to_plot.values():
            xs = [job.r_pair for job in grp]
            #print xs
            #print 'ef10, ef11 =', job.ef10[-1], job.ef11[-1]
            #print 'ef10, ef11 =', job.ElForce_c10[-1], job.ElForce_c11[-1]
            ys = [(abs(job.ef11[-1]) - abs(job.ef10[-1])) #/ abs(job.job_u0.ElForce_c11[-1]) 
            #ys = [job.job_u0.ElForce_c11[-1] 
                    for job in grp]
            #print ys
            pylab.plot(xs, ys, '-o', label=r'$Pe=%.1f$'%grp[0].Pe)
        pylab.legend(loc='best')
        pylab.xlabel(r'$r_{pair}$')
        pylab.ylabel(r'$(|ef_{11}^n| - |ef_{10}^n|)$')
        #pylab.ylabel(r'$ef_{11}^n(u=0)$')
        pylab.savefig('grrr%s.png'%ch)
    #print 'lksdfjksldjfas>>>>>', [job.r_pair for job in jobs_orig]

    
    
def main():
    print 'working here'
    #plot_dip('dip_norm')
    plot_forces_orig()


if __name__ == '__main__':
    main()

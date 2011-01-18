""" ... """

import os
import glob
import itertools
import numpy as np
from jobjob.utils import read_vars, cache_result

class Job(object):
    
    def __init__(self, path, input='input'):
        self.path = path
        self.input = input
        self.load_input(os.path.join(self.path, input))
        
    def load_input(self, input_filename):
        self.__dict__.update(dict(read_vars(input_filename)))
        
    def make_key(self, *jobvars):
        return ''.join(var+str(getattr(self, var)) for var in jobvars)
        
    def get_field_last(self):
        data_filename_mask = os.path.join(self.path, 'oelb_lattice_*.elb')
        data_filenames = glob.glob(data_filename_mask)
        data_filenames.sort(key=lambda s: int(s.rpartition('_')[-1].split('.')[0]))
        return data_filenames[-1]
        
    def get_logfile(self):
        data_filename_mask = os.path.join(self.path, 'log_*')
        data_filenames = glob.glob(data_filename_mask)
        return data_filenames[0]
    
    @property
    @cache_result()
    def v_inf(self):
        starts = [' '.join(values) 
                  for values in itertools.product(('1', '100'), 
                                                  ('1', '100'), 
                                                  ('0', '99'))]
        
        data_filename = self.get_field_last()
        data = open(data_filename)
        vs = np.array([float(line.split()[3]) 
                      for line in data if any(line.startswith(s) for s in starts)])
        return vs

    @property
    def Pe(self):
        return self.v_inf.mean() * self.r_eff / self.D_minus
        
    @property
    @cache_result()
    def HydroForce_c10(self):
            pass

    @property
    @cache_result()
    def HydroForce_c11(self):
            pass
            
    @property
    @cache_result()
    def ElForce_c10(self):
            pass

    @property
    @cache_result()
    def ElForce_c11(self):
            pass
            
    @property
    @cache_result()
    def pos_cpm(self):
        data_filename = self.get_field_last()
        adata = np.array([map(float, 
                              line.split()[:3]+line.split()[11:13]) 
                              for line in open(data_filename)])
        #data = []
        #for line in open(data_filename):
        #    line_split = line.split()
        #    try:
        #        data.append([float(v) for v in line_split[:3]  + line_split[11:13]])
        #    except Exception as e:
        #        print line_split
        #        raise e
        return adata
            
    @property
    @cache_result()
    def dip(self):
        print self.path
        print 'loading data...'
        adata = self.pos_cpm
        print 'data loaded!'
        pos_10 = self.position(10)
        pos_11 = self.position(11)
        pos = adata[:, :3] - (37.5, 50.0, 50.0)
        c_p = adata[:, -2]
        c_p.shape = (-1, 1)
        c_m = adata[:, -1]
        c_m.shape = (-1, 1)
        
        ccp = (pos * c_p).sum(axis=0)
        ccm = (pos * c_m).sum(axis=0)
        return ccp - ccm
        
    @property
    @cache_result()
    def dip_norm(self):
        print self.path
        print 'loading data...'
        adata = self.pos_cpm
        print 'data loaded!'
        pos = adata[:, :3]
        c_p = adata[:, -2]
        c_p.shape = (-1, 1)
        c_m = adata[:, -1]
        c_m.shape = (-1, 1)
        
        ccp = (pos * c_p).sum(axis=0) / c_p.sum()
        ccm = (pos * c_m).sum(axis=0) / c_m.sum()
        return ccp - ccm
        
        
    def position(self, colloid):
        command = 'grep "Placed COLLOID %i in" %s' % \
                   (colloid, self.get_logfile())
        r = os.popen(command).read()
        return np.array(map(float, r.split()[-3:]))
        
        
    #@property
    @cache_result()
    def plane(self, x=None, y=None, z=None):
        chs = {'plus':3, 'minus':4}
        value_plane = x or y or z
        index_plane = 0 if x else 1 if y else 2 
        indices = (1,2) if x else (0,2) if y else (0,1) 
        #indices = indices + (chs[ch], )
        indices = indices + (3, 4)
        print value_plane, index_plane, indices
        data = self.pos_cpm
        plane = np.zeros((100,100))
        plane_index = data[:, index_plane] == value_plane
        plane_full = data[plane_index][:,indices]-(1,0,0,0)
        for i,j,c_p,c_m in plane_full:
            plane[int(i),int(j)] = c_p - c_m
        return plane.transpose()
        
    @property
    @cache_result()
    def totalcharge(self):
        data_filename = self.get_field_last()
        ct_10 = 0
        ct_11 = 0
        for line in open(data_filename):
            values = line.split()
            pos = np.array(values[:3], dtype=float)
            pos10 = np.array([25.0, 50.0, 50.0])
            pos11 = np.array([50.0, 50.0, 50.0])
            if 10.0 < np.linalg.norm(pos - pos10) < 12.5:
                ct_10 += float(values[-1])
            elif 10.0 < np.linalg.norm(pos - pos11) < 12.5:
                ct_11 += float(values[-1])
        return [ct_10, ct_11]
    
    
        

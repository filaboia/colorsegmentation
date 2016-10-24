# This Python file uses the following encoding: utf-8
from __future__ import division
import numpy as np

def convertrgbtoxyz(f):
    g = np.empty(f.shape)
    g[0] = f[0] * 0.412453 + f[1] * 0.357580 + f[2] * 0.180423
    g[1] = f[0] * 0.212671 + f[1] * 0.715160 + f[2] * 0.072169 
    g[2] = f[0] * 0.019334 + f[1] * 0.119193 + f[2] * 0.950227 
    return g
    
def convertxyztorgb(f):
    g = np.empty(f.shape)
    g[0] = f[0] * 3.240479  + f[1] * -1.53715  + f[2] * -0.498535 
    g[1] = f[0] * -0.969256 + f[1] * 1.875991  + f[2] * 0.041556 
    g[2] = f[0] * 0.055648  + f[1] * -0.204043 + f[2] * 1.057311
    return g
    
def convertrgbtolab(f):
    def function(t):
        g = np.empty(t.shape)
        mask = t > 0.008856
        g[mask] = pow(t[mask], 1./3.)
        mask = t <= 0.008856
        g[mask] = 7.787 * t[mask] + 0.137931
        return g

    max_dtype = np.iinfo(f.dtype).max
    g = np.empty(f.shape)
    h = convertrgbtoxyz(f)
    
    X = h[0] / 0.950456 / max_dtype
    Y = h[1] / 1.       / max_dtype
    Z = h[2] / 1.088754 / max_dtype
    
    g[0] = 116. * function(Y) - 16.
    g[1] = 500. * (function(X) - function(Y))
    g[2] = 200. * (function(Y) - function(Z))
    
    g[0] *= max_dtype / 100.
    g[1] = (g[1] + 127.) / 254. * max_dtype
    g[2] = (g[2] + 127.) / 254. * max_dtype
    
    return np.clip(np.round(g), 0, max_dtype).astype(f.dtype)
    
def convertlabtorgb(f):
    def function(t):
        g = np.empty(t.shape)
        mask = t > 0.206893
        g[mask] = pow(t[mask], 3.)
        mask = t <= 0.206893
        g[mask] =  (t[mask] - 0.137931) / 7.787
        return g
        
    max_dtype = np.iinfo(f.dtype).max
        
    faux = np.empty(f.shape)    
    faux[0] = f[0] / max_dtype * 100. 
    faux[1] = f[1] / max_dtype * 254. - 127.
    faux[2] = f[2] / max_dtype * 254. - 127.
        
    g = np.empty(f.shape)
    g[0] = function(faux[1]/500. + ((faux[0]+16.)/116.)) * 0.950456 * max_dtype
    g[1] = function((faux[0]+16.)/116.) * max_dtype
    g[2] = function(((faux[0]+16.)/116.) - faux[2]/200.) * 1.088754 * max_dtype
    
    h = convertxyztorgb(g)
    
    return np.clip(np.round(h), 0, max_dtype).astype(f.dtype)
    
def convertrgbtoluv(f):
    max_dtype = np.iinfo(f.dtype).max
    
    z, x, y = f.shape
    g = np.zeros(f.shape)
    vl = np.zeros((x,y))
    ul = np.zeros((x,y))
    h = convertrgbtoxyz(f)
    
    X = h[0] / 0.950456 / max_dtype
    Y = h[1] / 1.       / max_dtype
    Z = h[2] / 1.088754 / max_dtype
    
    mask = Y > 0.008856
    g[0][mask] = 116. * pow(Y[mask], 1./3.) - 16.
    mask = Y <= 0.008856
    g[0][mask] = 903.296296 * Y[mask]
    
    mask = (X + 15. * Y + 3. * Z) > 0
    ul[mask] = 4. * X[mask] / (X[mask] + 15. * Y[mask] + 3. * Z[mask])
    vl[mask] = 9. * Y[mask] / (X[mask] + 15. * Y[mask] + 3. * Z[mask])
    
    g[1] = 13. * g[0] * (ul - 0.19793943)
    g[2] = 13. * g[0] * (vl - 0.46831096)
    
    g[0] *= max_dtype / 100.
    g[1] = (g[1] + 134.) * max_dtype / 354.  
    g[2] = (g[2] + 140.) * max_dtype / 262.
    
    return np.clip(np.round(g), 0, max_dtype).astype(f.dtype)
    
def convertluvtorgb(f):
    max_dtype = np.iinfo(f.dtype).max

    z, x, y = f.shape
    g = np.zeros(f.shape)
    vl = np.zeros((x,y))
    ul = np.zeros((x,y))
    
    L = f[0] * 100. / max_dtype
    u = f[1] * 354. / max_dtype - 134.
    v = f[2] * 262. / max_dtype - 140.
    
    mask = L > 0
    ul[mask] = u[mask] / (13. * L[mask]) + 0.19793943
    vl[mask] = v[mask] / (13. * L[mask]) + 0.46831096
    
    mask = L > 8
    g[1][mask] = pow((L[mask] + 16.) / 116., 3.)
    mask = L <= 8
    g[1][mask] = L[mask] / 903.296296
    
    mask = vl > 0
    g[0][mask] = g[1][mask] * 9. * ul[mask] / (4. * vl[mask])
    g[2][mask] = g[1][mask] * (12. - 3. * ul[mask] - 20. * vl[mask]) / (4. * vl[mask])
    
    g[0] *= 0.950456 * max_dtype
    g[1] *= 1. * max_dtype
    g[2] *= 1.088754 * max_dtype
    
    h = convertxyztorgb(g)
    return np.clip(np.round(h), 0, max_dtype).astype(f.dtype)
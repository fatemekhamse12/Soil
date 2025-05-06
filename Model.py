import pandas as pd
import numpy as np 
import datetime as date 
import math as math 
import matplotlib.pyplot as plt

from scipy.stats import pearsonr
from sklearn.metrics import r2_score 
from sklearn.metrics import mean_squared_error

class model:
     def __init__(self,sw0,cn2,prc,wp,fc,n,c,kh,pet,et0,pro,lai):
          self.sw0=sw0
          self.cn2=cn2
          self.prc=prc
          self.wp=wp
          self.fc=fc
          self.n=n
          self.c=c
          self.kh=kh
          self.pet=pet
          self.et0=et0
          self.pro=pro
          self.lai=lai
class inc(model):
     def __init__(self, sw0, cn2, prc, wp, fc, n, c, kh,pet,et0,pro,lai):
          super().__init__(sw0, cn2, prc, wp, fc, n, c, kh,pet,et0,pro,lai)
     def smax(self):
          return 0.935+0.498*self.lai-0.00575*self.lai**2
     def sv(self):
          return self.smax()*(1-math.exp(-(0.046*self.lai)*(self.prc/self.smax())))
     def prc2(self):
          return self.prc-self.sv()

class runoff(inc):
     def __init__(self, sw0, cn2, prc, wp, fc, n, c, kh,pet,et0,pro,lai):
          super().__init__(sw0, cn2, prc, wp, fc, n, c, kh,pet,et0,pro,lai)
     
     def sr(self):
          return 25.4*((100/self.cn2)-1)
     def SRP(self):
          if self.prc2()>0.3*self.sr():
               return (self.prc2()-0.3*self.sr())**2/(self.prc2()+0.7*self.sr())
          else:
               return 0
          
     def sw3(self):
          #return self.sw3()-self.SRP()/1000
          return self.sw0+self.prc/(1000*self.n)-self.SRP()/(1000*self.n)
          #return self.sw3()
  
class DEEP(runoff):
     def __init__(self, sw0, cn2, prc, wp, fc, n, c, kh,pet,et0,pro,lai):
          super().__init__(sw0, cn2, prc, wp, fc, n, c, kh,pet,et0,pro,lai)
     def sw3(self):
          return super().sw3()
     def dp(self):
           if self.sw0>self.fc:
                return self.prc-self.SRP()-(self.fc-self.sw0)*1000*self.n
           else:
                return 0
         
     def sw2(self):
          return self.sw3()-self.dp()/(1000*self.n)
         
class ET(DEEP):
     def __init__(self, sw0, cn2, prc, wp, fc, n, c, kh,pet,et0,pro,lai):
          super().__init__(sw0, cn2, prc, wp, fc, n, c, kh,pet,et0,pro,lai)
     def pro_m(self):
          if self.pet<5:
               # modify soil water depletion based on refrence ET 
               return self.pro+0.04*(5-self.pet)
          else:
               return self.pro
     def sw2(self):
          return super().sw2()

     def RAW(self):
          
          return ((self.pro_m())*(self.fc-self.wp))
     def TAW(self):
          return self.fc-self.wp
     def dr(self):
          return self.fc-self.sw2()
     def ks(self):
          if self.dr()>self.RAW():
               return (self.TAW()-self.dr())/((1-self.pro_m())*self.TAW())
          else:
               return 1 
          
     def ETC(self):
          # estimate ET considring soil moisture if it is less than RAW  it will be multiply to ks less than 1 
          return self.pet*self.ks()
     def sm(self):
          if (self.ETC()/(1000*self.n))<=self.sw2()-self.wp:
                  return self.sw2()-self.ETC()/(1000*self.n)
          if (self.ETC()/(1000*self.n))>self.sw2()-self.wp:
               return self.wp
               # assuming that soil water content cant be below wp 
           #return self.sw2()-self.ETC()/(1000*self.n)
                 #return a
     
               #return self.sw2()-(self.pet/(self.wp*1000))/(1000*self.n)
     def evap(self):
          if (self.ETC()/(1000*self.n))<=(self.sw2()-self.wp):
                  return self.ETC()
          if (self.ETC()/(1000*self.n))>(self.sw2()-self.wp):
                 return (self.wp)*self.ETC()
    
     
     
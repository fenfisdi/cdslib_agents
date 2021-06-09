# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:40:33 2021

@author: Carolina
"""
import numpy as np
import matplotlib.pyplot as plt

plt.figure()
delta_angles_0 = np.loadtxt('Data delta_angles_0.csv')

plt.hist(delta_angles_0, bins = 10)
plt.title('Delta_angles_0')
plt.show()

plt.figure()
angle_variation = np.loadtxt('Data angle_variation.csv')
plt.hist(angle_variation, bins = 10)
plt.title('Angle_variation')
plt.show()
import matplotlib.pyplot as plt
import numpy as np

result_simu0 = [0, 0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1]
result_simu1 = [0, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000, 100000]
result_simu2 = [0, 100000, 94140.98092949, 95747.75854672, 96338.17340632, 96467.21218882, 96510.12951217, 96546.94710641,  96601.57833933, 96671.73591867, 96745.47208339]       
result_simu3 = [0, 100000, 102806.41078048, 105229.61052072, 108059.33017593, 110936.15808083, 113844.47262942, 116790.07434998,  119742.35101481, 122674.35467603, 125545.70580768]
result_simu4 = [0, 298, 292.80590867, 294.2752874 , 295.01742587, 295.28404964, 295.44293831, 295.58498173, 295.73556218, 295.89315089, 296.04686556]
result_simu5 = [0, 298, 300.33680868, 302.50993316, 305.58850358, 308.71236212, 311.91148464, 315.21468932, 318.59210694, 322.01069416, 325.37326092]
result_simu6 = [0, 100000,100000,94140.98092949,95747.75854672,96338.17340632,96467.21218882,96510.12951217,96546.94710641,96601.57833933,96671.73591867]
result_simu7 = [0, 0.14691334, 0.1386783,  0.14010107, 0.13999715, 0.13928553, 0.13845963, 0.1371978,  0.13563929, 0.13405475, 0.1324996]

plt.figure(1, figsize=(13, 12))

plt.subplot(221)
plt.plot(result_simu0,result_simu2,'r',result_simu0,result_simu3,'g')
plt.xlabel('Time [s]')
plt.ylabel('Compressor Pressure [Pa]')

plt.subplot(222)
plt.plot(result_simu0,result_simu4,'r',result_simu0,result_simu5,'g')
plt.xlabel('Time [s]')
plt.ylabel('Compressor Temperature [K]')

plt.subplot(223)
plt.plot(result_simu0, result_simu7,'b')
plt.xlabel('Time [s]')
plt.ylabel('Massic Flow [kg/s]')

plt.subplot(224)
plt.plot(result_simu0,result_simu1,'r',result_simu0,result_simu6,'b')
plt.xlabel('time [s]')
plt.ylabel('Air Filter Pressure [Pa]')

plt.suptitle('Simple Engine Model - PySyC Implementation')
plt.show()
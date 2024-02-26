# MAIN
import numpy as np
import matplotlib.pyplot as plt
import math
import time
import sys
import os
#for path in sys.path:
    #print(path)
sys.path.append("C:\ANSYSDev\demopy0d\src")
from configparser import ConfigParser
from ansys.solutions.thermalengine0d.model.Library_ThermoFluid_class import Compressor_Tf, PressureLosses_R, Volume_C, EffortSource, FlowSource
from ansys.solutions.thermalengine0d.model.scripts.Fluid_properties_class import FluidFuel
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortM, FlowM
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolv

time1 = time.time()
"-----------------------------------------------------------"
"SIMULATION PARAMETER"
"-----------------------------------------------------------"
start_simu = 0
end_simu = 0.1
step_simu = 0.01
sample_time = 0.01
LastVal = (end_simu - start_simu) / step_simu

"-----------------------------------------------------------"
"SIMULATION CONFIG IMPORT"
"-----------------------------------------------------------"
directory = "C:\ANSYSDev\demopy0d\src\ansys\solutions\thermalengine0d\model\scripts"
filename = "ModelSimple_init.ini"
filePath = os.path.join(os.path.abspath(os.path.curdir), 'src', 'ansys', 'solutions', 'thermalengine0d', 'model', 'scripts', 'ModelSimple_init.ini')
config = ConfigParser()
print(os.path.abspath(os.path.curdir))
if os.path.isfile(filePath):
    config.read(filePath)
else:
    print("file not found")
#config.read('ModelSimple_init.ini')

"-----------------------------------------------------------"
"INIT"
"-----------------------------------------------------------"
Pair = 1e5
Tair = 298
P0 = 90000
T0 = 293
Ks = 14.4
LHV = 42800000
Hv = 230000
nC = 10.8
nH = 18.7
Nturbo = 120000
incr = 0

Fuel = FluidFuel(Ks, LHV, Hv, nC, nH)
Ambient_Air = EffortSource(Pair, Tair)
Flow_init = FlowSource(0, T0)

"Creation of vectors for saving / plots"
result_simu = np.zeros((int(LastVal+1 * step_simu / sample_time), 9))
time_simu = np.arange(1, LastVal+2)

"-----------------------------------------------------------"
"MODEL CREATION"
"-----------------------------------------------------------"
AirFilter = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
VolumeAirFilter = Volume_C(Flow_init.F, Flow_init.F)
Compressor = Compressor_Tf(Ambient_Air.E, Ambient_Air.E, FlowM(Nturbo / 30 * math.pi))
VolumeCompr = Volume_C(Flow_init.F, Flow_init.F)

"-----------------------------------------------------------"
"MODEL PARAM"
"-----------------------------------------------------------"
AirFilter.Param(eval(config['AirFilter_param']['k_pl_af']))
VolumeAirFilter.Param(eval(config['AirFilter_param']['vol_af']))
Compressor.Param(eval(config['Compr_param']['prefc']), eval(config['Compr_param']['trefc']),
                 eval(config['Compr_param']['x_nc']), eval(config['Compr_param']['surge_pr']),
                 eval(config['Compr_param']['y_margin']), eval(config['Compr_param']['z_flow_cor']),
                 eval(config['Compr_param']['z_eta_comp']))
VolumeCompr.Param(eval(config['Compr_param']['vol_compr']))
"-----------------------------------------------------------"
"SIMULATION"
"-----------------------------------------------------------"
time_simu[0]=start_simu
incr_save_old = 0
method = 'Euler'

for i in range(1, int(LastVal+1)):
    time_simu[i] = i * step_simu + start_simu
    "Pedal position=f(time_simu)"
    N = interpolv([0, 5, 5.01, 10.5, 10.51, 15], [120000, 120000, 150000, 150000, 130000, 130000], time_simu[i])

    "AirFilter"
    AirFilter.E1 = Ambient_Air.E
    AirFilter.E2 = VolumeAirFilter.E1
    AirFilter.Solve()

    '''
    print(incr)
    incr = incr + 1
    print("AirFilter")
    print("AirFilter.E1.h: " + str(AirFilter.E1.h))
    print("AirFilter.E1.P: " + str(AirFilter.E1.P))
    print("AirFilter.E1.R: " + str(AirFilter.E1.R))
    print("AirFilter.E1.T: " + str(AirFilter.E1.T))
    print("AirFilter.E2.h: " + str(AirFilter.E2.h))
    print("AirFilter.E2.P: " + str(AirFilter.E2.P))
    print("AirFilter.E2.R: " + str(AirFilter.E2.R))
    print("AirFilter.E2.T: " + str(AirFilter.E2.T))
    print("AirFilter.F1.Qm: " + str(AirFilter.F1.Qm))
    print("AirFilter.F1.Qmh: " + str(AirFilter.F1.Qmh))
    print("AirFilter.F2.Qm: " + str(AirFilter.F2.Qm))
    print("AirFilter.F2.Qmh: " + str(AirFilter.F2.Qmh))
    print("")
    '''

    VolumeAirFilter.F1 = AirFilter.F2
    VolumeAirFilter.F2 = Compressor.F1
    VolumeAirFilter.Solve(step_simu, method)

    '''
    print("VolumeAirFilter")
    print("VolumeAirFilter.E1.h: " + str(VolumeAirFilter.E1.h))
    print("VolumeAirFilter.E1.P: " + str(VolumeAirFilter.E1.P))
    print("VolumeAirFilter.E1.R: " + str(VolumeAirFilter.E1.R))
    print("VolumeAirFilter.E1.T: " + str(VolumeAirFilter.E1.T))
    print("VolumeAirFilter.E2.h: " + str(VolumeAirFilter.E2.h))
    print("VolumeAirFilter.E2.P: " + str(VolumeAirFilter.E2.P))
    print("VolumeAirFilter.E2.R: " + str(VolumeAirFilter.E2.R))
    print("VolumeAirFilter.E2.T: " + str(VolumeAirFilter.E2.T))
    print("VolumeAirFilter.F1.Qm: " + str(VolumeAirFilter.F1.Qm))
    print("VolumeAirFilter.F1.Qmh: " + str(VolumeAirFilter.F1.Qmh))
    print("VolumeAirFilter.F2.Qm: " + str(VolumeAirFilter.F2.Qm))
    print("VolumeAirFilter.F2.Qmh: " + str(VolumeAirFilter.F2.Qmh))
    print("")
    '''
    "Compressor"
    Compressor.E1 = VolumeAirFilter.E2
    Compressor.E2 = VolumeCompr.E1

    Compressor.Fm = FlowM(N / 30 * math.pi)
    Compressor.Solve()

    '''
    print("compressor")
    print("Compressor.E1.h: " + str(Compressor.E1.h))
    print("Compressor.E1.P: " + str(Compressor.E1.P))
    print("Compressor.E1.T: " + str(Compressor.E1.T))
    print("Compressor.E2.h: " + str(Compressor.E2.h))
    print("Compressor.E2.P: " + str(Compressor.E2.P))
    print("Compressor.E2.T: " + str(Compressor.E2.T))
    print("Compressor.F1.Qm: " + str(Compressor.F1.Qm))
    print("Compressor.F1.Qmh: " + str(Compressor.F1.Qmh))
    print("Compressor.F2.Qm: " + str(Compressor.F2.Qm))
    print("Compressor.F2.Qmh: " + str(Compressor.F2.Qmh))
    print("")  
    '''
    VolumeCompr.F1 = Compressor.F2
    VolumeCompr.F2 = FlowSource(-0.1, Compressor.E2.T)
    VolumeCompr.Solve(step_simu, method)
    '''
    print("VolumeCompressor")
    print("VolumeCompr.E1.h: " + str(VolumeCompr.E1.h))
    print("VolumeCompr.E1.P: " + str(VolumeCompr.E1.P))
    print("VolumeCompr.E1.R: " + str(VolumeCompr.E1.R))
    print("VolumeCompr.E1.T: " + str(VolumeCompr.E1.T))
    print("VolumeCompr.E2.h: " + str(VolumeCompr.E2.h))
    print("VolumeCompr.E2.P: " + str(VolumeCompr.E2.P))
    print("VolumeCompr.E2.R: " + str(VolumeCompr.E2.R))
    print("VolumeCompr.E2.T: " + str(VolumeCompr.E2.T))
    print("VolumeCompr.F1.Qm: " + str(VolumeCompr.F1.Qm))
    print("VolumeCompr.F1.Qmh: " + str(VolumeCompr.F1.Qmh))
    print("VolumeCompr.F2.Qm: " + str(VolumeCompr.F2.Qm))
    print("VolumeCompr.F2.Qmh: " + str(VolumeCompr.F2.Qmh))
    print("")
    '''
    "-----------------------------------------------------------"
    "Save results according to the defined sample time"
    "-----------------------------------------------------------"
    #incr_save = math.floor(i * step_simu / sample_time)
    #if incr_save > incr_save_old:
    #    print ("time="+repr(time_simu[i]))
    #    result_simu[incr_save, 0] = time_simu[i]
    #    result_simu[incr_save, 1] = Pair
    #    result_simu[incr_save, 2] = Compressor.E1.P   #changes when setting Compressor.E1
    #    result_simu[incr_save, 3] = Compressor.E2.P   #changes when setting Compressor.E2
    #    result_simu[incr_save, 4] = Compressor.E1.T   #changes when setting Compressor.E1
    #    result_simu[incr_save, 5] = Compressor.E2.T   #changes when setting Compressor.E2
    #    result_simu[incr_save, 6] = AirFilter.E2.P
    #    result_simu[incr_save, 7] = Compressor.F2.Qm #changes after solve
    #    result_simu[incr_save, 8] = N

    #incr_save_old = incr_save

time2 = time.time()
print("Time for Simulation", repr(round((time2 - time1), 5)))
#print("Time for Simulation", repr(round((time2 - time1)*10)/10))
"-----------------------------------------------------------"
"PLOTS"
"-----------------------------------------------------------"
#print(result_simu)
'''
plt.figure(1)
plt.subplot(221)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'r',result_simu[0:incr_save, 0],result_simu[0:incr_save, 3],'g')
plt.ylabel('Compressor Pressure [Pa]')
plt.subplot(222)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 4],'b',result_simu[0:incr_save, 0],result_simu[0:incr_save, 5],'r')
plt.ylabel('Compressor Temperature [K]')
plt.subplot(223)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 7])
plt.xlabel('time [s]')
plt.ylabel('Massic Flow [kg/s]')
plt.subplot(224)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 1],'r',result_simu[0:incr_save, 0],result_simu[0:incr_save, 6],'b')
plt.xlabel('time [s]')
plt.ylabel('Air Filter Pressure [Pa]')
plt.show()
'''
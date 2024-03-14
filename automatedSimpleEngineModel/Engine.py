#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
Engine

Inputs:
    - E1h
    - E1P
    - E1T
    - E2h
    - E2P
    - E2T
Outputs:
    - F1Qm
    - F1Qmh
    - F2Qm
    - F2Qmh

"""
print("engine.py")
import argparse
import os
import sys
import math

import matplotlib.pyplot as plt
import numpy as np

if sys.platform.startswith("win"):
    for p in os.environ["PYTHON_DLL_PATH"].split(os.pathsep):
        try:
            os.add_dll_directory(p)
        except (FileNotFoundError, OSError):
            pass  # skip any paths that don't exist

from pyExt import SystemCouplingParticipant as sysc

from Library_ThermoFluid_class import Engine_Tf, EffortSource
from EffortFlowPort_class import FlowM
from Library_Fluid_class import Injector_Sf
from Fluid_properties_class import FluidFuel
import ModelSimple_init as config
from Data_treatment import interpolv

result_simu = np.zeros((6, 11))
incr_save = 1

#initial values
pAir = 1e5
tAir = 298

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "Engine"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    sc.addInputParameter(sysc.Parameter("E1h"))
    sc.addInputParameter(sysc.Parameter("E1P"))
    sc.addInputParameter(sysc.Parameter("E1T"))
    sc.addInputParameter(sysc.Parameter("E1R"))
    sc.addInputParameter(sysc.Parameter("E2h"))
    sc.addInputParameter(sysc.Parameter("E2P"))
    sc.addInputParameter(sysc.Parameter("E2T"))

    sc.addOutputParameter(sysc.Parameter("F1Qm"))
    sc.addOutputParameter(sysc.Parameter("F1Qmh"))
    sc.addOutputParameter(sysc.Parameter("F2Qm"))
    sc.addOutputParameter(sysc.Parameter("F2Qmh"))
    sc.addOutputParameter(sysc.Parameter("FAR"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
    #sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
else:
    # solve mode

    # initialize system
    ambientAir1 = EffortSource(pAir, tAir)
    ambientAir2 = EffortSource(pAir, tAir)
    fuel = FluidFuel(config.ks, config.lhv, config.hv, config.nc, config.nh)
    injector = Injector_Sf(0, fuel.LHV)
    engine = Engine_Tf(ambientAir1.E, ambientAir2.E, FlowM(0), injector, fuel, pAir, tAir)
    injector.Param(config.x_ne, config.y_pps_qinj, config.z_qinj)
    engine.Param(config.vcyl, 
                config.x_ne,
                config.y_rho1rho2,
                config.y_etavol_overall,
                config.z_etavol,
                config.z_etaind,
                config.z_etacomb)
    
    sc.setParameterValue("F1Qm", engine.F1.Qm)
    sc.setParameterValue("F1Qmh", engine.F1.Qmh)
    sc.setParameterValue("F2Qm", engine.F2.Qm)
    sc.setParameterValue("F2Qmh", engine.F2.Qmh)
    sc.setParameterValue("FAR", engine.FAR)
    i = 1
    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        startTime = sc.getCurrentTimeStep().startTime
        tsSize = sc.getCurrentTimeStep().timeStepSize
        n = interpolv([0.0, 5.0, 5.01, 7.5, 7.51, 10.0, 10.01, 15.0, 15.01, 20.0],
                      [2000.0, 2000.0, 2500.0, 2500.0, 3000.0, 3000.0, 3000.0, 3000.0, 3000.0, 3000.0], 
                      startTime + tsSize)
        pps = interpolv([0.0, 5.0, 5.01, 7.5, 7.51, 10.0, 10.01, 15.0, 15.01, 20.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0, 0.7, 0.7, 1.0, 0.8, 0.8], 
                        startTime + tsSize)
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")

            print(i)
            i +=1
            print(f"engine.E1.h: {engine.E1.h}")
            print(f"engine.E1.P: {engine.E1.P}")
            print(f"engine.E1.T: {engine.E1.T}")
            print(f"engine.E1.R: {engine.E1.R}")
            print(f"engine.E2.h: {engine.E2.h}")
            print(f"engine.E2.P: {engine.E2.P}")
            print(f"engine.E2.T: {engine.E2.T}")
            print()

            engine.Fm = FlowM(n / 30 * math.pi)

            sc.updateInputs()
            engine.E1.h = sc.getParameterValue("E1h")
            engine.E1.P = sc.getParameterValue("E1P")
            engine.E1.T = 273+40
            engine.E1.R = sc.getParameterValue("E1R")
            engine.E2.h = sc.getParameterValue("E2h")
            engine.E2.P = sc.getParameterValue("E2P")
            engine.E2.T = sc.getParameterValue("E2T")  

            injector.Solve(pps, engine.Fm)
            engine.Solve()

            sc.setParameterValue("F1Qm", engine.F1.Qm)
            sc.setParameterValue("F1Qmh",engine.F1.Qmh)
            sc.setParameterValue("F2Qm", engine.F2.Qm)
            sc.setParameterValue("F2Qmh",engine.F2.Qmh)
            sc.setParameterValue("FAR",engine.FAR)

            """sc.updateInputs()
            engine.E1.h = sc.getParameterValue("E1h")
            engine.E1.P = sc.getParameterValue("E1P")
            engine.E1.T = 273+40
            engine.E1.R = sc.getParameterValue("E1R")
            engine.E2.h = sc.getParameterValue("E2h")
            engine.E2.P = sc.getParameterValue("E2P")
            engine.E2.T = sc.getParameterValue("E2T")  

            engine.Fm = FlowM(n / 30 * math.pi)
            injector.Solve(pps, engine.Fm)
            engine.Solve()

            sc.setParameterValue("F1Qm", engine.F1.Qm)
            sc.setParameterValue("F1Qmh",engine.F1.Qmh)
            sc.setParameterValue("F2Qm", engine.F2.Qm)
            sc.setParameterValue("F2Qmh",engine.F2.Qmh)
            sc.setParameterValue("FAR",engine.FAR)"""
            sc.updateOutputs(sysc.Converged)
            multiIteration = True

            '''
            result_simu[incr_save, 0] = startTime + tsSize
            result_simu[incr_save, 1] = engine.Em.Tq
            result_simu[incr_save, 2] = engine.F1.Qm * -1
            result_simu[incr_save, 3] = engine.F2.Qm
            result_simu[incr_save, 4] = engine.FAR
            result_simu[incr_save, 5] = engine.E1.P
            result_simu[incr_save, 6] = engine.E2.P
            result_simu[incr_save, 7] = engine.E1.T
            result_simu[incr_save, 10] = engine.Fm.N
            incr_save = incr_save +1
            '''
    '''
    plt.figure(1)
    plt.subplot(331)
    plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 1],'r')
    plt.ylabel('Engine.Em.Tq')

    plt.subplot(332)
    plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'r', result_simu[0:incr_save, 0],result_simu[0:incr_save, 3],'g')
    plt.ylabel('Engine Massic Flow [kg/s]')

    plt.subplot(333)
    plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 4],'r')
    plt.ylabel('Engine.FAR')

    plt.subplot(334)
    plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 5],'r', result_simu[0:incr_save, 0],result_simu[0:incr_save, 6],'g')
    plt.ylabel('Engine Pressure [Pa]')

    plt.subplot(335)
    plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 7],'r')
    plt.ylabel('Engine Temperature [k]')

    plt.subplot(337)
    plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 10],'r')
    plt.ylabel('Engine.Fm.N')

    plt.show()
    '''
sc.disconnect()  
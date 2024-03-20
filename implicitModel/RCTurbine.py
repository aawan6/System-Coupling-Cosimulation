#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
Volume Turbine

Inputs:
    - F1
    - F2
Outputs:
    - E1
    - E2

Turbine

Inputs:
    - E1
    - E2
Outputs:
    - F1
    - F2
"""
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

from Library_ThermoFluid_class import EffortSource, FlowSource, Volume_C, Turbine_TF
from Fluid_properties_class import FluidFuel
from EffortFlowPort_class import FlowM
import ModelSimple_init as config

result_simu = np.zeros((15, 11))
incr_save = 1

#initial values
t0 = 298
P0 = 1e5
T0 = 298
pAir = 1e5
tAir = 298
VNT = 0.7
Ffuel_Qm = 0 
far = Ffuel_Qm * config.ks #/ self.Qm

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "RC Turbine"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    # volume Turbine 
    
    sc.addInputParameter(sysc.Parameter("F1FAR")) 
    sc.addInputParameter(sysc.Parameter("F1Qm"))
    sc.addInputParameter(sysc.Parameter("F1Qmh"))

    sc.addOutputParameter(sysc.Parameter("E1h"))
    sc.addOutputParameter(sysc.Parameter("E1P"))
    sc.addOutputParameter(sysc.Parameter("E1T"))

    # Turbine
    sc.addInputParameter(sysc.Parameter("E2h"))
    sc.addInputParameter(sysc.Parameter("E2P"))
    sc.addInputParameter(sysc.Parameter("E2T"))
    sc.addInputParameter(sysc.Parameter("Fmomega"))
    sc.addInputParameter(sysc.Parameter("FmN"))
    sc.addInputParameter(sysc.Parameter("PI_VNTy"))

    sc.addOutputParameter(sysc.Parameter("F2FAR"))
    sc.addOutputParameter(sysc.Parameter("F2Qm"))
    sc.addOutputParameter(sysc.Parameter("F2Qmh"))
    sc.addOutputParameter(sysc.Parameter("EmTq"))
    
    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
    #sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
else:
    # solve mode

    # initialize system
    Flow_init1 = FlowSource(0, t0)
    Flow_init2 = FlowSource(0, t0)
    fuel = FluidFuel(config.ks, config.lhv, config.hv, config.nc, config.nh)
    volumeTurbine = Volume_C(Flow_init1.F, Flow_init2.F, P0, T0, fuel.nC, fuel.nH, far)
    volumeTurbine.Param(config.vol_om + config.vol_turbine)

    ambientAir1 = EffortSource(pAir, tAir)
    ambientAir2 = EffortSource(pAir, tAir)
    turbine = Turbine_TF(ambientAir1.E, ambientAir2.E, FlowM(config.Nturbo / 30 * math.pi), VNT, fuel.nC, fuel.nH, far)
    turbine.Param(config.preft, config.treft, config.x_pr, config.y_vntposition, config.z_flowt_cor, config.z_eta_turb*1.12)

    sc.setParameterValue("E1h", volumeTurbine.E1.h)
    sc.setParameterValue("E1P", volumeTurbine.E1.P)
    sc.setParameterValue("E1T", volumeTurbine.E1.T)

    sc.setParameterValue("F2FAR", turbine.FAR)
    sc.setParameterValue("F2Qm", turbine.F2.Qm)
    sc.setParameterValue("F2Qmh", turbine.F2.Qmh)
    sc.setParameterValue("EmTq", turbine.Em.Tq)
    i = 1
    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        startTime = sc.getCurrentTimeStep().startTime
        tsSize = sc.getCurrentTimeStep().timeStepSize
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")
            
            
            print(i)
            i +=1
          

            """print(f"turbine.E1.gamma: {turbine.E1.gamma}")
            print(f"turbine.E1.h: {turbine.E1.h}")
            print(f"turbine.E1.P: {turbine.E1.P}")
            print(f"turbine.E1.T: {turbine.E1.T}")
            print(f"turbine.E2.h: {turbine.E2.h}")
            print(f"turbine.E2.P: {turbine.E2.P}")
            print(f"turbine.E2.T: {turbine.E2.T}")
            print(f"turbine.FAR: {turbine.FAR}")
            print(f"volumeTurbine.FAR: {volumeTurbine.FAR}")
            print(f"volumeTurbine.F1.Qm: {volumeTurbine.F1.Qm}")
            print(f"volumeTurbine.F1.Qmh: {volumeTurbine.F1.Qmh}")
            print(f"volumeTurbine.F2.Qm: {volumeTurbine.F2.Qm}")
            print(f"volumeTurbine.F2.Qmh: {volumeTurbine.F2.Qmh}")
            print()"""

            sc.updateInputs()
            volumeTurbine.F1.Qm = sc.getParameterValue("F1Qm")
            volumeTurbine.F1.Qmh = sc.getParameterValue("F1Qmh")

            
            volumeTurbine.F2.Qm = turbine.F1.Qm
            volumeTurbine.F2.Qmh = turbine.F1.Qmh

            volumeTurbine.FAR = sc.getParameterValue("F1FAR")
            volumeTurbine.Solve(sc.getCurrentTimeStep().timeStepSize, 'Trapezoidal')

            turbine.E1.gamma = volumeTurbine.E2.gamma
            turbine.E1.h = volumeTurbine.E2.h
            turbine.E1.P = volumeTurbine.E2.P
            turbine.E1.T = volumeTurbine.E2.T
            
            turbine.E2.h = sc.getParameterValue("E2h")
            turbine.E2.P = sc.getParameterValue("E2P")
            turbine.E2.T = sc.getParameterValue("E2T")
            turbine.FAR = sc.getParameterValue("F1FAR")
            turbine.Fm.omega = sc.getParameterValue("Fmomega")
            turbine.Fm.N = sc.getParameterValue("FmN")
            turbine.VNT = sc.getParameterValue("PI_VNTy")
            
            turbine.Solve()

            sc.setParameterValue("E1h", volumeTurbine.E1.h)
            sc.setParameterValue("E1P", volumeTurbine.E1.P)
            sc.setParameterValue("E1T", volumeTurbine.E1.T)

            sc.setParameterValue("F2FAR", turbine.FAR)
            sc.setParameterValue("F2Qm", turbine.F2.Qm)
            sc.setParameterValue("F2Qmh", turbine.F2.Qmh)
            sc.setParameterValue("EmTq", turbine.Em.Tq)

            sc.updateOutputs(sysc.Converged)
            multiIteration = True

            result_simu[incr_save, 8] = turbine.E1.T
            result_simu[incr_save, 9] = turbine.E2.T
            incr_save = incr_save +1

    print()   
    print("[" + ", ".join(map(str, [row[8] for row in result_simu])) + "]")
    print("[" + ", ".join(map(str, [row[9] for row in result_simu])) + "]")
    print()

    '''plt.figure(1)

    plt.subplot(336)
    plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 8],'r', result_simu[0:incr_save, 0],result_simu[0:incr_save, 9],'g')
    plt.ylabel('Turbine Temperature [k]')

    plt.show()'''

sc.disconnect()
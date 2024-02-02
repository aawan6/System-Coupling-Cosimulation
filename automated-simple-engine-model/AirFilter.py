#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
Air Filter

Inputs:
    - E1
    - E2
Outputs:
    - F1Qm
    - F1Qmh
    - F2Qm
    - F2Qmh

"""

import argparse
import os
import sys
#import matplotlib.pyplot as plt
#import numpy as np

if sys.platform.startswith("win"):
    for p in os.environ["PYTHON_DLL_PATH"].split(os.pathsep):
        try:
            os.add_dll_directory(p)
        except (FileNotFoundError, OSError):
            pass  # skip any paths that don't exist

from pyExt import SystemCouplingParticipant as sysc

from Library_ThermoFluid_class import EffortSource, PressureLosses_R

#result_simu = np.zeros((7, 3))
#incr_save = 1

# initial values
pAir = 1e5
tAir = 298
k_pl_af = 0.002

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "Air Filter"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    sc.addInputParameter(sysc.Parameter("E2h"))
    sc.addInputParameter(sysc.Parameter("E2P"))
    sc.addInputParameter(sysc.Parameter("E2R"))
    sc.addInputParameter(sysc.Parameter("E2T"))

    sc.addOutputParameter(sysc.Parameter("F1Qm"))
    sc.addOutputParameter(sysc.Parameter("F1Qmh"))
    sc.addOutputParameter(sysc.Parameter("F2Qm"))
    sc.addOutputParameter(sysc.Parameter("F2Qmh"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
else:
    # solve mode

    # initialize system
    ambientAir1 = EffortSource(pAir, tAir)
    ambientAir2 = EffortSource(pAir, tAir)
    airFilter = PressureLosses_R(ambientAir1.E, ambientAir2.E)
    airFilter.Param(k_pl_af)

    sc.setParameterValue("F1Qm", airFilter.F1.Qm)
    sc.setParameterValue("F1Qmh", airFilter.F1.Qmh)
    sc.setParameterValue("F2Qm", airFilter.F2.Qm)
    sc.setParameterValue("F2Qmh", airFilter.F2.Qmh)

    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        startTime = sc.getCurrentTimeStep().startTime
        tsSize = sc.getCurrentTimeStep().timeStepSize
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")
            
            #result_simu[incr_save, 0] = startTime + tsSize
            #result_simu[incr_save, 1] = pAir
            #result_simu[incr_save, 2] = airFilter.E2.P
            #incr_save = incr_save +1

            sc.updateInputs()
            airFilter.E2.h = sc.getParameterValue("E2h")
            airFilter.E2.P = sc.getParameterValue("E2P")
            airFilter.E2.R = sc.getParameterValue("E2R")
            airFilter.E2.T = sc.getParameterValue("E2T")

            airFilter.Solve()

            sc.setParameterValue("F1Qm", airFilter.F1.Qm)
            sc.setParameterValue("F1Qmh", airFilter.F1.Qmh)
            sc.setParameterValue("F2Qm", airFilter.F2.Qm)
            sc.setParameterValue("F2Qmh", airFilter.F2.Qmh)
            sc.updateOutputs(sysc.Converged)
            multiIteration = True

    #plt.figure(1)
    #plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 1],'r',result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'b')
    #plt.xlabel('time [s]')
    #plt.ylabel('Air Filter Pressure [Pa]')
    #plt.show()

sc.disconnect()

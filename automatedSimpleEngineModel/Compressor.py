#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
Compressor

Inputs:
    - E1gamma
    - E1h
    - E1P
    - E1T
    - E2P
Outputs:
    - F1Qm
    - F1Qmh
    - F2Qm
    - F2Qmh
    - E2T

"""

import argparse
import math
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

parameters = {}

if sys.platform.startswith("win"):
    for p in os.environ["PYTHON_DLL_PATH"].split(os.pathsep):
        try:
            os.add_dll_directory(p)
        except (FileNotFoundError, OSError):
            pass  # skip any paths that don't exist

from pyExt import SystemCouplingParticipant as sysc

from Data_treatment import interpolv
from Library_ThermoFluid_class import Compressor_Tf, EffortSource
from EffortFlowPort_class import FlowM
import ModelSimple_init as config

#Creation of vectors for saving / plots
result_simu = np.zeros((12, 12))
incr_save = 1

# initial values
pAir = 1e5
tAir = 298
nTurbo = 120000

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "Compressor"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    sc.addInputParameter(sysc.Parameter("E1gamma"))
    sc.addInputParameter(sysc.Parameter("E1h"))
    sc.addInputParameter(sysc.Parameter("E1P"))
    sc.addInputParameter(sysc.Parameter("E1T"))
    sc.addInputParameter(sysc.Parameter("E2P"))
    sc.addInputParameter(sysc.Parameter("E2T"))
    sc.addInputParameter(sysc.Parameter("E2h"))

    sc.addOutputParameter(sysc.Parameter("F1Qm"))
    sc.addOutputParameter(sysc.Parameter("F1Qmh"))
    sc.addOutputParameter(sysc.Parameter("F2Qm"))
    sc.addOutputParameter(sysc.Parameter("F2Qmh"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
    #sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
else:
    # solve mode

    # initialize system
    ambientAir1 = EffortSource(pAir, tAir)
    ambientAir2 = EffortSource(pAir, tAir)
    compressor = Compressor_Tf(ambientAir1.E, ambientAir2.E, FlowM(nTurbo / 30 * math.pi))
    compressor.Param(
        config.Prefc,
        config.Trefc,
        config.x_NC,
        config.surge_PR,
        config.y_margin,
        config.z_flow_cor,
        config.z_eta_Comp,
    )

    sc.setParameterValue("F1Qm", compressor.F1.Qm)
    sc.setParameterValue("F1Qmh", compressor.F1.Qmh)
    sc.setParameterValue("F2Qm", compressor.F2.Qm)
    sc.setParameterValue("F2Qmh", compressor.F2.Qmh)

    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        startTime = sc.getCurrentTimeStep().startTime
        tsSize = sc.getCurrentTimeStep().timeStepSize
        n = interpolv(
            [0, 5, 5.01, 10.5, 10.51, 15],
            [120000, 120000, 150000, 150000, 130000, 130000],
            startTime + tsSize,
        )
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations") 

            sc.updateInputs()
            compressor.E1.h = sc.getParameterValue("E1h")
            compressor.E1.P = sc.getParameterValue("E1P")
            compressor.E1.T = sc.getParameterValue("E1T")
            compressor.E2.P = sc.getParameterValue("E2P")
            compressor.E2.T = sc.getParameterValue("E2T")
            compressor.E2.h = sc.getParameterValue("E2h") 

            compressor.Fm = FlowM(n / 30 * math.pi)
            compressor.Solve()

            sc.setParameterValue("F1Qm", compressor.F1.Qm)
            sc.setParameterValue("F1Qmh", compressor.F1.Qmh)
            sc.setParameterValue("F2Qm", compressor.F2.Qm)
            sc.setParameterValue("F2Qmh", compressor.F2.Qmh)
            sc.updateOutputs(sysc.Converged)
            multiIteration = True
             
            result_simu[incr_save, 0] = startTime + tsSize
            result_simu[incr_save, 2] = compressor.E1.P
            result_simu[incr_save, 3] = compressor.E2.P
            result_simu[incr_save, 4] = compressor.E1.T
            result_simu[incr_save, 5] = compressor.E2.T
            result_simu[incr_save, 7] = compressor.F2.Qm
            incr_save = incr_save +1     

    print(f"result_simu[incr_save, 0]: {result_simu[:, 0]}")
    print(f"result_simu[incr_save, 2]: {result_simu[:, 2]}")
    print(f"result_simu[incr_save, 3]: {result_simu[:, 3]}")
    print(f"result_simu[incr_save, 4]: {result_simu[:, 4]}")
    print(f"result_simu[incr_save, 5]: {result_simu[:, 5]}")
    print(f"result_simu[incr_save, 7]: {result_simu[:, 7]}")
    #plt.figure(1)
    #plt.subplot(221)
    #plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'r',result_simu[0:incr_save, 0],result_simu[0:incr_save, 3],'g')
    #plt.ylabel('Compressor Pressure [Pa]')
    #plt.subplot(222)
    #plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 4],'b',result_simu[0:incr_save, 0],result_simu[0:incr_save, 5],'r')
    #plt.ylabel('Compressor Temperature [K]')
    #plt.subplot(223)
    #plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 6])
    #plt.xlabel('time [s]')
    #plt.ylabel('Massic Flow [kg/s]')
    #plt.show()

sc.disconnect()
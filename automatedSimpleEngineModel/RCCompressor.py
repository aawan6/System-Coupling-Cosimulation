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

Volume Compressor

Inputs:
  - F1Qm
  - F1Qmh
Outputs:
  - E1
"""

import argparse
import math
import os
import sys

parameters = {}

if sys.platform.startswith("win"):
    for p in os.environ["PYTHON_DLL_PATH"].split(os.pathsep):
        try:
            os.add_dll_directory(p)
        except (FileNotFoundError, OSError):
            pass  # skip any paths that don't exist

from pyExt import SystemCouplingParticipant as sysc

from Library_ThermoFluid_class import FlowSource, Volume_C, Compressor_Tf, EffortSource
from Data_treatment import interpolv
from EffortFlowPort_class import FlowM
import ModelSimple_init as config

# initial values
pAir = 1e5
tAir = 298
nTurbo = 120000
t0 = 293
volCompressor = 20e-3

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "RC Compressor"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    #compressor
    sc.addInputParameter(sysc.Parameter("E1gamma"))
    sc.addInputParameter(sysc.Parameter("E1h"))
    sc.addInputParameter(sysc.Parameter("E1P"))
    sc.addInputParameter(sysc.Parameter("E1T"))

    sc.addOutputParameter(sysc.Parameter("F1Qm"))
    sc.addOutputParameter(sysc.Parameter("F1Qmh"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
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

    flowInit1 = FlowSource(0, t0)
    flowInit2 = FlowSource(0, t0)
    volC = Volume_C(flowInit1.F, flowInit2.F)
    volC.Param(volCompressor)

    #compressor
    sc.setParameterValue("F1Qm", compressor.F1.Qm)
    sc.setParameterValue("F1Qmh", compressor.F1.Qmh)
    
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

            compressor.E2.P = volC.E1.P
            compressor.E2.T = volC.E1.T
            compressor.E2.h = volC.E1.h 

            volC.F1.Qm = compressor.F2.Qm
            volC.F1.Qmh = compressor.F2.Qmh
            volC.F2 = FlowSource(-0.1, volC.E1.T)
            
            sc.updateInputs()
            compressor.E1.h = sc.getParameterValue("E1h")
            compressor.E1.P = sc.getParameterValue("E1P")
            compressor.E1.T = sc.getParameterValue("E1T") 

            compressor.Fm = FlowM(n / 30 * math.pi)
            compressor.Solve()
            volC.Solve(sc.getCurrentTimeStep().timeStepSize)
            
            sc.setParameterValue("F1Qm", compressor.F1.Qm)
            sc.setParameterValue("F1Qmh", compressor.F1.Qmh)

            sc.updateOutputs(sysc.Converged)
            multiIteration = True

sc.disconnect()   
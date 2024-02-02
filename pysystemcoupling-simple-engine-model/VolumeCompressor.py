#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
Volume Compressor

Inputs:
  - F1Qm
  - F1Qmh
Outputs:
  - E1
"""

import argparse
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

from Library_ThermoFluid_class import FlowSource, Volume_C

# initial values
t0 = 293
volCompressor = 20e-3

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "Volume Compressor"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    sc.addInputParameter(sysc.Parameter("F1Qm"))
    sc.addInputParameter(sysc.Parameter("F1Qmh"))

    sc.addOutputParameter(sysc.Parameter("E1P"))
    sc.addOutputParameter(sysc.Parameter("E1T"))
    sc.addOutputParameter(sysc.Parameter("E1h"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
else:
    # solve mode

    # initialize system
    flowInit1 = FlowSource(0, t0)
    flowInit2 = FlowSource(0, t0)
    volC = Volume_C(flowInit1.F, flowInit2.F)
    volC.Param(volCompressor)

    sc.setParameterValue("E1P", volC.E1.P)
    sc.setParameterValue("E1T", volC.E1.T)
    sc.setParameterValue("E1h", volC.E1.h)

    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")

            sc.updateInputs()
            volC.F1.Qm = sc.getParameterValue("F1Qm") 
            volC.F1.Qmh = sc.getParameterValue("F1Qmh")
            volC.F2 = FlowSource(-0.1, volC.E1.T)
            volC.Solve(sc.getCurrentTimeStep().timeStepSize)

            sc.setParameterValue("E1P", volC.E1.P)
            sc.setParameterValue("E1T", volC.E1.T)
            sc.setParameterValue("E1h", volC.E1.h)
            sc.updateOutputs(sysc.Converged)
            multiIteration = True

sc.disconnect()

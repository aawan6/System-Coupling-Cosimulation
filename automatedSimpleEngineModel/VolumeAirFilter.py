#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
Volume Air Filter

Inputs:
    - F1Qm
    - F1Qmh
    - F2Qm
    - F2Qmh
Outputs:
    - E1h
    - E1P
    - E1R
    - E1T
    - E2gamma
    - E2h
    - E2P
    - E2T

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
volAf = 30e-3

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "Volume Air Filter"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    sc.addInputParameter(sysc.Parameter("F1Qm"))
    sc.addInputParameter(sysc.Parameter("F1Qmh"))
    sc.addInputParameter(sysc.Parameter("F2Qm"))
    sc.addInputParameter(sysc.Parameter("F2Qmh"))

    sc.addOutputParameter(sysc.Parameter("E1h"))
    sc.addOutputParameter(sysc.Parameter("E1P"))
    sc.addOutputParameter(sysc.Parameter("E1R"))
    sc.addOutputParameter(sysc.Parameter("E1T"))
    sc.addOutputParameter(sysc.Parameter("E2gamma"))
    sc.addOutputParameter(sysc.Parameter("E2h"))
    sc.addOutputParameter(sysc.Parameter("E2P"))
    sc.addOutputParameter(sysc.Parameter("E2T"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
    #sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
else:
    # solve mode

    # initialize system
    flowInit1 = FlowSource(0, t0)
    flowInit2 = FlowSource(0, t0)
    volC = Volume_C(flowInit1.F, flowInit2.F)
    volC.Param(volAf)

    sc.setParameterValue("E1h", volC.E1.h)
    sc.setParameterValue("E1P", volC.E1.P)
    sc.setParameterValue("E1R", volC.E1.R)
    sc.setParameterValue("E1T", volC.E1.T)
    sc.setParameterValue("E2gamma", volC.E2.gamma)
    sc.setParameterValue("E2h", volC.E2.h)
    sc.setParameterValue("E2P", volC.E2.P)
    sc.setParameterValue("E2T", volC.E2.T)

    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")
            
            sc.updateInputs()
            volC.F1.Qm = sc.getParameterValue("F1Qm")
            volC.F1.Qmh = sc.getParameterValue("F1Qmh")
            volC.F2.Qm = sc.getParameterValue("F2Qm")
            volC.F2.Qmh = sc.getParameterValue("F2Qmh")

            volC.Solve(sc.getCurrentTimeStep().timeStepSize)

            sc.setParameterValue("E1h", volC.E1.h)
            sc.setParameterValue("E1P", volC.E1.P)
            sc.setParameterValue("E1R", volC.E1.R)
            sc.setParameterValue("E1T", volC.E1.T)
            sc.setParameterValue("E2gamma", volC.E2.gamma)
            sc.setParameterValue("E2h", volC.E2.h)
            sc.setParameterValue("E2P", volC.E2.P)
            sc.setParameterValue("E2T", volC.E2.T)
            sc.updateOutputs(sysc.Converged)
            multiIteration = True

sc.disconnect()

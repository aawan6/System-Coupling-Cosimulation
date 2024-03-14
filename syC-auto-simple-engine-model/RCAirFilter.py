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

if sys.platform.startswith("win"):
    for p in os.environ["PYTHON_DLL_PATH"].split(os.pathsep):
        try:
            os.add_dll_directory(p)
        except (FileNotFoundError, OSError):
            pass  # skip any paths that don't exist

from pyExt import SystemCouplingParticipant as sysc

from Library_ThermoFluid_class import EffortSource, PressureLosses_R, FlowSource, Volume_C
# initial values
pAir = 1e5
tAir = 298
k_pl_af = 0.002
t0 = 293
volAf = 30e-3

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "RC Air Filter"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    #volume Air Filter
    sc.addInputParameter(sysc.Parameter("F2Qm"))
    sc.addInputParameter(sysc.Parameter("F2Qmh"))

    sc.addOutputParameter(sysc.Parameter("E2gamma"))
    sc.addOutputParameter(sysc.Parameter("E2h"))
    sc.addOutputParameter(sysc.Parameter("E2P"))
    sc.addOutputParameter(sysc.Parameter("E2T"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
else:
    # solve mode

    # initialize system
    flowInit1 = FlowSource(0, t0)
    flowInit2 = FlowSource(0, t0)
    volAirFilter = Volume_C(flowInit1.F, flowInit2.F)
    volAirFilter.Param(volAf)

    ambientAir1 = EffortSource(pAir, tAir)
    ambientAir2 = EffortSource(pAir, tAir)
    airFilter = PressureLosses_R(ambientAir1.E, ambientAir2.E)
    airFilter.Param(k_pl_af)

    sc.setParameterValue("E2gamma", volAirFilter.E2.gamma)
    sc.setParameterValue("E2h", volAirFilter.E2.h)
    sc.setParameterValue("E2P", volAirFilter.E2.P)
    sc.setParameterValue("E2T", volAirFilter.E2.T)

    sc.initializeAnalysis()
    while sc.doTimeStep():

        airFilter.E2.h = volAirFilter.E1.h
        airFilter.E2.P = volAirFilter.E1.P
        airFilter.E2.R = volAirFilter.E1.R
        airFilter.E2.T = volAirFilter.E1.T

        volAirFilter.F1.Qm = airFilter.F2.Qm
        volAirFilter.F1.Qmh = airFilter.F2.Qmh

        sc.updateInputs()

        volAirFilter.F2.Qm = sc.getParameterValue("F2Qm")
        volAirFilter.F2.Qmh = sc.getParameterValue("F2Qmh")

        volAirFilter.Solve(sc.getCurrentTimeStep().timeStepSize)
        airFilter.Solve()

        sc.setParameterValue("E2gamma", volAirFilter.E2.gamma)
        sc.setParameterValue("E2h", volAirFilter.E2.h)
        sc.setParameterValue("E2P", volAirFilter.E2.P)
        sc.setParameterValue("E2T", volAirFilter.E2.T)

        sc.updateOutputs(sysc.Converged)

sc.disconnect()
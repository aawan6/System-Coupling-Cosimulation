#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
Volume Exhaust

Inputs:
    - F1
    - F2
Outputs:
    - E1
    - E2

Exhaust

Inputs:
    - E1
Outputs:
    - F1

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
from Fluid_properties_class import FluidFuel
import ModelSimple_init as config

# initial values
t0 = 293
P0 = 1e5
T0 = 298
pAir = 1e5
tAir = 298
Ffuel_Qm = 0 
far = Ffuel_Qm * config.ks #/ self.Qm

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "RC Exhaust"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    
    # setup mode
    # volume exhaust
    sc.addInputParameter(sysc.Parameter("FAR"))
    sc.addInputParameter(sysc.Parameter("F1Qm"))
    sc.addInputParameter(sysc.Parameter("F1Qmh"))

    sc.addOutputParameter(sysc.Parameter("E1h"))
    sc.addOutputParameter(sysc.Parameter("E1P"))
    sc.addOutputParameter(sysc.Parameter("E1T"))
    
    sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
else:
    # solve mode

    # initialize system
    flowInit1 = FlowSource(0, t0)
    flowInit2 = FlowSource(0, t0)
    fuel = FluidFuel(config.ks, config.lhv, config.hv, config.nc, config.nh)
    volumeExhaust = Volume_C(flowInit1.F, flowInit2.F, P0, T0, fuel.nC, fuel.nH, far)
    volumeExhaust.Param(config.vol_ex)

    ambientAir1 = EffortSource(pAir, tAir)
    ambientAir2 = EffortSource(pAir, tAir)
    exhaust = PressureLosses_R(ambientAir1.E, ambientAir2.E)
    exhaust.Param(config.k_pl_exhaust)

    sc.setParameterValue("E1h", volumeExhaust.E1.h)
    sc.setParameterValue("E1P", volumeExhaust.E1.P)
    sc.setParameterValue("E1T", volumeExhaust.E1.T)

    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")

            exhaust.E1.h = volumeExhaust.E2.h
            exhaust.E1.P = volumeExhaust.E2.P
            exhaust.E1.T = volumeExhaust.E2.T
            exhaust.E1.R = volumeExhaust.E2.R

            volumeExhaust.F2.Qm = exhaust.F1.Qm 
            volumeExhaust.F2.Qmh = exhaust.F1.Qmh

            sc.updateInputs()
            volumeExhaust.FAR = sc.getParameterValue("FAR")
            volumeExhaust.F1.Qm = sc.getParameterValue("F1Qm")
            volumeExhaust.F1.Qmh = sc.getParameterValue("F1Qmh")

            volumeExhaust.Solve(sc.getCurrentTimeStep().timeStepSize)
            exhaust.Solve()

            sc.setParameterValue("E1h", volumeExhaust.E1.h)
            sc.setParameterValue("E1P", volumeExhaust.E1.P)
            sc.setParameterValue("E1T", volumeExhaust.E1.T)

            sc.updateOutputs(sysc.Converged)
            multiIteration = True

sc.disconnect()
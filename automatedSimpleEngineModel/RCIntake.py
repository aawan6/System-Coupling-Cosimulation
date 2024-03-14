#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
Intake

Inputs:
    - E1
    - E2
Outputs:
    - F1
    - F2

Volume intake

Inputs:
    - F1
    - F2
Outputs:
    - E1
    - E2
"""
print("RCIntake.py")
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
import ModelSimple_init as config

#initial values
pAir = 1e5
tAir = 298
t0 = 298
k_pl_intake = 0.001177355219365358 #0.0016352643389866259

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "RC Intake"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    # intake    
    sc.addInputParameter(sysc.Parameter("E1h"))
    sc.addInputParameter(sysc.Parameter("E1P"))
    sc.addInputParameter(sysc.Parameter("E1T"))
    sc.addInputParameter(sysc.Parameter("E1R"))

    sc.addOutputParameter(sysc.Parameter("F1Qm"))
    sc.addOutputParameter(sysc.Parameter("F1Qmh"))

    # volume intake
    sc.addInputParameter(sysc.Parameter("F2Qm"))
    sc.addInputParameter(sysc.Parameter("F2Qmh"))

    sc.addOutputParameter(sysc.Parameter("E2h"))
    sc.addOutputParameter(sysc.Parameter("E2P"))
    sc.addOutputParameter(sysc.Parameter("E2T"))
    sc.addOutputParameter(sysc.Parameter("E2R"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
    #sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))

else:
    # solve mode

    # initialize system
    ambientAir1 = EffortSource(pAir, tAir)
    ambientAir2 = EffortSource(pAir, tAir)
    intake = PressureLosses_R(ambientAir1.E, ambientAir2.E)
    intake.Param(k_pl_intake)

    Flow_init1 = FlowSource(0, t0)
    Flow_init2 = FlowSource(0, t0)
    volumeIntake = Volume_C(Flow_init1.F, Flow_init2.F)
    volumeIntake.Param(config.vol_intake + config.vol_ic)

    sc.setParameterValue("F1Qm", intake.F1.Qm)
    sc.setParameterValue("F1Qmh", intake.F1.Qmh)

    sc.setParameterValue("E2h", volumeIntake.E2.h)
    sc.setParameterValue("E2P", volumeIntake.E2.P)
    sc.setParameterValue("E2T", volumeIntake.E2.T)
    sc.setParameterValue("E2R", volumeIntake.E2.R)
    i = 1
    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")
            print(i)
            i +=1
            print(f"intake.E1.h: {intake.E1.h}")
            print(f"intake.E1.P: {intake.E1.P}")
            print(f"intake.E1.T: {intake.E1.T}")
            print(f"intake.E1.R: {intake.E1.R}")
            print(f"intake.E2.h: {intake.E2.h}")
            print(f"intake.E2.P: {intake.E2.P}")
            print(f"intake.E2.T: {intake.E2.T}")
            print(f"intake.E2.R: {intake.E2.R}")
            print(f"volumeIntake.F1.Qm: {volumeIntake.F1.Qm}")
            print(f"volumeIntake.F1.Qmh: {volumeIntake.F1.Qmh}")
            print(f"volumeIntake.F2.Qm: {volumeIntake.F2.Qm}")
            print(f"volumeIntake.F2.Qmh: {volumeIntake.F2.Qmh}")
            print()

            sc.updateInputs()
            intake.E1.h = sc.getParameterValue("E1h")
            intake.E1.P = sc.getParameterValue("E1P")
            intake.E1.T = sc.getParameterValue("E1T")
            intake.E1.R = sc.getParameterValue("E1R")

            intake.E2.h = volumeIntake.E1.h
            intake.E2.P = volumeIntake.E1.P
            intake.E2.T = volumeIntake.E1.T
            intake.E2.R = volumeIntake.E1.R

            intake.Solve()

            volumeIntake.F1.Qm = intake.F2.Qm
            volumeIntake.F1.Qmh = intake.F2.Qmh

            volumeIntake.F2.Qm = sc.getParameterValue("F2Qm")
            volumeIntake.F2.Qmh = sc.getParameterValue("F2Qmh")

            volumeIntake.Solve(sc.getCurrentTimeStep().timeStepSize, 'Trapezoidal')

            sc.setParameterValue("F1Qm", intake.F1.Qm)
            sc.setParameterValue("F1Qmh", intake.F1.Qmh)

            sc.setParameterValue("E2h", volumeIntake.E2.h)
            sc.setParameterValue("E2P", volumeIntake.E2.P)
            sc.setParameterValue("E2T", volumeIntake.E2.T)
            sc.setParameterValue("E2R", volumeIntake.E2.R)

            """ intake.E2.h = volumeIntake.E1.h
            intake.E2.P = volumeIntake.E1.P
            intake.E2.T = volumeIntake.E1.T
            intake.E2.R = volumeIntake.E1.R

            volumeIntake.F1.Qm = intake.F2.Qm
            volumeIntake.F1.Qmh = intake.F2.Qmh

            sc.updateInputs()
            intake.E1.h = sc.getParameterValue("E1h")
            intake.E1.P = sc.getParameterValue("E1P")
            intake.E1.T = sc.getParameterValue("E1T")
            intake.E1.R = sc.getParameterValue("E1R")

            volumeIntake.F2.Qm = sc.getParameterValue("F2Qm")
            volumeIntake.F2.Qmh = sc.getParameterValue("F2Qmh")

            intake.Solve()
            volumeIntake.Solve(sc.getCurrentTimeStep().timeStepSize)

            sc.setParameterValue("F1Qm", intake.F1.Qmh)
            sc.setParameterValue("F1Qmh", intake.F1.Qmh)

            sc.setParameterValue("E2h", volumeIntake.E2.h)
            sc.setParameterValue("E2P", volumeIntake.E2.P)
            sc.setParameterValue("E2T", volumeIntake.E2.T)
            sc.setParameterValue("E2R", volumeIntake.E2.R)"""

            sc.updateOutputs(sysc.Converged)
            multiIteration = True

sc.disconnect()
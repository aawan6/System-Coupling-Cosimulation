#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
TurboShaft

Inputs:
    - Em1
    - Em2
Outputs:
    - Fm1
    - Fm2

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

from Library_Mechanics_class import Shaft_I
from EffortFlowPort_class import EffortM
import ModelSimple_init as config

result_simu = np.zeros((6, 15))
incr_save = 1

#initial values

parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "TurboShaft"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    
    sc.addInputParameter(sysc.Parameter("Em1Tq"))
    sc.addInputParameter(sysc.Parameter("Em2Tq"))

    sc.addOutputParameter(sysc.Parameter("Fm1omega"))
    sc.addOutputParameter(sysc.Parameter("Fm1N"))
    sc.addOutputParameter(sysc.Parameter("Fm2omega"))
    sc.addOutputParameter(sysc.Parameter("Fm2N"))
    
    sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
    

else:
    # solve mode
    
    # initialize system
    turboShaft = Shaft_I(EffortM(0), EffortM(0), config.Nturbo / 30 * math.pi)
    turboShaft.Param(config.compr_inertia +config.turbine_inertia, 1000)

    sc.setParameterValue("Fm1omega", turboShaft.Fm1.omega)
    sc.setParameterValue("Fm1N", turboShaft.Fm1.N)
    sc.setParameterValue("Fm2omega", turboShaft.Fm2.omega)
    sc.setParameterValue("Fm2N", turboShaft.Fm2.N)

    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False
        startTime = sc.getCurrentTimeStep().startTime
        tsSize = sc.getCurrentTimeStep().timeStepSize
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")
            
            result_simu[incr_save, 0] = startTime + tsSize
            result_simu[incr_save, 11] = turboShaft.Fm1.N

            sc.updateInputs()
            turboShaft.Em1.Tq = sc.getParameterValue("Em1Tq")
            turboShaft.Em2.Tq = sc.getParameterValue("Em2Tq")

            turboShaft.Solve(sc.getCurrentTimeStep().timeStepSize)

            sc.setParameterValue("Fm1omega", turboShaft.Fm1.omega)
            sc.setParameterValue("Fm1N", turboShaft.Fm1.N)
            sc.setParameterValue("Fm2omega", turboShaft.Fm2.omega)
            sc.setParameterValue("Fm2N", turboShaft.Fm2.N)

            sc.updateOutputs(sysc.Converged)
            multiIteration = True

sc.disconnect()  
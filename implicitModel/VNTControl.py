#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

"""
VNT Control

Inputs:
    - F1
    - F2
Outputs:
    - E1
    - E2

"""
import argparse
import os
import sys
import numpy as np

if sys.platform.startswith("win"):
    for p in os.environ["PYTHON_DLL_PATH"].split(os.pathsep):
        try:
            os.add_dll_directory(p)
        except (FileNotFoundError, OSError):
            pass  # skip any paths that don't exist

from pyExt import SystemCouplingParticipant as sysc

from Library_Control_class import PI_control
from Data_treatment import interpolv, interpolm
import ModelSimple_init as config

result_simu = np.zeros((15, 15))
incr_save = 1

# initial values
P0 = 1e5
Eninge_E1P = P0
print(f"engine.E1.P: {Eninge_E1P}")
parser = argparse.ArgumentParser()
parser.add_argument("--schost", type=str, default="")
parser.add_argument("--scport", type=int, default=0)
parser.add_argument("--scname", type=str, default="")
parser.add_argument("--scsetup", default=False, action="store_true")

""" Parse input arguments. """
args = parser.parse_args()

buildInfo = "VNT Control"

sc = sysc.SystemCoupling(args.schost, args.scport, args.scname, buildInfo)

if args.scsetup:
    # setup mode
    sc.addInputParameter(sysc.Parameter("x_Act"))

    sc.addOutputParameter(sysc.Parameter("PI_VNTy"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient))
    #sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
else:
    # solve mode
    # initialize system
    PI_VNT = PI_control(P0, P0)
    PI_VNT.Param(config.kp, config.ki, config.vnt_min, config.vnt_max)

    sc.setParameterValue("PI_VNTy", PI_VNT.y)
    i = 1
    sc.initializeAnalysis()
    while sc.doTimeStep():
        multiIteration = False

        startTime = sc.getCurrentTimeStep().startTime
        tsSize = sc.getCurrentTimeStep().timeStepSize
        n = interpolv([0.0, 5.0, 5.01, 7.5, 7.51, 10.0, 10.01, 15.0, 15.01, 20.0],
                      [2000.0, 2000.0, 2500.0, 2500.0, 3000.0, 3000.0, 3000.0, 3000.0, 3000.0, 3000.0], 
                      startTime + tsSize)
        pps = interpolv([0.0, 5.0, 5.01, 7.5, 7.51, 10.0, 10.01, 15.0, 15.01, 20.0],
                        [1.0, 1.0, 1.0, 1.0, 1.0, 0.7, 0.7, 1.0, 0.8, 0.8], 
                        startTime + tsSize)
        P1E_Ord = interpolm(config.y_pps_qinj, config.engine_x_ne, config.z_p1e_ord, pps, n)
        Kp_VNT = interpolv(config.x_epsilon_kp, config.y_kp, P1E_Ord - Eninge_E1P)
        while sc.doIteration():
            if multiIteration:
                raise RuntimeError("participant does not support multiple iterations")
            print(i)
            i +=1
            print(f"engine.E1.P / x_act: {Eninge_E1P}")
            print()

            PI_VNT.x_Ord = P1E_Ord

            sc.updateInputs()
            Eninge_E1P = sc.getParameterValue("x_Act")
            
            PI_VNT.x_Act = Eninge_E1P
            PI_VNT.Kp = Kp_VNT * 0.25

            PI_VNT.Solve(sc.getCurrentTimeStep().timeStepSize, 'Trapezoidal')

            sc.setParameterValue("PI_VNTy", PI_VNT.y)

            sc.updateOutputs(sysc.Converged)
            multiIteration = True

            result_simu[incr_save, 12] = PI_VNT.y
            result_simu[incr_save, 13] = PI_VNT.x_Ord
            incr_save += 1

    print()   
    print("[" + ", ".join(map(str, [row[12] for row in result_simu])) + "]")
    print("[" + ", ".join(map(str, [row[13] for row in result_simu])) + "]")
    print()

sc.disconnect()
    
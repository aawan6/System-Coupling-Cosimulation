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
    - Fmomega
    - FmN
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
import pandas as pd

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
import numpy as np

result_simu = np.zeros((1001, 11))
incr_save = 1

# initial values
pAir = 100000
tAir = 298
nTurbo = 120000
#t0 = 298 #simple engine model: 293
t0 = 293
#volCompressor = 0.004 #simple engine model: 20e-3
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
    sc.addInputParameter(sysc.Parameter("Fmomega"))
    sc.addInputParameter(sysc.Parameter("FmN"))

    sc.addOutputParameter(sysc.Parameter("F1Qm"))
    sc.addOutputParameter(sysc.Parameter("F1Qmh"))
    sc.addOutputParameter(sysc.Parameter("EmTq"))

    #volume compressor (added for intake connection)
    sc.addInputParameter(sysc.Parameter("F2Qm"))
    sc.addInputParameter(sysc.Parameter("F2Qmh"))

    sc.addOutputParameter(sysc.Parameter("E2h"))
    sc.addOutputParameter(sysc.Parameter("E2P"))
    sc.addOutputParameter(sysc.Parameter("E2T"))
    sc.addOutputParameter(sysc.Parameter("E2R"))

    sc.completeSetup(sysc.SetupInfo(sysc.Transient, False, sysc.Dimension_D3, sysc.TimeIntegration_Explicit))
    
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
    sc.setParameterValue("EmTq", compressor.Em.Tq)

    #volume compressor (added for intake connection)
    sc.setParameterValue("E2P", volC.E2.P)
    sc.setParameterValue("E2T", volC.E2.T)
    sc.setParameterValue("E2h", volC.E2.h)
    sc.setParameterValue("E2R", volC.E2.R)
    
    sc.initializeAnalysis() 
    i = 1
    simpleModel = False
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
            print(i)
            i +=1
            print(f"compressor.E2.P: {compressor.E2.P}")
            print(f"compressor.E2.T: {compressor.E2.T}")
            print(f"compressor.E2.h: {compressor.E2.h}")
            print(f"volC.F1.Qm: {volC.F1.Qm}")
            print(f"volC.F1.Qmh: {volC.F1.Qmh}")
            print(f"compressor.E1.gamma: {compressor.E1.gamma}")
            print(f"compressor.E1.h: {compressor.E1.h}")
            print(f"compressor.E1.P: {compressor.E1.P}")
            print(f"compressor.E1.T: {compressor.E1.T}")
            print(f"compressor.Fm.omega: {compressor.Fm.omega}")
            print(f"compressor.Fm.N: {compressor.Fm.N}")
            print(f"volC.F2.Qm: {volC.F2.Qm}")
            print(f"volC.F2.Qmh: {volC.F2.Qmh}")
            print() 

            compressor.E2.P = volC.E1.P
            compressor.E2.T = volC.E1.T
            compressor.E2.h = volC.E1.h

            volC.F1.Qm = compressor.F2.Qm
            volC.F1.Qmh = compressor.F2.Qmh

            sc.updateInputs()
            compressor.E1.gamma = sc.getParameterValue("E1gamma")
            compressor.E1.h = sc.getParameterValue("E1h")
            compressor.E1.P = sc.getParameterValue("E1P")
            compressor.E1.T = sc.getParameterValue("E1T") 
            compressor.Fm.omega = sc.getParameterValue("Fmomega")
            compressor.Fm.N = sc.getParameterValue("FmN")

            #volume compressor (added for intake connection)
            volC.F2.Qm = sc.getParameterValue("F2Qm") 
            volC.F2.Qmh = sc.getParameterValue("F2Qmh")
            
            if compressor.Fm.omega == 0 and compressor.Fm.N == 0:
                print("simple model")
                compressor.Fm = FlowM(n / 30 * math.pi)
                volC.F2 = FlowSource(-0.1, volC.E1.T)

            compressor.Solve() 
            volC.Solve(sc.getCurrentTimeStep().timeStepSize) #simple model
            #volC.Solve(sc.getCurrentTimeStep().timeStepSize, 'Trapezoidal') #thermal model
            
            sc.setParameterValue("F1Qm", compressor.F1.Qm)
            sc.setParameterValue("F1Qmh", compressor.F1.Qmh)
            sc.setParameterValue("EmTq", compressor.Em.Tq)

            #volume compressor (added for intake connection)
            sc.setParameterValue("E2P", volC.E2.P)
            sc.setParameterValue("E2T", volC.E2.T)
            sc.setParameterValue("E2h", volC.E2.h)
            sc.setParameterValue("E2R", volC.E2.R)

            sc.updateOutputs(sysc.Converged)
            multiIteration = True

            result_simu[incr_save, 2] = compressor.E1.P
            result_simu[incr_save, 3] = compressor.E2.P
            result_simu[incr_save, 4] = compressor.E1.T
            result_simu[incr_save, 5] = compressor.E2.T
            result_simu[incr_save, 7] = compressor.F2.Qm
            incr_save = incr_save +1

    rows_to_write = [2, 3, 4, 5, 7]
    start_rows = [3, 4, 5, 6, 8] 

    data_transposed = list(map(list, zip(*result_simu)))

    # Open the existing Excel file for writing
    with pd.ExcelWriter("simpleEngineCompData2.xlsx", mode='w') as writer:
        # Write the selected rows to the Excel file
        for i, row_idx in enumerate(rows_to_write):
            df = pd.DataFrame(data_transposed[row_idx]).T  # Transpose to write as a row
            df.to_excel(writer, index=False, header=False, startrow=start_rows[i])


    print()   
    print("[" + ", ".join(map(str, [row[2] for row in result_simu])) + "]")
    print("[" + ", ".join(map(str, [row[3] for row in result_simu])) + "]")
    print("[" + ", ".join(map(str, [row[4] for row in result_simu])) + "]")
    print("[" + ", ".join(map(str, [row[5] for row in result_simu])) + "]")
    print("[" + ", ".join(map(str, [row[7] for row in result_simu])) + "]")
    print()

sc.disconnect()   
#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#
import sys
import time
sys.path.append('C:/Users/aawan/Documents/SystemCouplingCosimulation/automatedSimpleEngineModel')
import cosim

time1 = time.time()
cosimSetup = cosim.cosimulation()

cosimSetup.setHiddenFeatures()

# add participants
RCAirFilter = cosimSetup.addRCAirFilter()
RCCompressor = cosimSetup.addRCCompressor()

# add data transfers
cosimSetup.connect(RCCompressor, 1, RCAirFilter, 2)

cosimSetup.analysisType("Transient")
cosimSetup.minIterations(1)
cosimSetup.maxIterations(1)
cosimSetup.timeStepSize("0.01 [s]")
cosimSetup.endTime("0.1 [s]")

cosimSetup.solve()
time2 = time.time()
print("Time for Simulation", repr(round((time2 - time1), 5)))
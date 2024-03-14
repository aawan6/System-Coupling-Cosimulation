#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#
import sys
sys.path.append('C:/Users/aawan/Documents/SystemCouplingCosimulation/automatedSimpleEngineModel')
import cosim

cosimSetup = cosim.cosimulation()

cosimSetup.setHiddenFeatures()

# add participants
RCAirFilter = cosimSetup.addRCAirFilter()
RCCompressor = cosimSetup.addRCCompressor()

# add data transfers
cosimSetup.connect(RCCompressor, 1, RCAirFilter, 2)
cosimSetup.analysisType("Transient")
cosimSetup.timeStepSize("0.01 [s]")
cosimSetup.endTime("0.1 [s]")

cosimSetup.solve()
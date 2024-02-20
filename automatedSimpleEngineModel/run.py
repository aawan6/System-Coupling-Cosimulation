#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#
import sys
sys.path.append('C:/Users/aawan/Documents/SystemCouplingCosimulation/automatedSimpleEngineModel')
import cosim

cosimSetup = cosim.cosimulation()

# add participants
airFilter = cosimSetup.addFilter()
volumeAirFilter = cosimSetup.addVolFilter()
compressor = cosimSetup.addCompressor()
volumeCompressor = cosimSetup.addVolCompressor()

# add data transfers
cosimSetup.connect(volumeAirFilter, 1, airFilter, 2)
cosimSetup.connect(compressor, 1, volumeAirFilter, 2)
cosimSetup.connect(volumeCompressor, 1, compressor, 2)

cosimSetup.analysisType("Transient")
cosimSetup.minIterations(1)
cosimSetup.maxIterations(1)
cosimSetup.timeStepSize("0.01 [s]")
cosimSetup.endTime("0.1 [s]")

cosimSetup.solve()
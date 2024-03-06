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
RCIntake = cosimSetup.addRCIntake()
Engine = cosimSetup.addEngine()
RCTurbine = cosimSetup.addRCTurbine() 
TurboShaft = cosimSetup.addTurboShaft()
RCExhaust = cosimSetup.addRCExhaust()
VNTControl = cosimSetup.addVNTControl()

# add data transfers
cosimSetup.connect(RCCompressor, 1, RCAirFilter, 2)
cosimSetup.connect(RCIntake, 1, RCCompressor, 2)
cosimSetup.connect(Engine, 1, RCIntake, 2)
cosimSetup.connect(RCTurbine, 1, Engine, 2)
cosimSetup.connect(RCExhaust, 1, RCTurbine, 2)

cosimSetup.connect(RCTurbine, 3, TurboShaft, 2)
cosimSetup.connect(TurboShaft, 1, RCCompressor, 3)
cosimSetup.connect(VNTControl, 1, RCIntake, 2)
cosimSetup.connect(RCTurbine, 4, VNTControl, 2)

cosimSetup.analysisType("Transient")
cosimSetup.minIterations(1)
cosimSetup.maxIterations(1)
cosimSetup.timeStepSize("0.001 [s]")
cosimSetup.endTime("0.005 [s]")

cosimSetup.solve()
import platform
from enum import Enum

class TransferType(Enum):
    effort = 1
    flow = 2
    x = 3
    y = 4

class QuantityType(Enum):
    enthalpy = 1
    pressure = 2
    temp = 3
    R = 4
    gamma = 5
    Qm = 6
    Qmh = 7
    FAR = 8
    Tq = 9
    omega = 10
    N = 11
    y = 12

class Variable:
    def __init__(self, name, quantityType):
        self.name = name
        self.quantityType = quantityType

class Participant:
    def __init__(self, participantName):
        self.name = participantName

class AirFilter(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {2: TransferType.effort}
        self.outputs = {2: TransferType.flow}
        self.variables = {
            TransferType.effort : {
                2 : [
                    Variable("E2h", QuantityType.enthalpy), 
                    Variable("E2P", QuantityType.pressure),
                    Variable("E2T", QuantityType.temp),
                    Variable("E2R", QuantityType.R)]},
            
            TransferType.flow : {
                2 : [
                    Variable("F2Qm", QuantityType.Qm),
                    Variable("F2Qmh", QuantityType.Qmh)]}}

class VolumeAirFilter(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.flow, 2: TransferType.flow}
        self.outputs = {1: TransferType.effort, 2: TransferType.effort}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp),
                    Variable("E1R", QuantityType.R)],
                
                2 : [Variable("E2h", QuantityType.enthalpy), 
                    Variable("E2P", QuantityType.pressure),
                    Variable("E2T", QuantityType.temp),
                    Variable("E2R", QuantityType.R),
                    Variable("E2gamma", QuantityType.gamma)]},

            TransferType.flow : {
                1: [Variable("F1Qm", QuantityType.Qm),
                    Variable("F1Qmh", QuantityType.Qmh)],

                2: [Variable("F2Qm", QuantityType.Qm),
                    Variable("F2Qmh", QuantityType.Qmh)]}}

class RCAirFilter(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {2: TransferType.flow}
        self.outputs = {2: TransferType.effort}
        self.variables = {
            TransferType.effort : {
                2 : [Variable("E2h", QuantityType.enthalpy), 
                    Variable("E2P", QuantityType.pressure),
                    Variable("E2T", QuantityType.temp),
                    Variable("E2gamma", QuantityType.gamma)]},

            TransferType.flow : {
                2: [Variable("F2Qm", QuantityType.Qm),
                    Variable("F2Qmh", QuantityType.Qmh)]}}

class Compressor(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.effort, 2: TransferType.effort}
        self.outputs = {1: TransferType.flow, 2: TransferType.flow}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp),
                    Variable("E1gamma", QuantityType.gamma)],
                
                2 : [Variable("E2h", QuantityType.enthalpy), 
                    Variable("E2P", QuantityType.pressure),
                    Variable("E2T", QuantityType.temp)]},

            TransferType.flow : {
                1: [Variable("F1Qm", QuantityType.Qm),
                    Variable("F1Qmh", QuantityType.Qmh)],

                2: [Variable("F2Qm", QuantityType.Qm),
                    Variable("F2Qmh", QuantityType.Qmh)]}}
        
class VolumeCompressor(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.flow}
        self.outputs = {1: TransferType.effort}
        self.variables = {
            TransferType.effort : {
                1 : [
                    Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp),
                    Variable("E1R", QuantityType.R)]},
            
            TransferType.flow : {
                1 : [
                    Variable("F1Qm", QuantityType.Qm),
                    Variable("F1Qmh", QuantityType.Qmh)]}}
        
class RCCompressor(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.effort, 2: TransferType.flow, 3: TransferType.flow}
        self.outputs = {1: TransferType.flow, 2: TransferType.effort, 3: TransferType.effort}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp),
                    Variable("E1gamma", QuantityType.gamma)],

                2:  [Variable("E2h", QuantityType.enthalpy), 
                    Variable("E2P", QuantityType.pressure),
                    Variable("E2T", QuantityType.temp),
                    Variable("E2R", QuantityType.temp)],
                    
                3: [Variable("EmTq", QuantityType.Tq)]},

            TransferType.flow : {
                1:  [Variable("F1Qm", QuantityType.Qm),
                    Variable("F1Qmh", QuantityType.Qmh)],
                    
                2:  [Variable("F2Qm", QuantityType.Qm),
                    Variable("F2Qmh", QuantityType.Qmh)],
                    
                3: [Variable("Fmomega", QuantityType.omega),
                   Variable("FmN", QuantityType.N) ]}}

class RCIntake(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.effort, 2: TransferType.flow}
        self.outputs = {1: TransferType.flow, 2: TransferType.effort, 3: TransferType.effort}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp),
                    Variable("E1R", QuantityType.temp)],

                2:  [Variable("E2h", QuantityType.enthalpy), 
                    Variable("E2P", QuantityType.pressure),
                    Variable("E2T", QuantityType.temp),
                    Variable("E2R", QuantityType.R)]},

            TransferType.flow : {
                1:  [Variable("F1Qm", QuantityType.Qm),
                    Variable("F1Qmh", QuantityType.Qmh)],
                    
                2:  [Variable("F2Qm", QuantityType.Qm),
                    Variable("F2Qmh", QuantityType.Qmh)]}}
        
class Engine(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.effort, 2: TransferType.effort}
        self.outputs = {1: TransferType.flow, 2: TransferType.flow}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp),
                    Variable("E1R", QuantityType.R)],

                2:  [Variable("E2h", QuantityType.enthalpy), 
                    Variable("E2P", QuantityType.pressure),
                    Variable("E2T", QuantityType.temp)]},

            TransferType.flow : {
                1:  [Variable("F1Qm", QuantityType.Qm),
                    Variable("F1Qmh", QuantityType.Qmh)],
                    
                2:  [Variable("F2Qm", QuantityType.Qm),
                    Variable("F2Qmh", QuantityType.Qmh),
                    Variable("FAR", QuantityType.FAR)]}}
        
class RCTurbine(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.flow, 2: TransferType.effort, 3: TransferType.flow, 4: TransferType.y}
        self.outputs = {1: TransferType.effort, 2: TransferType.flow, 3: TransferType.effort}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp)],

                2:  [Variable("E2h", QuantityType.enthalpy), 
                    Variable("E2P", QuantityType.pressure),
                    Variable("E2T", QuantityType.temp)],

                3: [Variable("EmTq", QuantityType.Tq)]},

            TransferType.flow : {
                1:  [Variable("F1Qm", QuantityType.Qm),
                    Variable("F1Qmh", QuantityType.Qmh),
                    Variable("F1FAR", QuantityType.FAR)],
                    
                2:  [Variable("F2FAR", QuantityType.FAR),
                    Variable("F2Qm", QuantityType.Qm),
                    Variable("F2Qmh", QuantityType.Qmh)],

                3: [Variable("Fmomega", QuantityType.omega),
                   Variable("FmN", QuantityType.N) ]},
            
            TransferType.y : {
                4: [Variable("PI_VNTy", QuantityType.y)]}}
        
class TurboShaft(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.effort, 2: TransferType.effort}
        self.outputs = {1: TransferType.flow, 2: TransferType.flow}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("Em1Tq", QuantityType.Tq)],

                2:  [Variable("Em2Tq", QuantityType.Tq)]},

            TransferType.flow : {
                1:  [Variable("Fm1omega", QuantityType.omega),
                    Variable("Fm1N", QuantityType.N)],
                    
                2:  [Variable("Fm2omega", QuantityType.omega),
                    Variable("Fm2N", QuantityType.N)]}}
        
class RCExhaust(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.flow}
        self.outputs = {1: TransferType.effort}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp)]},

            TransferType.flow : {
                1:  [Variable("F1Qm", QuantityType.Qm),
                    Variable("F1Qmh", QuantityType.Qmh),
                    Variable("FAR", QuantityType.FAR)]}}
        
class VNTControl(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.inputs = {1: TransferType.effort}
        self.outputs = {2: TransferType.y}    
        self.variables = {
            TransferType.effort : {
                1 : [Variable("x_Act", QuantityType.pressure)]},

            TransferType.y : {
                2:  [Variable("PI_VNTy", QuantityType.y)]}}    

class cosimulation:

    def __init__(self):
        self.dm = DatamodelRoot()

    def getScriptName(self, baseName):
        return f"{baseName}.bat" if platform.system() == "Windows" else f"{baseName}.sh"

    def addFilter(self):
        airFilterName = AddParticipant(Executable=self.getScriptName("AirFilter"))
        self.dm.CouplingParticipant[airFilterName].DisplayName = "Air Filter"
        airFilter = AirFilter(airFilterName)
        return airFilter

    def addVolFilter(self):
        volumeAirFilterName = AddParticipant(Executable=self.getScriptName("VolumeAirFilter"))
        self.dm.CouplingParticipant[volumeAirFilterName].DisplayName = "Volume Air Filter"
        volumeAirFilter = VolumeAirFilter(volumeAirFilterName)
        return volumeAirFilter

    def addCompressor(self):
        compressorName = AddParticipant(Executable=self.getScriptName("Compressor"))
        self.dm.CouplingParticipant[compressorName].DisplayName = "Compressor"
        compressor = Compressor(compressorName)
        return compressor

    def addVolCompressor(self):
        volumeCompressorName = AddParticipant(Executable=self.getScriptName("VolumeCompressor"))
        self.dm.CouplingParticipant[volumeCompressorName].DisplayName = "Volume Compressor"
        volumeCompressor = VolumeCompressor(volumeCompressorName)
        return volumeCompressor
        
    def addRCAirFilter(self):
        RCAirFilterName = AddParticipant(Executable=self.getScriptName("RCAirFilter"))
        self.dm.CouplingParticipant[RCAirFilterName].DisplayName = "RC Air Filter"
        rcAirFilter = RCAirFilter(RCAirFilterName)
        return rcAirFilter
    
    def addRCCompressor(self):
        RCCompressorName = AddParticipant(Executable=self.getScriptName("RCCompressor"))
        self.dm.CouplingParticipant[RCCompressorName].DisplayName = "RC Compressor"
        rcCompressor = RCCompressor(RCCompressorName)
        return rcCompressor
    
    def addRCIntake(self):
        RCIntakeName = AddParticipant(Executable=self.getScriptName("RCIntake"))
        self.dm.CouplingParticipant[RCIntakeName].DisplayName = "RC Intake"
        rcIntake = RCIntake(RCIntakeName)
        return rcIntake
    
    def addEngine(self):
        engineName = AddParticipant(Executable=self.getScriptName("Engine"))
        self.dm.CouplingParticipant[engineName].DisplayName = "Engine"
        engine = Engine(engineName)
        return engine
    
    def addRCTurbine(self):
        RCTurbineName = AddParticipant(Executable=self.getScriptName("RCTurbine"))
        self.dm.CouplingParticipant[RCTurbineName].DisplayName = "RC Turbine"
        rcTurbine = RCTurbine(RCTurbineName)
        return rcTurbine
    
    def addTurboShaft(self):
        turboShaftName = AddParticipant(Executable=self.getScriptName("TurboShaft"))
        self.dm.CouplingParticipant[turboShaftName].DisplayName = "TurboShaft"
        turboShaft = TurboShaft(turboShaftName)
        return turboShaft
    
    def addRCExhaust(self):
        RCExhaustName = AddParticipant(Executable=self.getScriptName("RCExhaust"))
        self.dm.CouplingParticipant[RCExhaustName].DisplayName = "RC Exhaust"
        rcExhaust = RCExhaust(RCExhaustName)
        return rcExhaust
    
    def addVNTControl(self):
        VNT_ControlName = AddParticipant(Executable=self.getScriptName("VNTControl"))
        self.dm.CouplingParticipant[VNT_ControlName].DisplayName = "VNT Control"
        vnt_Control = VNTControl(VNT_ControlName)
        return vnt_Control

    def connect(self, sideOnePar, sideOnePort, sideTwoPar, sideTwoPort):
        interface2 = AddInterface(
            SideOneParticipant= sideOnePar.name, SideTwoParticipant= sideTwoPar.name
            )
        #setup transfers from sideOne to sideTwo
        sideOneTransferType = sideOnePar.outputs.get(sideOnePort, None)
        sideTwoTransferType = sideTwoPar.inputs.get(sideTwoPort, None)
        if sideOneTransferType is not None and sideTwoTransferType is not None:
            assert sideOneTransferType == sideTwoTransferType
            sideOneVariables = sideOnePar.variables[sideOneTransferType][sideOnePort]
            sideTwoVariables = sideTwoPar.variables[sideTwoTransferType][sideTwoPort]
                
            for sideOneVar in sideOneVariables:
                for sideTwoVar in sideTwoVariables:
                    if sideOneVar.quantityType == sideTwoVar.quantityType:
                        AddDataTransfer(
                                interface=interface2,
                                TargetSide="Two",
                                SourceVariable= sideOneVar.name,
                                TargetVariable= sideTwoVar.name
                            )
                        break
        
        #setup transfers from sideTwo to sideOne
        sideOneTransferType = sideOnePar.inputs.get(sideOnePort, None)
        sideTwoTransferType = sideTwoPar.outputs.get(sideTwoPort, None)
        if sideOneTransferType is not None and sideTwoTransferType is not None:
            assert sideOneTransferType == sideTwoTransferType
            sideOneVariables = sideOnePar.variables[sideOneTransferType][sideOnePort]
            sideTwoVariables = sideTwoPar.variables[sideTwoTransferType][sideTwoPort]

            for sideOneVar in sideOneVariables:
                for sideTwoVar in sideTwoVariables:
                    if sideOneVar.quantityType == sideTwoVar.quantityType:
                        AddDataTransfer(
                                interface=interface2,
                                TargetSide="One",
                                SourceVariable= sideTwoVar.name,
                                TargetVariable= sideOneVar.name
                            )
                        break
    
    def setHiddenFeatures(self):
        self.dm.ActivateHidden.BetaFeatures = True
        self.dm.ActivateHidden.AlphaFeatures = True

    def analysisType(self, type):
        self.dm.AnalysisControl.AnalysisType = type

    def minIterations(self, number):
        self.dm.SolutionControl.MinimumIterations= number

    def maxIterations(self, number):
        self.dm.SolutionControl.MaximumIterations = number

    def timeStepSize(self, time):
        self.dm.SolutionControl.TimeStepSize = time

    def endTime(self, time):
        self.dm.SolutionControl.EndTime= time

    def solve(self):
        Solve()
        

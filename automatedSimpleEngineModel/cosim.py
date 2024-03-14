import platform
import ansys.systemcoupling.core as pysystemcoupling
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
                    Variable("E2R", QuantityType.R)],
                    
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
        self.outputs = {1: TransferType.flow, 2: TransferType.effort}
        self.variables = {
            TransferType.effort : {
                1 : [Variable("E1h", QuantityType.enthalpy), 
                    Variable("E1P", QuantityType.pressure),
                    Variable("E1T", QuantityType.temp),
                    Variable("E1R", QuantityType.R)],

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
        self.syc = pysystemcoupling.launch()
        self.setup = self.syc.setup

    def getScriptName(self, baseName):
        return f"{baseName}.bat" if platform.system() == "Windows" else f"{baseName}.sh"

    def addFilter(self):
        airFilterName = self.setup.add_participant(executable=self.getScriptName("AirFilter"))
        self.setup.coupling_participant[airFilterName].display_name = "Air Filter"
        airFilter = AirFilter(airFilterName)
        return airFilter

    def addVolFilter(self):
        volumeAirFilterName = self.setup.add_participant(executable=self.getScriptName("VolumeAirFilter"))
        self.setup.coupling_participant[volumeAirFilterName].display_name = "Volume Air Filter"
        volumeAirFilter = VolumeAirFilter(volumeAirFilterName)
        return volumeAirFilter

    def addCompressor(self):
        compressorName = self.setup.add_participant(executable=self.getScriptName("Compressor"))
        self.setup.coupling_participant[compressorName].display_name = "Compressor"
        compressor = Compressor(compressorName)
        return compressor

    def addVolCompressor(self):
        volumeCompressorName = self.setup.add_participant(executable=self.getScriptName("VolumeCompressor"))
        self.setup.coupling_participant[volumeCompressorName].display_name = "Volume Compressor"
        volumeCompressor = VolumeCompressor(volumeCompressorName)
        return volumeCompressor
        
    def addRCAirFilter(self):
        RCAirFilterName = self.setup.add_participant(executable=self.getScriptName("RCAirFilter"))
        #RCAirFilterName = self.setup.add_participant(python_script="RCAirFilter.py")
        self.setup.coupling_participant[RCAirFilterName].display_name = "RC Air Filter"
        rcAirFilter = RCAirFilter(RCAirFilterName)
        return rcAirFilter
    
    def addRCCompressor(self):
        RCCompressorName = self.setup.add_participant(executable=self.getScriptName("RCCompressor"))
        #RCCompressorName = self.setup.add_participant(python_script="RCCompressor.py")
        self.setup.coupling_participant[RCCompressorName].display_name = "RC Compressor"
        rcCompressor = RCCompressor(RCCompressorName)
        return rcCompressor
    
    def addRCIntake(self):
        RCIntakeName = self.setup.add_participant(executable=self.getScriptName("RCIntake"))
        self.setup.coupling_participant[RCIntakeName].display_name = "RC Intake"
        rcIntake = RCIntake(RCIntakeName)
        return rcIntake
    
    def addEngine(self):
        engineName = self.setup.add_participant(executable=self.getScriptName("Engine"))
        self.setup.coupling_participant[engineName].display_name = "Engine"
        engine = Engine(engineName)
        return engine
    
    def addRCTurbine(self):
        RCTurbineName = self.setup.add_participant(executable=self.getScriptName("RCTurbine"))
        self.setup.coupling_participant[RCTurbineName].display_name = "RC Turbine"
        rcTurbine = RCTurbine(RCTurbineName)
        return rcTurbine
    
    def addTurboShaft(self):
        turboShaftName = self.setup.add_participant(executable=self.getScriptName("TurboShaft"))
        self.setup.coupling_participant[turboShaftName].display_name = "TurboShaft"
        turboShaft = TurboShaft(turboShaftName)
        return turboShaft
    
    def addRCExhaust(self):
        RCExhaustName = self.setup.add_participant(executable=self.getScriptName("RCExhaust"))
        self.setup.coupling_participant[RCExhaustName].display_name = "RC Exhaust"
        rcExhaust = RCExhaust(RCExhaustName)
        return rcExhaust
    
    def addVNTControl(self):
        VNT_ControlName = self.setup.add_participant(executable=self.getScriptName("VNTControl"))
        self.setup.coupling_participant[VNT_ControlName].display_name = "VNT Control"
        vnt_Control = VNTControl(VNT_ControlName)
        return vnt_Control

    def connect(self, sideOneParticipant, sideOnePort, sideTwoParticipant, sideTwoPort):
        interface2 = self.setup.add_interface(
            side_one_participant= sideOneParticipant.name, side_two_participant= sideTwoParticipant.name
            )
        #setup transfers from sideOne to sideTwo
        sideOneTransferType = sideOneParticipant.outputs.get(sideOnePort, None)
        sideTwoTransferType = sideTwoParticipant.inputs.get(sideTwoPort, None)
        if sideOneTransferType is not None and sideTwoTransferType is not None:
            assert sideOneTransferType == sideTwoTransferType
            sideOneVariables = sideOneParticipant.variables[sideOneTransferType][sideOnePort]
            sideTwoVariables = sideTwoParticipant.variables[sideTwoTransferType][sideTwoPort]
                
            for sideOneVar in sideOneVariables:
                for sideTwoVar in sideTwoVariables:
                    if sideOneVar.quantityType == sideTwoVar.quantityType:
                        self.setup.add_data_transfer(
                                interface=interface2,
                                target_side="Two",
                                source_variable= sideOneVar.name,
                                target_variable= sideTwoVar.name
                            )
                        break
        
        #setup transfers from sideTwo to sideOne
        sideOneTransferType = sideOneParticipant.inputs.get(sideOnePort, None)
        sideTwoTransferType = sideTwoParticipant.outputs.get(sideTwoPort, None)
        if sideOneTransferType is not None and sideTwoTransferType is not None:
            assert sideOneTransferType == sideTwoTransferType
            sideOneVariables = sideOneParticipant.variables[sideOneTransferType][sideOnePort]
            sideTwoVariables = sideTwoParticipant.variables[sideTwoTransferType][sideTwoPort]

            for sideOneVar in sideOneVariables:
                for sideTwoVar in sideTwoVariables:
                    if sideOneVar.quantityType == sideTwoVar.quantityType:
                        self.setup.add_data_transfer(
                                interface=interface2,
                                target_side="One",
                                source_variable= sideTwoVar.name,
                                target_variable= sideOneVar.name
                            )
                        break
    
    def setHiddenFeatures(self):
        self.setup.activate_hidden.beta_features = True
        self.setup.activate_hidden.alpha_features = True

    def analysisType(self, type):
        self.setup.analysis_control.analysis_type = type

    def minIterations(self, number):
        self.setup.solution_control.minimum_iterations = number

    def maxIterations(self, number):
        self.setup.solution_control.maximum_iterations = number

    def timeStepSize(self, time):
        self.setup.solution_control.time_step_size = time

    def endTime(self, time):
        self.setup.solution_control.end_time = time

    def solve(self):
        self.syc.start_output()
        self.solution = self.syc.solution
        self.solution.solve()
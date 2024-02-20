import platform
import ansys.systemcoupling.core as pysystemcoupling
from enum import Enum

class TransferType(Enum):
    effort = 1
    flow = 2

class QuantityType(Enum):
    enthalpy = 1
    pressure = 2
    temp = 3
    R = 4
    gamma = 5
    Qm = 6
    Qmh = 7

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
        self.ports = [2]
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
        self.ports = [1, 2]
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

class Compressor(Participant):
    def __init__(self, participantName):
        Participant.__init__(self, participantName)
        self.ports = [1, 2]
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
        self.ports = [1]
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

class cosimulation:

    def __init__(self):
        self.syc = pysystemcoupling.launch()
        self.setup = self.syc.setup

    def getScriptName(self, baseName):
        return f"{baseName}.bat" if platform.system() == "Windows" else f"{baseName}.sh"

    def addFilter(self):
        airFilterName = self.setup.add_participant(executable=self.getScriptName("AirFilter"))
        airFilter = AirFilter(airFilterName)
        return airFilter

    def addVolFilter(self):
        volumeAirFilterName = self.setup.add_participant(executable=self.getScriptName("VolumeAirFilter"))
        volumeAirFilter = VolumeAirFilter(volumeAirFilterName)
        return volumeAirFilter
        
    def addCompressor(self):
        compressorName = self.setup.add_participant(executable=self.getScriptName("Compressor"))
        compressor = Compressor(compressorName)
        return compressor

    def addVolCompressor(self):
        volumeCompressorName = self.setup.add_participant(executable=self.getScriptName("VolumeCompressor"))
        volumeCompressor = VolumeCompressor(volumeCompressorName)
        return volumeCompressor

    def connect(self, sideOneParticipant, sideOnePort, sideTwoParticipant, sideTwoPort):
        interface2 = self.setup.add_interface(
            side_one_participant= sideOneParticipant.name, side_two_participant= sideTwoParticipant.name
            )

        #setup transfers from sideOne to sideTwo
        sideOneTransferType = sideOneParticipant.outputs[sideOnePort]
        sideTwoTransferType = sideTwoParticipant.inputs[sideTwoPort]
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
        sideOneTransferType = sideOneParticipant.inputs[sideOnePort]
        sideTwoTransferType = sideTwoParticipant.outputs[sideTwoPort]
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
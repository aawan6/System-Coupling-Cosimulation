import platform
import ansys.systemcoupling.core as pysystemcoupling
#from kernel.framework.ApplicationContext import ApplicationContext
from enum import Enum

class ParticipantType(Enum):
    airFilter = 1
    volumeAirFilter = 2
    compressor = 3
    volumeCompressor = 4

class Participant:
    def __init__(self, participantName, participantType):
        self.name = participantName
        self.type = participantType

class cosimulation:

    def __init__(self):
        self.syc = pysystemcoupling.launch()
        self.setup = self.syc.setup

    def getScriptName(self, baseName):
        return f"{baseName}.bat" if platform.system() == "Windows" else f"{baseName}.sh"

    def addFilter(self):
        airFilterName = self.setup.add_participant(executable=self.getScriptName("AirFilter"))
        airFilter = Participant(airFilterName, ParticipantType.airFilter)
        return airFilter

    def addVolFilter(self):
        volumeAirFilterName = self.setup.add_participant(executable=self.getScriptName("VolumeAirFilter"))
        volumeAirFilter = Participant(volumeAirFilterName, ParticipantType.volumeAirFilter)
        return volumeAirFilter
        
    def addCompressor(self):
        compressorName = self.setup.add_participant(executable=self.getScriptName("Compressor"))
        compressor = Participant(compressorName, ParticipantType.compressor)
        return compressor

    def addVolCompressor(self):
        volumeCompressorName = self.setup.add_participant(executable=self.getScriptName("VolumeCompressor"))
        volumeCompressor = Participant(volumeCompressorName, ParticipantType.volumeCompressor)
        return volumeCompressor

    def connect(self, sideOneParticipant, sideTwoParticipant):

        if sideOneParticipant.type == ParticipantType.volumeAirFilter and sideTwoParticipant.type == ParticipantType.airFilter:
            interface2 = self.setup.add_interface(
            side_one_participant= sideOneParticipant.name, side_two_participant= sideTwoParticipant.name
            )

            self.setup.add_data_transfer(
                interface=interface2, target_side="Two", source_variable="E1h", target_variable="E2h"
            )
            self.setup.add_data_transfer(
                interface=interface2, target_side="Two", source_variable="E1P", target_variable="E2P"
            )
            self.setup.add_data_transfer(
                interface=interface2, target_side="Two", source_variable="E1R", target_variable="E2R"
            )
            self.setup.add_data_transfer(
                interface=interface2, target_side="Two", source_variable="E1T", target_variable="E2T"
            )
            self.setup.add_data_transfer(
                interface=interface2, target_side="One", source_variable="F2Qm", target_variable="F1Qm"
            )
            self.setup.add_data_transfer(
                interface=interface2, target_side="One", source_variable="F2Qmh", target_variable="F1Qmh",
            )

        elif sideOneParticipant.type == ParticipantType.compressor and sideTwoParticipant.type == ParticipantType.volumeAirFilter:
            
            interface3 = self.setup.add_interface(
            side_one_participant= sideOneParticipant.name, side_two_participant= sideTwoParticipant.name
            )

            self.setup.add_data_transfer(
                interface=interface3, target_side="Two", source_variable="F1Qm", target_variable="F2Qm"
            )
            self.setup.add_data_transfer(
                interface=interface3, target_side="Two", source_variable="F1Qmh", target_variable="F2Qmh",
            )
            self.setup.add_data_transfer(
                interface=interface3, target_side="One", source_variable="E2gamma", target_variable="E1gamma",
            )
            self.setup.add_data_transfer(
                interface=interface3, target_side="One", source_variable="E2h", target_variable="E1h"
            )
            self.setup.add_data_transfer(
                interface=interface3, target_side="One", source_variable="E2P", target_variable="E1P"
            )
            self.setup.add_data_transfer(
                interface=interface3, target_side="One", source_variable="E2T", target_variable="E1T"
            )

        elif sideOneParticipant.type == ParticipantType.volumeCompressor and sideTwoParticipant.type == ParticipantType.compressor:
            
            interface4 = self.setup.add_interface(
            side_one_participant= sideOneParticipant.name, side_two_participant= sideTwoParticipant.name
            )

            self.setup.add_data_transfer(
            interface=interface4, target_side="Two", source_variable="E1P", target_variable="E2P"
            )
            self.setup.add_data_transfer(
                interface=interface4, target_side="Two", source_variable="E1T", target_variable="E2T"
            )
            self.setup.add_data_transfer(
                interface=interface4, target_side="Two", source_variable="E1h", target_variable="E2h"
            )
            self.setup.add_data_transfer(
                interface=interface4, target_side="One", source_variable="F2Qm", target_variable="F1Qm"
            )
            self.setup.add_data_transfer(
                interface=interface4, target_side="One", source_variable="F2Qmh", target_variable="F1Qmh",
            )
    
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
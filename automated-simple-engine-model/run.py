#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#

import platform
import sys
dm = DatamodelRoot()

#dm.ActivateHidden.BetaFeatures = True
#dm.AnalysisControl.AllowSimultaneousUpdate = True
#dm.AnalysisControl.SimultaneousParticipants = "All"

def getScriptName(baseName):
    return f"{baseName}.bat" if platform.system() == "Windows" else f"{baseName}.sh"

# add participants
airFilter = AddParticipant(Executable=getScriptName("AirFilter"))
dm.CouplingParticipant[airFilter].DisplayName = "Air Filter"

volumeAirFilter = AddParticipant(Executable=getScriptName("VolumeAirFilter"))
dm.CouplingParticipant[volumeAirFilter].DisplayName = "Volume Air Filter"

compressor = AddParticipant(Executable=getScriptName("Compressor"))
dm.CouplingParticipant[compressor].DisplayName = "Compressor"

volumeCompressor = AddParticipant(Executable=getScriptName("VolumeCompressor"))
dm.CouplingParticipant[volumeCompressor].DisplayName = "Volume Compressor"

# add data transfers
interface2 = AddInterface(
    SideOneParticipant=volumeAirFilter, SideTwoParticipant=airFilter
)
AddDataTransfer(
    Interface=interface2, TargetSide="Two", SourceVariable="E1h", TargetVariable="E2h"
)
AddDataTransfer(
    Interface=interface2, TargetSide="Two", SourceVariable="E1P", TargetVariable="E2P"
)
AddDataTransfer(
    Interface=interface2, TargetSide="Two", SourceVariable="E1R", TargetVariable="E2R"
)
AddDataTransfer(
    Interface=interface2, TargetSide="Two", SourceVariable="E1T", TargetVariable="E2T"
)
AddDataTransfer(
    Interface=interface2, TargetSide="One", SourceVariable="F2Qm", TargetVariable="F1Qm"
)
AddDataTransfer(
    Interface=interface2,
    TargetSide="One",
    SourceVariable="F2Qmh",
    TargetVariable="F1Qmh",
)

interface3 = AddInterface(
    SideOneParticipant=compressor, SideTwoParticipant=volumeAirFilter
)
AddDataTransfer(
    Interface=interface3, TargetSide="Two", SourceVariable="F1Qm", TargetVariable="F2Qm"
)
AddDataTransfer(
    Interface=interface3,
    TargetSide="Two",
    SourceVariable="F1Qmh",
    TargetVariable="F2Qmh",
)
AddDataTransfer(
    Interface=interface3,
    TargetSide="One",
    SourceVariable="E2gamma",
    TargetVariable="E1gamma",
)
AddDataTransfer(
    Interface=interface3, TargetSide="One", SourceVariable="E2h", TargetVariable="E1h"
)
AddDataTransfer(
    Interface=interface3, TargetSide="One", SourceVariable="E2P", TargetVariable="E1P"
)
AddDataTransfer(
    Interface=interface3, TargetSide="One", SourceVariable="E2T", TargetVariable="E1T"
)

interface4 = AddInterface(
    SideOneParticipant=volumeCompressor, SideTwoParticipant=compressor
)
AddDataTransfer(
    Interface=interface4, TargetSide="Two", SourceVariable="E1P", TargetVariable="E2P"
)
AddDataTransfer(
    Interface=interface4, TargetSide="Two", SourceVariable="E1T", TargetVariable="E2T"
)
AddDataTransfer(
    Interface=interface4, TargetSide="Two", SourceVariable="E1h", TargetVariable="E2h"
)
AddDataTransfer(
    Interface=interface4, TargetSide="One", SourceVariable="F2Qm", TargetVariable="F1Qm"
)
AddDataTransfer(
    Interface=interface4,
    TargetSide="One",
    SourceVariable="F2Qmh",
    TargetVariable="F1Qmh",
)

dm.AnalysisControl.AnalysisType = "Transient"
dm.SolutionControl.MinimumIterations = 1
dm.SolutionControl.MaximumIterations = 1
dm.SolutionControl.TimeStepSize = "0.01 [s]"
dm.SolutionControl.EndTime = "0.1 [s]"

Solve()
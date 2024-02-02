#
# Copyright ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#
import ansys.systemcoupling.core as pysystemcoupling
import platform
import sys

syc = pysystemcoupling.launch()
setup = syc.setup

def getScriptName(baseName):
    return f"{baseName}.bat" if platform.system() == "Windows" else f"{baseName}.sh"

# add participants
airFilter = setup.add_participant(executable=getScriptName("AirFilter"))

volumeAirFilter = setup.add_participant(executable=getScriptName("VolumeAirFilter"))

compressor = setup.add_participant(executable=getScriptName("Compressor"))

volumeCompressor = setup.add_participant(executable=getScriptName("VolumeCompressor"))

# add data transfers
interface2 = setup.add_interface(
    side_one_participant=volumeAirFilter, side_two_participant=airFilter
)
setup.add_data_transfer(
    interface=interface2, target_side="Two", source_variable="E1h", target_variable="E2h"
)
setup.add_data_transfer(
    interface=interface2, target_side="Two", source_variable="E1P", target_variable="E2P"
)
setup.add_data_transfer(
    interface=interface2, target_side="Two", source_variable="E1R", target_variable="E2R"
)
setup.add_data_transfer(
    interface=interface2, target_side="Two", source_variable="E1T", target_variable="E2T"
)
setup.add_data_transfer(
    interface=interface2, target_side="One", source_variable="F2Qm", target_variable="F1Qm"
)
setup.add_data_transfer(
    interface=interface2,
    target_side="One",
    source_variable="F2Qmh",
    target_variable="F1Qmh",
)

interface3 = setup.add_interface(
    side_one_participant=compressor, side_two_participant=volumeAirFilter
)
setup.add_data_transfer(
    interface=interface3, target_side="Two", source_variable="F1Qm", target_variable="F2Qm"
)
setup.add_data_transfer(
    interface=interface3,
    target_side="Two",
    source_variable="F1Qmh",
    target_variable="F2Qmh",
)
setup.add_data_transfer(
    interface=interface3,
    target_side="One",
    source_variable="E2gamma",
    target_variable="E1gamma",
)
setup.add_data_transfer(
    interface=interface3, target_side="One", source_variable="E2h", target_variable="E1h"
)
setup.add_data_transfer(
    interface=interface3, target_side="One", source_variable="E2P", target_variable="E1P"
)
setup.add_data_transfer(
    interface=interface3, target_side="One", source_variable="E2T", target_variable="E1T"
)

interface4 = setup.add_interface(
    side_one_participant=volumeCompressor, side_two_participant=compressor
)
setup.add_data_transfer(
    interface=interface4, target_side="Two", source_variable="E1P", target_variable="E2P"
)
setup.add_data_transfer(
    interface=interface4, target_side="Two", source_variable="E1T", target_variable="E2T"
)
setup.add_data_transfer(
    interface=interface4, target_side="Two", source_variable="E1h", target_variable="E2h"
)
setup.add_data_transfer(
    interface=interface4, target_side="One", source_variable="F2Qm", target_variable="F1Qm"
)
setup.add_data_transfer(
    interface=interface4,
    target_side="One",
    source_variable="F2Qmh",
    target_variable="F1Qmh",
)

setup.analysis_control.analysis_type = "Transient"
setup.solution_control.minimum_iterations = 1
setup.solution_control.maximum_iterations = 1
setup.solution_control.time_step_size = "0.01 [s]"
setup.solution_control.end_time = "0.1 [s]"

syc.start_output()
solution = syc.solution
solution.solve()
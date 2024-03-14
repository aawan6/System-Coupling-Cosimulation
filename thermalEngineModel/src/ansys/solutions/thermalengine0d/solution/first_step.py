# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Backend of the first step."""

#from ansys.saf.glow.solution import StepModel, StepSpec, transaction

import numpy as np
import matplotlib.pyplot as plt
import math
import time
import copy
from configparser import ConfigParser
import sys
sys.path.append("C:\\Users\\aawan\\Documents\\SystemCouplingCosimulation\\thermalEngineModel\\src")
from ansys.solutions.thermalengine0d.solution.config_step import ConfigStep
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolv, interpolm
from ansys.solutions.thermalengine0d.model.Library_ThermoFluid_class import Compressor_Tf, Turbine_TF, Engine_Tf, PressureLosses_R, Volume_C, EffortSource, FlowSource
from ansys.solutions.thermalengine0d.model.scripts.Fluid_properties_class import FluidFuel
from ansys.solutions.thermalengine0d.model.Library_Mechanics_class import Shaft_I
from ansys.solutions.thermalengine0d.model.Library_Control_class import PI_control
from ansys.solutions.thermalengine0d.model.Library_Fluid_class import Injector_Sf
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortM, FlowM


#class FirstStep(StepModel):
"""Step definition of the first step."""


result: float = 0
result_simu: dict = {}

#@transaction(self=StepSpec(upload=["result", "result_simu"]), config_step=StepSpec(download=["first_arg", "second_arg", "third_arg","control", "config", "x_N","y_N", "x_pps", "y_pps"]))
#def calculate(self, config_step: ConfigStep) -> None:


time1 = time.time()
"-----------------------------------------------------------"
"SIMULATION PARAMETER"
"-----------------------------------------------------------"
configStep = ConfigStep()
configStep.configure()
start_simu = 0
end_simu = configStep.first_arg
step_simu = configStep.second_arg
sample_time = configStep.third_arg
LastVal = (end_simu - start_simu) / step_simu

"-----------------------------------------------------------"
"SIMULATION CONFIG IMPORT"
"-----------------------------------------------------------"
config = configStep.config
control = configStep.control



"-----------------------------------------------------------"
"INIT"
"-----------------------------------------------------------"
Nturbo = eval(config['Integrators_init']['nturbo'])
print(f"config['AirFilter_param']['vol_af']: {config['AirFilter_param']['vol_af']}")
VNT = 0.7
Pair = eval(config['Engine_param']['pair'])
Tair = eval(config['Engine_param']['tair'])
P0 = eval(control['Engine_control']['p0'])
T0 = eval(control['Engine_control']['t0'])
Fuel = FluidFuel(eval(config['Fuel_param']['ks']), eval(config['Fuel_param']['lhv']),
                    eval(config['Fuel_param']['hv']), eval(config['Fuel_param']['nc']),
                    eval(config['Fuel_param']['nh']))
Ambient_Air = EffortSource(P0, T0)
Flow_init = FlowSource(0, T0)
print(f"Pair: {Pair}")
print(f"Tair: {Tair}")

"Creation of vectors for saving / plots"
result_simu = np.zeros((int(LastVal + 1 * step_simu / sample_time), 15), dtype = float)
time_simu = np.arange(1, LastVal + 2)

"-----------------------------------------------------------"
"MODEL CREATION"
"-----------------------------------------------------------"
AirFilter = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
VolumeAirFilter = Volume_C(Flow_init.F, Flow_init.F)
Compressor = Compressor_Tf(Ambient_Air.E, Ambient_Air.E, FlowM(Nturbo / 30 * math.pi))
VolumeCompr = Volume_C(Flow_init.F, Flow_init.F)
Intake = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
VolumeIntake = Volume_C(Flow_init.F, Flow_init.F)
Injector = Injector_Sf(0, Fuel.LHV)
Engine = Engine_Tf(Ambient_Air.E, Ambient_Air.E, FlowM(0), Injector, Fuel, Pair, Tair)
VolumeTurb = Volume_C(Flow_init.F, Flow_init.F, P0, T0, Fuel.nC, Fuel.nH, Engine.FAR)
Turbine = Turbine_TF(Ambient_Air.E, Ambient_Air.E, FlowM(Nturbo / 30 * math.pi), VNT, Fuel.nC, Fuel.nH,
                        Engine.FAR)
VolumeExhaust = Volume_C(Flow_init.F, Flow_init.F, P0, T0, Fuel.nC, Fuel.nH, Engine.FAR)
Exhaust = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
TurboShaft = Shaft_I(EffortM(0), EffortM(0), Nturbo / 30 * math.pi)
PI_VNT = PI_control(P0, P0)

"-----------------------------------------------------------"
"MODEL PARAM"
"-----------------------------------------------------------"
AirFilter.Param(eval(config['AirFilter_param']['k_pl_af']))
VolumeAirFilter.Param(eval(config['AirFilter_param']['vol_af']))
Compressor.Param(eval(config['Compr_param']['prefc']), eval(config['Compr_param']['trefc']),
                    eval(config['Compr_param']['x_nc']), eval(config['Compr_param']['surge_pr']),
                    eval(config['Compr_param']['y_margin']), eval(config['Compr_param']['z_flow_cor']),
                    eval(config['Compr_param']['z_eta_comp']))
VolumeCompr.Param(eval(config['Compr_param']['vol_compr']))
print(f"config['Compr_param']['vol_compr']: {config['Compr_param']['vol_compr']}")
Intake.Param(eval(config['Intake_param']['k_pl_intake']))
VolumeIntake.Param(eval(config['Intake_param']['vol_intake'])+eval(config['Intercooler_param']['vol_ic']))
Injector.Param(eval(control['Engine_ECU']['x_ne']), eval(control['Engine_ECU']['y_pps_qinj']),
                eval(control['Engine_ECU']['z_qinj']))
Engine.Param(eval(config['Engine_param']['vcyl']), eval(config['Engine_param']['x_ne']),
                eval(config['Engine_param']['y_rho1rho2']),
                eval(config['Engine_param']['y_etavol_overall']), eval(config['Engine_param']['z_etavol']),
                eval(config['Engine_param']['z_etaind']), eval(config['Engine_param']['z_etacomb']))
VolumeTurb.Param(eval(config['Outlet_param']['vol_om'])+eval(config['Turbine_param']['vol_turbine']))
Turbine.Param(eval(config['Turbine_param']['preft']), eval(config['Turbine_param']['treft']),
                eval(config['Turbine_param']['x_pr']), eval(config['Turbine_param']['y_vntposition']),
                eval(config['Turbine_param']['z_flowt_cor']), eval(config['Turbine_param']['z_eta_turb'])*1.12)
VolumeExhaust.Param(eval(config['Exhaust_param']['vol_ex']))
Exhaust.Param(eval(config['Exhaust_param']['k_pl_exhaust']))
TurboShaft.Param(eval(config['Compr_param']['inertia'])+eval(config['Turbine_param']['inertia']), 1000)
PI_VNT.Param(eval(control['Engine_ECU']['kp']), eval(control['Engine_ECU']['ki']), eval(control['Engine_ECU']['vnt_min']), eval(control['Engine_ECU']['vnt_max']))

"-----------------------------------------------------------"
"SIMULATION"
"-----------------------------------------------------------"
time_simu[0] = start_simu
incr_save_old = 0
method = 'Trapezoidal'
for i in range(1, int(LastVal + 1)):
    print(i)
    time_simu[i] = i * step_simu + start_simu
    "Pedal position=f(time_simu)"
    N = interpolv(eval(configStep.x_N),
                    eval(configStep.y_N), time_simu[i])
    pps = interpolv(eval(configStep.x_pps),
                    eval(configStep.y_pps), time_simu[i])
    P1E_Ord = interpolm(eval(control['Engine_ECU']['y_pps_qinj']), eval(control['Engine_ECU']['x_ne']),
                        eval(control['Engine_ECU']['z_p1e_ord']), pps, N)
    Kp_VNT = interpolv(eval(control['Engine_ECU']['x_epsilon_kp']),
                    eval(control['Engine_ECU']['y_kp']), P1E_Ord - Engine.E1.P)
    

    "AirFilter"
    print(f"airFilter.E2.h: {AirFilter.E2.h}")
    print(f"airFilter.E2.P: {AirFilter.E2.P}")
    print(f"airFilter.E2.R: {AirFilter.E2.R}")
    print(f"airFilter.E2.T: {AirFilter.E2.T}")
    print(f"volAirFilter.F1.Qm: {VolumeAirFilter.F1.Qm}")
    print(f"volAirFilter.F1.Qmh: {VolumeAirFilter.F1.Qmh}")
    print(f"volAirFilter.F2.Qm: {VolumeAirFilter.F2.Qm}")
    print(f"volAirFilter.F2.Qmh: {VolumeAirFilter.F2.Qmh}")
    print()
    AirFilter.E1 = Ambient_Air.E
    AirFilter.E2 = VolumeAirFilter.E1
    AirFilter.Solve()
    VolumeAirFilter.F1 = AirFilter.F2
    VolumeAirFilter.F2 = Compressor.F1
    VolumeAirFilter.Solve(step_simu, method)
    print(AirFilter.E1)

    "Compressor"
    print(f"compressor.E2.P: {Compressor.E2.P}")
    print(f"compressor.E2.T: {Compressor.E2.T}")
    print(f"compressor.E2.h: {Compressor.E2.h}")
    print(f"volC.F1.Qm: {VolumeCompr.F1.Qm}")
    print(f"volC.F1.Qmh: {VolumeCompr.F1.Qmh}")
    print(f"compressor.E1.gamma: {Compressor.E1.gamma}")
    print(f"compressor.E1.h: {Compressor.E1.h}")
    print(f"compressor.E1.P: {Compressor.E1.P}")
    print(f"compressor.E1.T: {Compressor.E1.T}")
    print(f"compressor.Fm.omega: {Compressor.Fm.omega}")
    print(f"compressor.Fm.N: {Compressor.Fm.N}")
    print(f"volC.F2.Qm: {VolumeCompr.F2.Qm}")
    print(f"volC.F2.Qmh: {VolumeCompr.F2.Qmh}")
    print()
    Compressor.E1 = VolumeAirFilter.E2
    Compressor.E2 = VolumeCompr.E1
    Compressor.Fm = TurboShaft.Fm1 
    Compressor.Solve()
    VolumeCompr.F1 = Compressor.F2
    VolumeCompr.F2 = Intake.F1
    VolumeCompr.Solve(step_simu, method)

    "Engine Intake"
    print(f"Intake.E1.h: {Intake.E1.h}")
    print(f"Intake.E1.P: {Intake.E1.P}")
    print(f"Intake.E1.T: {Intake.E1.T}")
    print(f"Intake.E1.R: {Intake.E1.R}")
    print(f"Intake.E2.h: {Intake.E2.h}")
    print(f"Intake.E2.P: {Intake.E2.P}")
    print(f"Intake.E2.T: {Intake.E2.T}")
    print(f"Intake.E2.R: {Intake.E2.R}")
    print(f"VolumeIntake.F1.Qm: {VolumeIntake.F1.Qm}")
    print(f"VolumeIntake.F1.Qmh: {VolumeIntake.F1.Qmh}")
    print(f"VolumeIntake.F2.Qm: {VolumeIntake.F2.Qm}")
    print(f"VolumeIntake.F2.Qmh: {VolumeIntake.F2.Qmh}")
    print()
    Intake.E1 = VolumeCompr.E2
    Intake.E2 = VolumeIntake.E1
    Intake.Solve()
    VolumeIntake.F1 = Intake.F2
    VolumeIntake.F2 = Engine.F1
    VolumeIntake.Solve(step_simu, method)

    "Engine bloc"
    print(f"engine.E1.h: {Engine.E1.h}")
    print(f"engine.E1.P: {Engine.E1.P}")
    print(f"engine.E1.T: {Engine.E1.T}")
    print(f"engine.E1.R: {Engine.E1.R}")
    print(f"engine.E2.h: {Engine.E2.h}")
    print(f"engine.E2.P: {Engine.E2.P}")
    print(f"engine.E2.T: {Engine.E2.T}")
    print()
    Engine.Fm = FlowM(N / 30 * math.pi)
    Engine.E1 = VolumeIntake.E2
    #Engine.E1 = copy.deepcopy(VolumeIntake.E2)
    Engine.E1.T = 273+40
    Engine.E2 = VolumeTurb.E1
    Injector.Solve(pps, Engine.Fm)
    Engine.Solve()

    "Turbine"
    print(f"turbine.E1.gamma: {Turbine.E1.gamma}")
    print(f"turbine.E1.h: {Turbine.E1.h}")
    print(f"turbine.E1.P: {Turbine.E1.P}")
    print(f"turbine.E1.T: {Turbine.E1.T}")
    print(f"turbine.E2.h: {Turbine.E2.h}")
    print(f"turbine.E2.P: {Turbine.E2.P}")
    print(f"turbine.E2.T: {Turbine.E2.T}")
    print(f"turbine.FAR: {Turbine.FAR}")
    print(f"volumeTurbine.FAR: {VolumeTurb.FAR}")
    print(f"volumeTurbine.F1.Qm: {VolumeTurb.F1.Qm}")
    print(f"volumeTurbine.F1.Qmh: {VolumeTurb.F1.Qmh}")
    print(f"volumeTurbine.F2.Qm: {VolumeTurb.F2.Qm}")
    print(f"volumeTurbine.F2.Qmh: {VolumeTurb.F2.Qmh}")
    print()
    VolumeTurb.F1 = Engine.F2
    VolumeTurb.F2 = Turbine.F1
    VolumeTurb.FAR = Engine.FAR
    VolumeTurb.Solve(step_simu, method)
    Turbine.E1 = VolumeTurb.E2
    #Turbine.E2 = Exhaust.E1
    Turbine.E2 = VolumeExhaust.E1  
    Turbine.FAR = Engine.FAR
    Turbine.Fm = TurboShaft.Fm2 
    Turbine.VNT = PI_VNT.y
    Turbine.Solve()

    "Exhaust"
    print(f"exhaust.E1.h: {Exhaust.E1.h}")
    print(f"exhaust.E1.P: {Exhaust.E1.P}")
    print(f"exhaust.E1.T: {Exhaust.E1.T}")
    print(f"exhaust.E1.R: {Exhaust.E1.R}")
    print(f"volumeExhaust.F2.Qm: {VolumeExhaust.F2.Qm}")
    print(f"volumeExhaust.F2.Qmh: {VolumeExhaust.F2.Qmh}")
    print(f"volumeExhaust.FAR: {VolumeExhaust.FAR}")
    print(f"volumeExhaust.F1.Qm: {VolumeExhaust.F1.Qm}")
    print(f"volumeExhaust.F1.Qmh: {VolumeExhaust.F1.Qmh}")
    print()
    VolumeExhaust.F1 = Turbine.F2
    VolumeExhaust.F2 = Exhaust.F1
    VolumeExhaust.FAR = Engine.FAR
    VolumeExhaust.Solve(step_simu, method)
    Exhaust.E1 = VolumeExhaust.E2
    Exhaust.E2 = Ambient_Air.E
    Exhaust.Solve()

    "Turbo Shaft"
    print(f"turboShaft.Em1.Tq: {TurboShaft.Em1.Tq}")
    print(f"turboShaft.Em2.Tq: {TurboShaft.Em2.Tq}")
    print()
    TurboShaft.Em1 = Compressor.Em
    TurboShaft.Em2 = Turbine.Em
    TurboShaft.Solve(step_simu, method)

    "VNT Control"
    print(f"PI_VNT.x_Act: {PI_VNT.x_Act}")
    print()
    PI_VNT.x_Ord = P1E_Ord
    PI_VNT.x_Act = Engine.E1.P
    PI_VNT.Kp = Kp_VNT*0.25
    PI_VNT.Solve(step_simu, method)

    "-----------------------------------------------------------"
    "Save results according to the defined sample time"
    "-----------------------------------------------------------"
    incr_save = math.floor(i * step_simu / sample_time)
    if incr_save > incr_save_old:
        result_simu[incr_save, 0] = time_simu[i]
        result_simu[incr_save, 1] = Engine.Em.Tq
        result_simu[incr_save, 2] = Engine.F1.Qm * -1
        result_simu[incr_save, 3] = Engine.F2.Qm
        result_simu[incr_save, 4] = Engine.FAR
        result_simu[incr_save, 5] = Engine.E1.P
        result_simu[incr_save, 6] = Engine.E2.P
        result_simu[incr_save, 7] = Engine.E1.T
        result_simu[incr_save, 8] = Turbine.E1.T
        result_simu[incr_save, 9] = Turbine.E2.T
        result_simu[incr_save, 10] = Engine.Fm.N
        result_simu[incr_save, 11] = TurboShaft.Fm1.N
        result_simu[incr_save, 12] = PI_VNT.y
        result_simu[incr_save, 13] = PI_VNT.x_Ord
        result_simu[incr_save, 14] = Compressor.E2.T

    incr_save_old = incr_save

time2 = time.time()
result = round((time2 - time1)*10)/10

plt.figure(1)
plt.subplot(331)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 1],'r')
plt.ylabel('Engine.Em.Tq')

plt.subplot(332)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'r', result_simu[0:incr_save, 0],result_simu[0:incr_save, 3],'g')
plt.ylabel('Engine Massic Flow [kg/s]')

plt.subplot(333)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 4],'r')
plt.ylabel('Engine.FAR')

plt.subplot(334)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 5],'r', result_simu[0:incr_save, 0],result_simu[0:incr_save, 6],'g')
plt.ylabel('Engine Pressure [Pa]')

plt.subplot(335)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 7],'r')
plt.ylabel('Engine Temperature [k]')

plt.subplot(336)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 8],'r', result_simu[0:incr_save, 0],result_simu[0:incr_save, 9],'g')
plt.ylabel('Turbine Temperature [k]')

plt.subplot(337)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 10],'r')
plt.ylabel('Engine.Fm.N')

plt.show()

'''
result_simu['time'] = list(result_simu[0:incr_save, 0])
result_simu['TqE'] = list(result_simu[0:incr_save, 1])
result_simu['Qm1E'] = list(result_simu[0:incr_save, 2])
result_simu['Qm2E'] = list(result_simu[0:incr_save, 3])
result_simu['FAR'] = list(result_simu[0:incr_save, 4])
result_simu['P1E'] = list(result_simu[0:incr_save, 5])
result_simu['P2E'] = list(result_simu[0:incr_save, 6])
result_simu['T1E'] = list(result_simu[0:incr_save, 7])
result_simu['T1T'] = list(result_simu[0:incr_save, 8])
result_simu['T2T'] = list(result_simu[0:incr_save, 9])
result_simu['NE'] = list(result_simu[0:incr_save, 10])
result_simu['NT'] = list(result_simu[0:incr_save, 11])
result_simu['VNT_act'] = list(result_simu[0:incr_save, 12])
result_simu['P1E_ord'] = list(result_simu[0:incr_save, 13])
result_simu['T2C'] = list(result_simu[0:incr_save, 14])
'''
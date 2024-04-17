# SystemCouplingCosimulation

### automatedSimpleEngineModel
- PySystemCoupling
- Automated data transfers
- Explicit
- run.py: Simple Engine Model
- thermalEngineRun.py: Full Thermal Engine Model
- Need to change initial values and solver mode (Euler/Trapezoidal) in RCAirfilter.py/RCCompressor.py for each engine model

### implicitModel
- PySystemCoupling
- Automated data transfers
- Implicict solver to match results from original implementation
- run.py: Simple Engine Model
- thermalEngineRun.py: Full Thermal Engine Model
- Need to change initial values and solver mode (Euler/Trapezoidal) in RCAirfilter.py/RCCompressor.py for each engine model

### pysystemcoupling-simple-engine-model
- PySystemCoupling
- Manual data transfers 
- run.py: Simple Engine Model
- results match original implementation

### syC-auto-simple-engine-model
- System Coupling
- Local copy of \Tests\Cosimulation\cosim-parameters-simple-engine-model
    - cosim-parameters-simple-engine-model more accurate/ updated
- Automatic data transfers
- Explicit
- run.py: Simple Engine Model

### thermalEngineModel
- Python
- first_step.py: Simple Engine Model
- original implementation altered to run locally

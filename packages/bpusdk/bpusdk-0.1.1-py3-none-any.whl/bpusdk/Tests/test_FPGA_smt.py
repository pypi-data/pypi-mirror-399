import os
import sys
import brainpy as bp
current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.SNNCompiler.snn_compiler_FPGA.flow.smt_compiler import SMTCompiler


funcs = {"V": bp.neurons.LIF(256).derivative}

predefined_regs = {
    "V": "R2",
}

cv = {
    "V_reset": -68.,
    "V_th": -30.,
    "V_rest": -65.,
    "tau": 10.,
    "R":1., 
    "tau_ref":5.0
}


i_compiler, v_compiler, smt_result = SMTCompiler.compile_all(
    func=funcs,
    preload_constants=cv,
    predefined_regs=predefined_regs,
    i_func=None,
    update_method=None,
    result_bits=3,
)

all_constants = v_compiler.preload_constants
printed_name = []
register_constants = []
all_constants_tmp = sorted(all_constants, key=lambda r: int(r.name[2:]))
for pc in all_constants_tmp:
    if pc.name not in printed_name:
        printed_name.append(pc.name)
        register_constants.append(pc)

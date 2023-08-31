import random
from uuid import uuid4
from qiskit import transpile
from core.entities import Circuit

DEFAULT_SEED = 123

class QuantumRedundancyChannel:
    def __init__(self, device) -> None:
        self.device = device
        self.id = str(uuid4())

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, QuantumRedundancyChannel):
            return __value.id == self.id
        return False

    def apply(self, circuit):
        transpilation = self.create_variant_of(circuit)
        return Circuit(circuit.id + "_transpiled", transpilation)

    def create_variant_of(self, circuit):
        '''Execute the circuit and return measurements'''
        pass
    
class VaryingTranspilationSeedGeneration(QuantumRedundancyChannel):
    def __init__(self, device) -> None:
        super().__init__(device)
        self.seed = random.randrange(0, 10000)
        self.id = "_".join(["VaryingTranspilationSeedGeneration", device.unique_name, str(self.seed), self.id])
        
    def create_variant_of(self, circuit):
        print("Apply varying transpilation seed channel")
        circuit.qiskit_circuit.name = f"{circuit.id}-{self.seed}"
        return transpile(circuit.qiskit_circuit, 
                         backend=self.device.get_backend(), 
                         seed_transpiler=self.seed)

class HeterogeneousQuantumDeviceBackend(QuantumRedundancyChannel):
    def __init__(self, device) -> None:
        super().__init__(device)
        self.id = "_".join(["HeterogeneousQuantumDeviceBackend", device.unique_name, self.id])

    def create_variant_of(self, circuit):
        print("Apply heterogeneous quantum device channel")
        circuit.qiskit_circuit.name = f"{circuit.id}-{self.device}"
        return transpile(circuit.qiskit_circuit, 
                  backend=self.device.get_backend(), 
                  seed_transpiler=DEFAULT_SEED)

class DifferentOptimizationLevel(QuantumRedundancyChannel):
    def __init__(self, device, opt_level) -> None:
        super().__init__(device)
        self.opt_level = opt_level
        self.id = "_".join(["DifferentOptimizationLevel", device.unique_name, str(opt_level), self.id])

    def create_variant_of(self, circuit):
        print("Apply different optimization level channel")
        circuit.qiskit_circuit.name = f"{circuit.id}-{DEFAULT_SEED}-{self.opt_level}"
        return transpile(circuit.qiskit_circuit, 
                         backend=self.device.get_backend(), 
                         optimization_level=self.opt_level, 
                         seed_transpiler=DEFAULT_SEED)
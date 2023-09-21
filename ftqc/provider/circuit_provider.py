import random
from qiskit.circuit.random import random_circuit
from qiskit.circuit import QuantumCircuit
from core.entities import Circuit
from provider.util import list_files, get_base_name

class CircuitProvider:
    def get(self):
        '''Main method of the provider from which circuits are obtained'''
        pass

class RandomCircuitProvider(CircuitProvider):
    def __init__(self, num_circuits, max_num_qubits = 10, max_depth = 40) -> None:
        self.random_circuits = []
        for i in range(num_circuits):
            circuit = random_circuit(random.randint(2, max_num_qubits), random.randint(5, max_depth), measure=True)
            circuit.name = 'randomcircuit' + str(i)
            self.random_circuits.append(Circuit(circuit.name, circuit))
        
    
    def get(self):
        return self.random_circuits
    
class QasmBasedCircuitProvider(CircuitProvider):
    def __init__(self, dir) -> None:
        self.circuits = {}
        for qasm_file in list_files(dir, extension=".qasm"):
            qiskit_circuit = QuantumCircuit.from_qasm_file(qasm_file)
            name = get_base_name(qasm_file)
            circuit = Circuit(name, qiskit_circuit)

            prefix = name[:name.rfind("_")]
            if prefix not in self.circuits.keys():
                self.circuits[prefix] = []    

            self.circuits[prefix].append(circuit)

    def get(self):
        return [circuit for key in self.circuits.keys() for circuit in self.circuits[key]]
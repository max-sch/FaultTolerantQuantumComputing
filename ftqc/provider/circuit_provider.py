import random
from qiskit.circuit.random import random_circuit
from qiskit.circuit import QuantumCircuit
from core.entities import Circuit
from provider.util import list_files, get_base_name

class CircuitProvider:
    def get(self):
        '''Main method of the provider from which circuits are obtained'''
        pass

class CircuitBatch:
    def __init__(self, size, circuits) -> None:
        self.size = size
        if self.size > 25:
            raise Exception("Batch size must not exceed the size of 25")

        if len(circuits) != size:
            raise Exception("The number of circuits must match the specified batch size.")
        self.circuits = circuits

class RandomCircuitProvider(CircuitProvider):
    def __init__(self, num_circuits, batch_size=25, max_num_qubits = 10, max_depth = 40) -> None:
        self.batch_size = 25 if batch_size >= 25 else batch_size
        self.max_num_qubits = max_num_qubits
        self.max_depth = max_depth
        self.num_batches = (int) (num_circuits / self.batch_size)
        if num_circuits % batch_size != 0:
            self.num_batches += 1
    
    def get(self):
        batches = []
        for i in range(self.num_batches):
            random_circuits = []
            for j in range(self.batch_size):
                circuit = random_circuit(random.randint(2, self.max_num_qubits), random.randint(5, self.max_depth), measure=True)
                random_circuits.append(Circuit('batch{0}_randomcircuit{1}'.format(i,j), circuit))
            
            batches.append(CircuitBatch(self.batch_size, random_circuits))

        return batches
    
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

        self.num_batches = len(self.circuits)

    def get(self):
        return [CircuitBatch(len(self.circuits[key]), self.circuits[key]) for key in self.circuits.keys()]
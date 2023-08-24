import random
from qiskit.circuit.random import random_circuit
from core.entities import Circuit


class CircuitProvider:
    def __init__(self, num_circuits, batch_size = 25) -> None:
        self.batch_size = batch_size
        self.num_batches = (int) (num_circuits / (25 if batch_size >= 25 else batch_size))

    def get(self):
        '''Main method of the provider from which circuits are obtained'''
        pass

class CircuitBatch:
    def __init__(self, size, circuits) -> None:
        self.size = size

        if len(circuits) != size:
            raise Exception("The number of circuits must match the specified batch size.")
        self.circuits = circuits

class RandomCircuitProvider(CircuitProvider):
    def __init__(self, num_circuits, batch_size=25, max_num_qubits = 10, max_depth = 40) -> None:
        super().__init__(num_circuits, batch_size)
        self.max_num_qubits = max_num_qubits
        self.max_depth = max_depth
    
    def get(self):
        batches = []
        for i in range(self.num_batches):
            random_circuits = []
            for j in range(self.batch_size):
                circuit = random_circuit(random.randint(2, self.max_num_qubits), random.randint(5, self.max_depth), measure=True)
                random_circuits.append(Circuit('batch{0}_randomcircuit{1}'.format(i,j), circuit))
            
            batches.append(CircuitBatch(self.batch_size, random_circuits))

        return batches
import numpy as np
from mqt.bench import get_benchmark
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke, FakeProvider, FakeBoeblingenV2, FakeAlmadenV2
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit import transpile
from qiskit_aer.noise import (NoiseModel, QuantumError, ReadoutError,
    pauli_error, depolarizing_error, thermal_relaxation_error)
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

#print(FakeProvider().backends())


# Example error probabilities
p_reset = 0.3
p_meas = 0.1
p_gate1 = 0.001

# QuantumError objects
error_reset = pauli_error([('X', p_reset), ('I', 1 - p_reset)])
error_meas = pauli_error([('X',p_meas), ('I', 1 - p_meas)])
error_gate1 = pauli_error([('X',p_gate1), ('I', 1 - p_gate1)])
error_gate2 = error_gate1.tensor(error_gate1)

# Add errors to noise model
noise_bit_flip = NoiseModel()
noise_bit_flip.add_all_qubit_quantum_error(error_reset, "reset")
noise_bit_flip.add_all_qubit_quantum_error(error_meas, "measure")
noise_bit_flip.add_all_qubit_quantum_error(error_gate1, ["u1", "u2", "u3"])
noise_bit_flip.add_all_qubit_quantum_error(error_gate2, ["cx"])


#print(noise_bit_flip)
backend1 = FakeBoeblingenV2()
backend2 = FakeAlmadenV2()
#backend1 = AerSimulator(noise_model = noise_bit_flip)
#backend2 = AerSimulator(noise_model = noise_bit_flip)
#noise = backend1._get_noise_model_from_backend_v2()

for i in range(5, 15):
    for _ in range(10):
        circuit = get_benchmark("dj", "alg", i)
        tc = transpile(circuit, backend=backend1)
        job = backend1.run(tc)
        counts1 = job.result().get_counts()
        tc = transpile(circuit, backend=backend2)
        job = backend2.run(tc)
        counts2 = job.result().get_counts()
        max_keyA = int(max(counts1, key=counts1.get), 2)
        max_keyB = int(max(counts2, key=counts2.get), 2)
        circuit.remove_final_measurements(inplace=True)
        v = Statevector(circuit).probabilities()
        print(v)
        max_correct = np.argmax(v)
        if not (max_keyB == max_keyA):
            print(max_correct)
            print(max_keyA)
            print(max_keyB)
            print()

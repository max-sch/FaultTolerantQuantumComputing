import numpy as np
from math import log2
from core.entities import QuantumComputerSimulator

def simulate(batch):
    return [simulate_and_retrieve_best_solution(c) for c in batch]

def simulate_and_retrieve_best_solution(circuit):
    result = QuantumComputerSimulator.create_perfect_simulator().execute(circuit)
    stv = result.get_statevector(circuit.qiskit_circuit, decimals=3)
    probs = stv.probabilities()
    bestIdxs = np.argwhere(probs == np.amax(probs)).flatten().tolist()
    n = (int)(log2(len(probs)))
    getbinary = lambda x, n: format(x, 'b').zfill(n)
    return [getbinary(i, n) for i in bestIdxs]

def determine_position(correct_state, measurements):
    pos = 0
    for state in measurements.rank().keys():
        if state == correct_state:
            return pos
        else:
            pos += 1

    raise Exception("The measurements do not include " + correct_state)


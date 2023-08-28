import numpy as np
import json
from datetime import datetime
from math import log2
from os import mkdir
from os.path import join, exists
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

def save_results(results, result_dir, file_name = None):
    if not exists(result_dir):
        mkdir(result_dir)

    if file_name is None:
        name = "results_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".json"
        file_name = join(result_dir, name)

    with open(file_name, "w") as json_file:
        results_json = []
        for result in results:
            results_json.append(result.to_json())
            json_file.write(results_json)

    print("Results have been written to file: " + file_name)


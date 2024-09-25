import numpy as np
import json
from datetime import datetime
from math import log2
from os import mkdir
from os.path import join, exists
from core.entities import QuantumComputerSimulator
from qiskit.quantum_info import Statevector  
from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit_aer import Aer 
from qiskit import transpile

def simulate(batch):
    return [simulate_wihtout_error(c) for c in batch]

def circuit_with_measurements(circuit):
    l = []
    for o in circuit.data:
        if o.name == 'measure':
            for qb in o.qubits:
                l.append(circuit.find_bit(qb).index)
    return l

def simulate_wihtout_error(circuit):
    #result = QuantumComputerSimulator.create_perfect_simulator().execute(circuit)
    #print(circuit.qiskit_circuit)
    #print(circuit.qiskit_circuit.data)
    measuredQubits = circuit_with_measurements(circuit.qiskit_circuit)
    backend = Aer.get_backend('statevector_simulator')
    c = transpile(circuit.qiskit_circuit, backend)
    stv = backend.run(c, shots=1).result().get_statevector()
    probs = stv.probabilities(measuredQubits)
    return probs

def determine_position(correct_states, measurements):
    max_count = 0
    for correct_state in correct_states:
        count = measurements.get_count_for(correct_state)
        if count >= max_count:
            best_state = correct_state
            max_count = count
    
    pos = 0
    for state in measurements.rank().keys():
        if state == best_state:
            return pos
        else:
            pos += 1

    return 2 ** len(best_state)

def load_results(result_file, hook):
    with open(result_file, "r") as json_file:
        json_file_content = json_file.read()
        return json.loads(json_file_content, object_hook=hook)

def save_results(results, result_dir, json_encoder, file_name = None):
    if not exists(result_dir):
        mkdir(result_dir)

    if file_name is None:
        name = "results_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".json"
        file_name = join(result_dir, name)

    with open(file_name, "w") as json_file:
        json_results = json.dumps(results, sort_keys=True, indent=4, cls=json_encoder)
        json_file.write(json_results)

    print("Results have been written to file: " + file_name)

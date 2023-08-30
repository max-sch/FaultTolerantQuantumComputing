from qiskit import Aer, execute
from qiskit.providers.aer.noise import NoiseModel
from qiskit.circuit import QuantumCircuit
from qiskit.exceptions import QiskitError
from itertools import groupby

class Circuit:
    def __init__(self, id, qiskit_circuit) -> None:
        self.id = id

        if not isinstance(qiskit_circuit, QuantumCircuit):
            raise Exception("Only qiskit circuits are supported")
        self.qiskit_circuit = qiskit_circuit
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Circuit):
            return self.id == __value.id
        return False

class Measurements:
    def __init__(self, generated_from_channel, measurements) -> None:
        self.generated_from_channel = generated_from_channel
        self.measurements = measurements

    def get_measured_states(self):
        return self.measurements.keys()
    
    def get_count_for(self, state):
        if state not in self.get_measured_states():
            return 0.0
        return self.measurements[state]
    
    #rank in descending order
    def rank(self):
        return {k: v for k, v in sorted(self.measurements.items(), key=lambda item: item[1], reverse=True)}

class QuantumDevice:
    def __init__(self, unique_name, shots) -> None:
        self.unique_name = unique_name
        self.shots = shots

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, QuantumDevice):
            return self.unique_name == __value.unique_name
        return False
    
    def __hash__(self) -> int:
        return hash(self.unique_name)
    
    def __str__(self) -> str:
        return self.unique_name
    
    def get_backend(self):
        '''Returns the backend of the device'''
        pass

    def execute(self, circuit):
        '''Executes a qiskit circuit on the device'''
        pass

    def execute_batch(self, circuits):
        '''Executes a batch of qiskit circuits on the device'''
        pass

class QuantumComputerSimulator(QuantumDevice):
    def __init__(self, simulator, noise_model_backend=None, shots=None) -> None:
        super().__init__(simulator.name() if noise_model_backend == None else simulator.name() + "_" + noise_model_backend.name(), shots=shots)
        self.simulator = simulator
        self.noise_model = NoiseModel.from_backend(noise_model_backend, warnings=False) if noise_model_backend != None else None
        self.shots = shots

    def create_perfect_simulator():
        simulator = Aer.get_backend('statevector_simulator')
        return QuantumComputerSimulator(simulator)
    
    #TODO: check whether this can be achieved by just using fake providers for IBMQuantumComputer
    def create_noisy_simulator(backend, shots=1024):
        simulator = Aer.get_backend('qasm_simulator')
        return QuantumComputerSimulator(simulator, noise_model_backend=backend, shots=shots)
    
    def get_backend(self):
        return self.simulator

    def execute(self, circuit):
        job = execute(circuit.qiskit_circuit, self.simulator, shots=self.shots, noise_model=self.noise_model)
        return job.result()
    
    def execute_batch(self, circuits):
        qiskit_circuits = [c.qiskit_circuit for c in circuits]
        job = execute(qiskit_circuits, self.simulator, shots=self.shots, noise_model=self.noise_model)
        return job.result()
    
class IBMQuantumComputer(QuantumDevice):
    def __init__(self, backend, shots=4096) -> None:
        super().__init__(backend.name(), shots=shots)
        self.backend = backend
        self.shots = shots

    def execute(self, circuit):
        job = execute(circuit.qiskit_circuit, self.backend, shots=self.shots)
        return job.result()

    def execute_batch(self, circuits):
        qiskit_circuits = [c.qiskit_circuit for c in circuits]
        job = execute(qiskit_circuits, self.backend, shots=self.shots)
        return job.result()
    
    def get_backend(self):
        return self.backend

class FaultTolerantQuantumContainer:
    def __init__(self, id, channels, measurement_aggregator) -> None:
        self.id = id
        self.channels = channels
        self.measurement_aggregator = measurement_aggregator

    def aggregate(self, measurements):
        return self.measurement_aggregator(measurements)

    def broadcast_and_apply(self, circuit):
        return [channel.apply(circuit) for channel in self.channels]
    
    def get_devices(self):
        return {c.device for c in self.channels}
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, FaultTolerantQuantumContainer):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)
    
class QuantumContainerOrchestrator:
    def __init__(self, qcontainers) -> None:
        self.orchestrated_containers = set(qcontainers)
        self.aggregated_results = []

    def get_result_for(self, circuit, container):
        for entry in self.aggregated_results:
            if entry[0] == circuit and entry[1] == container:
                return (entry[2], entry[3])
        
        raise Exception("There is no result for container {0} with circuit {1}".format(container.id, circuit.id))

    def orchestrate_executions(self, circuit_batch):
        orchestrations, partitioned_circuits = self.create_orchestrations_and_partitions(circuit_batch)
        executions_results = self.execute(partitioned_circuits)
        self.aggregate_results(orchestrations, executions_results)

    def create_orchestrations_and_partitions(self, circuit_batch):
        orchestrations = []
        partitioned_circuits = {device:[] for c in self.orchestrated_containers for device in c.get_devices()}
        for circuit in circuit_batch.circuits:
            for container in self.orchestrated_containers:
                transpiled_circuits = {}
                for channel in container.channels:
                    transpiled_circuit = channel.apply(circuit)
                    transpiled_circuits[channel] = transpiled_circuit
                    partitioned_circuits[channel.device].append(transpiled_circuit)

                orchestrations.append((circuit, container, transpiled_circuits))
        return (orchestrations, partitioned_circuits)
    
    def execute(self, partitioned_circuits):
        return {device:device.execute_batch(circuits) for device, circuits in partitioned_circuits.items()}

    def aggregate_results(self, orchestrations, executions_results):
        for orch in orchestrations:
            original_circuit = orch[0]
            container = orch[1]
            transpiled_circuits = orch[2]
            
            measurements = []
            for channel, t_circuit in transpiled_circuits.items():
                try:
                    measurement = executions_results[channel.device].get_counts(t_circuit.qiskit_circuit)
                except QiskitError:
                    raise Exception("There are no measurements for circuit: " + t_circuit.id)

                measurements.append(Measurements(channel, measurement))
            
            aggregate = container.aggregate(measurements)
            self.aggregated_results.append((original_circuit, container, aggregate, measurements))
import numpy as np
from qiskit.providers.basic_provider import BasicSimulator
from mqt.bench import get_benchmark
from core.qerror_detection import QuantumFaultDetector, MeasurementNoiseQuantifier
from qiskit import transpile

class RunConfiguration:
    def __init__(self) -> None:
        pass

    def execute(self, circuit, shots=1024):
        circuit = transpile(circuit, self.backend)
        job = self.backend.run(circuit, shots=shots)
        return job.result().get_counts()

class DefaultRunConfiguration(RunConfiguration):
    def __init__(self) -> None:
        super().__init__()
        self.backend = BasicSimulator()

class QuantumSwitch():
    def __init__(self, main_run_configuration, alternative, fault_detector, exepected_dist) -> None:
        self.main_run_configuration = main_run_configuration
        self.alternative = alternative
        self.fault_detector = fault_detector
        self.expected_dist = exepected_dist

    def execute(self, circuit):
        counts = [self.get_probabilities(self.main_run_configuration.execute(circuit))]
        if (self.fault_detector.reject(counts, self.expected_dist.probs)):
            print("detected fault")
            return self.alternative.execute(circuit)
        else:
            print("no fault detected")
            return counts

    def get_probabilities(self, counts):
        total = sum(counts.values())
        return np.fromiter(counts.values(), dtype=float)/total

class Distribution():
    def __init__(self) -> None:
        pass

class EquiDist(Distribution):
    def __init__(self, m) -> None:
        super().__init__()
        self.probs = np.full((m, ), 1/m)

class DiracDist(Distribution):
    def __init__(self):
        super().__init__()
        self.probs = np.array([1.0])



def run_experiment():
    qiskit_circuit = get_benchmark(benchmark_name="grover-noancilla", level="alg", circuit_size=5)

    qs = QuantumSwitch(DefaultRunConfiguration(), DefaultRunConfiguration(), MeasurementNoiseQuantifier.using_hellinger(0.1), EquiDist(1))
    qs.execute(qiskit_circuit)

if __name__ == "__main__":
    run_experiment()


from provider.qdevice_provider import FakeQuantumDeviceProvider
from provider.circuit_provider import CircuitProvider
from builder.ft_builder import CombinerPatternBuilder
from core.entities import Circuit
from core.qchannels import VaryingTranspilationSeedGeneration, HeterogeneousQuantumDeviceBackend, DifferentOptimizationLevel
from experiment.ftqc_experiment import FaultTolerantQCExperiment
from qiskit.circuit.random import random_circuit

class SingleCircuitProvider(CircuitProvider):
    def __init__(self, circuit) -> None:
        self.circuit = circuit
    
    def get(self):
        return [Circuit(self.circuit.name, self.circuit)]

if __name__ == '__main__':
    device_provider = FakeQuantumDeviceProvider()

    builder = CombinerPatternBuilder("DemoCombiner")
    for i in range(2):
        builder.add_channel(VaryingTranspilationSeedGeneration(device_provider.default_device))
        builder.add_channel(DifferentOptimizationLevel(device_provider.default_device, i))
    for device in device_provider.provided_devices():
        if device.unique_name == 'fake_brooklyn' or device.unique_name == 'fake_manhattan':
            builder.add_channel(HeterogeneousQuantumDeviceBackend(device))
    builder.combine_measurements_uniformly()
    combiner = builder.build()

    circuit = random_circuit(3, 6, measure=True)
    circuit_provider = SingleCircuitProvider(circuit)

    ftqc_exp = FaultTolerantQCExperiment(circuit_provider, device_provider, [combiner])
    result = ftqc_exp.run_experiment()[0]

    print(result.ft_qcontainer)
    print(str(result.ground_truth))
    print(str(result.agg_measurements.measurements))
    for m in result.single_measurements:
        print(str(m.measurements))

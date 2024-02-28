from builder.ft_builder import CombinerPatternBuilder, SparingPatternBuilder, ConformalMeasurementsBuilder
from core.qchannels import DifferentOptimizationLevel, HeterogeneousQuantumDeviceBackend, VaryingTranspilationSeedGeneration
from core.qerror_detection import MeasurementNoiseQuantifier, MeasurementComparison
from core.qswitches import SimpleQuantumRedundancySwitch
from provider.qdevice_provider import FakeQuantumDeviceProvider

def build_patterns(params, device_provider):
    patterns = []

    builder = CombinerPatternBuilder("C_seed")
    for _ in range(params["transpilations"]):
        builder.add_channel(VaryingTranspilationSeedGeneration(device_provider.default_device))
    builder.combine_measurements_uniformly()
    pattern = builder.build()

    patterns.append(pattern)

    builder = CombinerPatternBuilder("C_back")
    for device in device_provider.provided_devices():
        builder.add_channel(HeterogeneousQuantumDeviceBackend(device))
    builder.combine_measurements_uniformly()
    pattern = builder.build()

    patterns.append(pattern)

    builder = CombinerPatternBuilder("C_opt")
    for i in range(params["num_opt_level"]):
        builder.add_channel(DifferentOptimizationLevel(device_provider.default_device, i))
    builder.combine_measurements_uniformly()
    pattern = builder.build()

    patterns.append(pattern)

    builder = CombinerPatternBuilder("C_hyb")
    for _ in range(2):
        builder.add_channel(VaryingTranspilationSeedGeneration(device_provider.default_device))
    builder.add_channel(DifferentOptimizationLevel(device_provider.default_device, 1))
    builder.add_channel(DifferentOptimizationLevel(device_provider.default_device, 2))
    for device in device_provider.provided_devices():
        if device.unique_name == 'fake_brooklyn' or device.unique_name == 'fake_manhattan':
            builder.add_channel(HeterogeneousQuantumDeviceBackend(device))
    builder.combine_measurements_uniformly()
    pattern = builder.build()

    patterns.append(pattern)

    builder = SparingPatternBuilder("S_noise")
    builder.with_operational(HeterogeneousQuantumDeviceBackend(device_provider.default_device))
    for _ in range(2):
        builder.and_spare(VaryingTranspilationSeedGeneration(device_provider.default_device))
    for device in device_provider.provided_devices():
        if device.unique_name == 'fake_brooklyn':
            builder.and_spare(HeterogeneousQuantumDeviceBackend(device))
    builder.and_spare(DifferentOptimizationLevel(device_provider.default_device, 1))
    builder.and_spare(DifferentOptimizationLevel(device_provider.default_device, 2))
    builder.using_single_error_detection(MeasurementNoiseQuantifier.using_hellinger(0.1))
    builder.using_quantum_switch(SimpleQuantumRedundancySwitch())
    pattern = builder.build()

    patterns.append(pattern)

    builder = SparingPatternBuilder("S_com")
    channel_primary = VaryingTranspilationSeedGeneration(device_provider.default_device)
    channel_comparator = DifferentOptimizationLevel(device_provider.default_device, 0)
    builder.with_operational(channel_primary, channel_comparator, MeasurementComparison(channel_primary, channel_comparator))
    for i in range(1, 4):
        channel_primary = VaryingTranspilationSeedGeneration(device_provider.default_device)
        channel_comparator = DifferentOptimizationLevel(device_provider.default_device, i)
        builder.and_spare(channel_primary, channel_comparator, MeasurementComparison(channel_primary, channel_comparator))
    for device in device_provider.provided_devices():
        if device.unique_name == 'fake_brooklyn' or device.unique_name == 'fake_manhattan':
            channel_primary = VaryingTranspilationSeedGeneration(device_provider.default_device)
            channel_comparator = HeterogeneousQuantumDeviceBackend(device)
            builder.and_spare(channel_primary, channel_comparator, MeasurementComparison(channel_primary, channel_comparator))
    builder.using_quantum_switch(SimpleQuantumRedundancySwitch())
    pattern = builder.build()

    patterns.append(pattern)

    builder = ConformalMeasurementsBuilder("M_seed")
    for _ in range(4):
        builder.add_channel(VaryingTranspilationSeedGeneration(device_provider.default_device))
    builder.default_conformity()
    pattern = builder.build()

    patterns.append(pattern)

    builder = ConformalMeasurementsBuilder("M_hyb")
    builder.add_channel(VaryingTranspilationSeedGeneration(device_provider.default_device))
    builder.add_channel(DifferentOptimizationLevel(device_provider.default_device, 1))
    for device in device_provider.provided_devices():
        if device.unique_name == 'fake_brooklyn':
            builder.add_channel(HeterogeneousQuantumDeviceBackend(device))
    builder.default_conformity()
    pattern = builder.build()

    patterns.append(pattern)

    return patterns
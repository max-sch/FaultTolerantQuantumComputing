from builder.ft_builder import CombinerPatternBuilder
from core.qchannels import DifferentOptimizationLevel, HeterogeneousQuantumDeviceBackend, VaryingTranspilationSeedGeneration
from provider.qdevice_provider import FakeQuantumDeviceProvider
from provider.circuit_provider import RandomCircuitProvider
from experiment.ftqc_experiment import FaultTolerantQCExperiment
from expsuite import PyExperimentSuite



class FtqcExperimentSuite(PyExperimentSuite):
    def reset(self, params, rep):
        print("Start initializing the experiment")

        self.results_dir = params["outputdir"]

        device_provider = FakeQuantumDeviceProvider()
        #device_provider = QuantumDeviceProvider(params["backend"])
        #device_provider = QuantumDeviceProvider(params["backend"], IBMQCredentials(params["apitoken"], params["apiurl"])

        builder = CombinerPatternBuilder("VaryingTranspilationSeedCombiner")
        for _ in range(params["transpilations"]):
            builder.add_channel(VaryingTranspilationSeedGeneration(device_provider.default_device))
        builder.combine_measurements_uniformly()
        varying_transpilation_seed_container = builder.build()

        builder = CombinerPatternBuilder("HeterogeneousQuantumDeviceBackendCombiner")
        for device in device_provider.provided_devices():
            builder.add_channel(HeterogeneousQuantumDeviceBackend(device))
        builder.combine_measurements_uniformly()
        heterogeneous_device_container = builder.build()

        builder = CombinerPatternBuilder("DifferentOptimizationLevelCombiner")
        for i in range(params["num_opt_level"]):
            builder.add_channel(DifferentOptimizationLevel(device_provider.default_device, i))
        builder.combine_measurements_uniformly()
        different_opt_level_container = builder.build()

        c_provider = RandomCircuitProvider(4, batch_size=2, max_num_qubits=3, max_depth=10)
        self.ftqc_exp = FaultTolerantQCExperiment(varying_transpilation_seed_container,
                                        heterogeneous_device_container,
                                        different_opt_level_container,
                                        circuit_provider=c_provider)

    def iterate(self, params, rep, n):
        print('Start running the experiment')

        exp_results = self.ftqc_exp.run_experiment()
        self.ftqc_exp.save(exp_results, self.results_dir)
        eval_results = self.ftqc_exp.evaluate(exp_results, self.results_dir)

        ret = {"rep": rep, "iter": n, "eval_results": eval_results}
        return ret


if __name__ == '__main__':
    FtqcExperimentSuite().start()

    




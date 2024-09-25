from provider.qdevice_provider import QuantumDeviceProvider, FakeQuantumDeviceProvider, HybridQuantumDeviceProvider 
from provider.circuit_provider import QasmBasedCircuitProvider, RandomCircuitProvider
from pattern_definition import build_patterns, build_some_patterns
from experiment.ftqc_experiment import FaultTolerantQCExperiment
from expsuite import PyExperimentSuite

from builder.ft_builder import ConformalMeasurementsBuilder, CombinerPatternBuilder
from core.qchannels import VaryingTranspilationSeedGeneration, DifferentOptimizationLevel, HeterogeneousQuantumDeviceBackend
from core.entities import Measurements

class FtqcExperimentSuite(PyExperimentSuite):
    def __init__(self):
        super().__init__() 
        self.options.ncores = 1
    
    def reset(self, params, rep):
        print("Start initializing the experiment")

        ibmq_credentials = IBMQCredentials(api_token='api_token', api_url='api_url', instance='instance')
        device_provider = HybridQuantumDeviceProvider(ibmq_credentials)

        patterns = build_some_patterns(params, device_provider)        

        #circuit_provider = RandomCircuitProvider(1, max_num_qubits=10, max_depth=40)
        circuit_provider = QasmBasedCircuitProvider(params["qasm_dir"])

        self.ftqc_exp = FaultTolerantQCExperiment(circuit_provider, device_provider, patterns)

    def iterate(self, params, rep, n):
        print('Start running the experiment')

        results_dir = params["outputdir"]

        try:
            result_file = params["result_file"]
        except:
            result_file = None

        if result_file == None:
            exp_results = self.ftqc_exp.run_experiment()
            self.ftqc_exp.save(exp_results, results_dir)
        else:
            exp_results = self.ftqc_exp.load_from(result_file)
            exp_results = [result for result in exp_results if result.agg_measurements.accepted]

        eval_results = self.ftqc_exp.evaluate(exp_results, results_dir)

        return {"rep": rep, "iter": n, "eval_results": eval_results}

def manual_run():
    print("Start initializing the experiment")
    params = dict()
    params["qasm_dir"] = "DJ"
    params["backend"] = "ibmq_ehningen"
    params["outputdir"] = "results"
    params["qasm_dir"] = "DJ"
    params["num_opt_level"] = 4
    params["amount"] = 3
    params["printlatex"] = False
    params["filter"] = None
    params["transpilations"] = 9
    params["showplot"] = True
    params["simulate"] = True
    params["iterations"] = 1

    #ibmq_credentials = IBMQCredentials(api_token='api_token', api_url='api_url', instance='instance')
    ibmq_credentials = None
    device_provider = HybridQuantumDeviceProvider(ibmq_credentials)

    patterns = build_some_patterns(params, device_provider)        

    #circuit_provider = RandomCircuitProvider(1, max_num_qubits=10, max_depth=40)
    #circuit_provider = QasmBasedCircuitProvider(params["qasm_dir"])
    circuit_provider = MQTCircuitProvider()

    ftqc_exp = FaultTolerantQCExperiment(circuit_provider, device_provider, patterns)

    for i in range(params["iterations"]):
        print('Start running the experiment')

        results_dir = params["outputdir"]

        try:
            result_file = params["result_file"]
        except:
            result_file = None

        if result_file == None:
            exp_results = ftqc_exp.run_experiment()
            ftqc_exp.save(exp_results, results_dir)
        else:
            exp_results = ftqc_exp.load_from(result_file)
            exp_results = [result for result in exp_results if result.agg_measurements.accepted]

        eval_results = ftqc_exp.evaluate(exp_results, results_dir)

        print( {"iter": i, "eval_results": eval_results})

if __name__ == '__main__':
    #FtqcExperimentSuite().start()
    manual_run()

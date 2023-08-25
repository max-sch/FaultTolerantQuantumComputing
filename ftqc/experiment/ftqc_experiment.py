from provider.circuit_provider import CircuitProvider, RandomCircuitProvider
from core.entities import QuantumContainerOrchestrator, Measurements
from experiment.util import simulate_and_retrieve_best_solution

class FaultTolerantQCExperiment:
    def __init__(self, *ft_qcontainers, circuit_provider = RandomCircuitProvider(500)):
        self.ft_qcontainers = list(ft_qcontainers)
        # TODO: check whether the provider can also be passed by params, i.e., params["circuit_provider"]
        self.circuit_provider: CircuitProvider = circuit_provider

    def run_experiment(self):
        results = []
        for batch in self.circuit_provider.get():
            orch_result = QuantumContainerOrchestrator(self.ft_qcontainers)
            orch_result.orchestrate_executions(batch)
            for circuit in batch.circuits:
                ground_truth = simulate_and_retrieve_best_solution(circuit)
                for qcontainer in self.ft_qcontainers:
                    agg_measurements = orch_result.get_result_for(circuit, qcontainer)
                    results.append(ExperimentResult(qcontainer, ground_truth, agg_measurements))
        return results
    
    def save(self, results, results_dir):
        pass

    def process_and_visualize(self, results):
        pass

class ExperimentResult:
    def __init__(self, ft_qcontainer, ground_truth, agg_measurements) -> None:
        self.ft_qcontainer = ft_qcontainer.id
        self.ground_truth = ground_truth
        self.agg_measurements = agg_measurements
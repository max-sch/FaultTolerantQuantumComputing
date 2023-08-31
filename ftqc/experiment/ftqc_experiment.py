import json
from provider.circuit_provider import CircuitProvider, RandomCircuitProvider
from core.entities import QuantumContainerOrchestrator
from experiment.util import simulate_and_retrieve_best_solution, determine_position, save_results
from evaluation.exp_eval import FtqcExperimentEvaluator

class FaultTolerantQCExperiment:
    def __init__(self, *ft_qcontainers, circuit_provider = RandomCircuitProvider(500)):
        self.ft_qcontainers = list(ft_qcontainers)
        self.circuit_provider: CircuitProvider = circuit_provider

    def run_experiment(self):
        results = []
        for batch in self.circuit_provider.get():
            orch_result = QuantumContainerOrchestrator(self.ft_qcontainers)
            orch_result.orchestrate_executions(batch)
            for circuit in batch.circuits:
                ground_truth = simulate_and_retrieve_best_solution(circuit)
                for qcontainer in self.ft_qcontainers:
                    aggregated, single = orch_result.get_result_for(circuit, qcontainer)
                    results.append(ExperimentResult(qcontainer, ground_truth, aggregated, single))
        return results
    
    def save(self, results, result_dir):
        save_results(results, result_dir)

    def evaluate(self, results):
        FtqcExperimentEvaluator(results).evaluate()

class ExperimentResult:
    def __init__(self, ft_qcontainer, ground_truth, agg_measurements, single_measurements) -> None:
        self.ft_qcontainer = ft_qcontainer.id
        self.ground_truth = ground_truth
        self.agg_measurements = agg_measurements
        self.single_measurements = single_measurements

    def avg_postion(self):
        '''Determines the average position of the correct state in the indivdual (non-combined) measurements'''
        positions = [determine_position(self.ground_truth, measurements) for measurements in self.single_measurements]
        return sum(positions) / len(positions)

    def position_of_closest(self):
        '''Determines the position of the an individual measurements closest to the correct state'''
        pos = None
        for measurements in self.single_measurements:
            pos = determine_position(self.ground_truth, measurements)
            if pos == 0:
                return pos
        return pos          

    def position_of_agg(self):
        '''Determines the position of the aggregated measurements'''
        return determine_position(self.ground_truth, self.agg_measurements)
    
    def to_json(self, encoder=json.JSONEncoder):
        return json.dumps(self, sort_keys=True, indent=4, cls=encoder)
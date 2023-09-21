import json
import re
import math
from typing import Any
from core.entities import QuantumContainerOrchestrator, Measurements
from core.qchannels import QuantumRedundancyChannel
from experiment.util import simulate_and_retrieve_best_solution, determine_position, save_results, load_results
from evaluation.exp_eval import FtqcExperimentEvaluator

class FaultTolerantQCExperiment:
    def __init__(self, circuit_provider, qdevice_provider, ft_qcontainers):
        self.ft_qcontainers = ft_qcontainers
        self.circuit_provider = circuit_provider
        self.qdevice_provider = qdevice_provider

    def run_experiment(self):
        results = []
        
        orch_result = QuantumContainerOrchestrator(self.ft_qcontainers, self.qdevice_provider)
        orch_result.orchestrate_executions(self.circuit_provider)
        for circuit in self.circuit_provider.get():
            ground_truth = simulate_and_retrieve_best_solution(circuit)
            for qcontainer in self.ft_qcontainers:
                aggregated, single = orch_result.get_result_for(circuit, qcontainer)
                results.append(ExperimentResult(qcontainer.id, ground_truth, aggregated, single))
        
        return results
    
    def save(self, results, result_dir):
        save_results(results, result_dir, ExperimentResult.JSONEncoder)

    def load_from(self, result_file):
        return load_results(result_file, ExperimentResult.from_json)

    def evaluate(self, results, result_dir):
        FtqcExperimentEvaluator(results, result_dir).evaluate()

class ExperimentResult:
    class JSONEncoder(json.JSONEncoder):
            def default(self, o: Any) -> Any:
                if isinstance(o, QuantumRedundancyChannel):
                    return o.id
                
                return o.__dict__

    def __init__(self, ft_qcontainer_id, ground_truth, agg_measurements, single_measurements, top_ten_size=None) -> None:
        self.ft_qcontainer = ft_qcontainer_id
        self.ground_truth = ground_truth
        self.agg_measurements = agg_measurements
        self.single_measurements = single_measurements
        self.top_ten_size = top_ten_size if top_ten_size != None else self._top_ten_size()

    def avg_postion(self):
        '''Determines the average position of the correct state in the indivdual (non-aggregated) measurements'''
        positions = [determine_position(self.ground_truth, measurements) for measurements in self.single_measurements]

        avg_pos = sum(positions) / len(positions)
        return round(avg_pos)
    
    def position_of_closest(self):
        '''Determines the position of closest state vector to the correct state'''
        closest = len(self.single_measurements[0].measurements)
        for measurements in self.single_measurements:
            pos = determine_position(self.ground_truth, measurements)
            if pos < closest:
                closest = pos
            if pos == 0:
                break

        return closest          

    def position_of_agg(self):
        '''Determines the position of the aggregated measurements'''
        return determine_position(self.ground_truth, self.agg_measurements)
    
    def _top_ten_size(self):
        '''Determines the size of the top ten'''
        return max(math.ceil(len(self.single_measurements) * 0.1), 3)
    
    def from_json(json_dct):
        if all(re.fullmatch("[01]+", key) for key in json_dct.keys()):
            return json_dct            

        if "generated_from_channel" in json_dct.keys():
            return Measurements(json_dct["generated_from_channel"], 
                                json_dct["measurements"], 
                                json_dct["accepted"])
        
        if "ft_qcontainer" in json_dct.keys():
            return ExperimentResult(json_dct["ft_qcontainer"],
                                    json_dct["ground_truth"],
                                    json_dct["agg_measurements"],
                                    json_dct["single_measurements"],
                                    json_dct["top_ten_size"])
        
        raise TypeError("There is no proper type for " + json_dct)
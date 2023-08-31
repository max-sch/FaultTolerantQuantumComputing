from enum import Enum
from evaluation.metrics import NumberOfCorrectCircuits, NumberOfTopTenCircuits, DirectComparison
import pandas as pd
from tabulate import tabulate
import datetime

class Approach(Enum):
    VARYING_TRANSPILATION_SEED = "VaryingTranspilationSeedCombiner"
    BACKEND = "HeterogeneousQuantumDeviceBackendCombiner"
    DIFFERENT_OPTIMIZATION_LEVEL = "DifferentOptimizationLevelCombiner"

class ApproachResult:
    def __init__(self, results_for_approach, approach):
        self.results = results_for_approach
        self.approach = approach
        self.num_correct_evaluator = NumberOfCorrectCircuits()
        self.num_top_ten_evaluator = NumberOfTopTenCircuits()
        self.direct_comparison_evaluator = DirectComparison()
        
    def evaluate(self):
        avg_pos_results = [result.avg_postion() for result in self.results]
        agg_pos_results = [result.position_of_closest() for result in self.results]
        fixed_pos_results = [result.position_of_agg() for result in self.results]
        top_ten_size = [result.top_ten_size for result in self.results]

        return [[self.approach, "Avg", self.num_correct_evaluator.evaluate(avg_pos_results), self.num_top_ten_evaluator.evaluate(avg_pos_results, top_ten_size), self.direct_comparison_evaluator.evaluate(avg_pos_results, agg_pos_results)],
            [self.approach, "Agg", self.num_correct_evaluator.evaluate(agg_pos_results), self.num_top_ten_evaluator.evaluate(agg_pos_results, top_ten_size), "-"],
            [self.approach, "Closest", self.num_correct_evaluator.evaluate(fixed_pos_results), self.num_top_ten_evaluator.evaluate(fixed_pos_results, top_ten_size), self.direct_comparison_evaluator.evaluate(agg_pos_results, fixed_pos_results)]]
        

class FtqcExperimentEvaluator:
    def __init__(self, results, result_directory) -> None:
        self.results = results
        self.result_directory = result_directory

    def _get_results_for_approach(self, approach):
        return [result for result in self.results if result.ft_qcontainer == approach.value]

    def evaluate(self):
        evaluations = {}
        
        for approach in Approach:
            results_for_approach = self._get_results_for_approach(approach)
            evaluator = ApproachResult(results_for_approach, approach)
            evaluations[approach] = evaluator.evaluate()

        evaluation_as_latex= self.printEvaluations(evaluations, self.result_directory)
            
        return evaluation_as_latex

    def printEvaluations(evaluations, save_directory="."):
        df = []

        for key in evaluations:
            df.extend(evaluations[key])

        df = pd.DataFrame(df, columns=["Appr.", "View", "numT1", "numT10%", "comparison"])
        df = df.round(decimals=1)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{save_directory}/evaluations_{timestamp}.csv"
        
        df.to_csv(csv_filename, index=False)

        return df.to_latex(index=False)

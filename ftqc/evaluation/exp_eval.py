import datetime
import pandas as pd
from enum import Enum
from evaluation.metrics import NumberOfCorrectCircuits, NumberOfTopTenCircuits, DirectComparison
from tabulate import tabulate
from itertools import groupby
from os.path import join 

class ApproachResult:
    def __init__(self, results_for_approach, approach):
        self.results = results_for_approach
        self.approach = approach
        self.num_correct_evaluator = NumberOfCorrectCircuits()
        self.num_top_ten_evaluator = NumberOfTopTenCircuits()
        self.direct_comparison_evaluator = DirectComparison()
        
    def evaluate(self):
        avg_pos_results = [result.avg_postion() for result in self.results]
        agg_pos_results = [result.position_of_agg() for result in self.results]
        fixed_pos_results = [result.position_of_closest() for result in self.results]
        top_ten_size = [result.top_ten_size for result in self.results]

        #TODO: refatoring using enum
        return [[self.approach, "Avg", self.num_correct_evaluator.evaluate(avg_pos_results), self.num_top_ten_evaluator.evaluate(avg_pos_results, top_ten_size), self.direct_comparison_evaluator.evaluate(avg_pos_results, agg_pos_results)],
            [self.approach, "Agg", self.num_correct_evaluator.evaluate(agg_pos_results), self.num_top_ten_evaluator.evaluate(agg_pos_results, top_ten_size), "-"],
            [self.approach, "Closest", self.num_correct_evaluator.evaluate(fixed_pos_results), self.num_top_ten_evaluator.evaluate(fixed_pos_results, top_ten_size), self.direct_comparison_evaluator.evaluate(agg_pos_results, fixed_pos_results)]]
        

class FtqcExperimentEvaluator:
    def __init__(self, results, result_directory) -> None:
        self.results = results
        self.result_directory = result_directory

    def evaluate(self):
        evaluations = {}

        approaches = groupby(self.results, lambda x: x.ft_qcontainer)
        for approach, results in approaches:
            evaluations[approach] = ApproachResult(results, approach).evaluate()

        return self.print_and_save(evaluations, self.result_directory)
            
    def print_and_save(evaluations, save_directory="."):
        df = []

        for key in evaluations:
            df.extend(evaluations[key])

        df = pd.DataFrame(df, columns=["Appr.", "View", "numT1", "numT10%", "comparison"])
        df = df.round(decimals=1)
        print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = join(save_directory, f"evaluations_{timestamp}.csv")
        
        df.to_csv(csv_filename, index=False)

        return df.to_latex(index=False)

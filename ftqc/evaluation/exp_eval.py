import datetime
import pandas as pd
from evaluation.metrics import NumberOfCorrectCircuits, NumberOfTopTenCircuits, DirectComparisonWithAgg
from tabulate import tabulate
from os.path import join 

class ApproachResult:
    def __init__(self, approach, results_for_approach):
        self.results = results_for_approach
        self.approach = approach
        self.num_correct_evaluator = NumberOfCorrectCircuits()
        self.num_top_ten_evaluator = NumberOfTopTenCircuits()
        self.direct_comparison_evaluator = DirectComparisonWithAgg()
        
    def evaluate(self):
        avg_pos_results = [result.avg_postion() for result in self.results]
        agg_pos_results = [result.position_of_agg() for result in self.results]
        fixed_pos_results = [result.position_of_closest() for result in self.results]
        top_ten_size = [result.top_ten_size for result in self.results]

        return [[self.approach, "Avg", self.num_correct_evaluator.evaluate(avg_pos_results), self.num_top_ten_evaluator.evaluate(avg_pos_results, top_ten_size), self.direct_comparison_evaluator.evaluate(agg_pos_results, avg_pos_results)],
            [self.approach, "Agg", self.num_correct_evaluator.evaluate(agg_pos_results), self.num_top_ten_evaluator.evaluate(agg_pos_results, top_ten_size), self.direct_comparison_evaluator.evaluate_with_single(self.results)],
            [self.approach, "Fixed", self.num_correct_evaluator.evaluate(fixed_pos_results), self.num_top_ten_evaluator.evaluate(fixed_pos_results, top_ten_size), self.direct_comparison_evaluator.evaluate(agg_pos_results, fixed_pos_results)]]
        

class FtqcExperimentEvaluator:
    def __init__(self, results, result_directory) -> None:
        self.result_directory = result_directory
        self.approaches = {}
        for result in results:
            if result.ft_qcontainer not in self.approaches.keys():
                self.approaches[result.ft_qcontainer] = []

            self.approaches[result.ft_qcontainer].append(result)

    def evaluate(self):
        evaluations = {}
        for approach, results in self.approaches.items():
            evaluations[approach] = ApproachResult(approach, results).evaluate()

        return FtqcExperimentEvaluator.print_and_save(evaluations, save_directory=self.result_directory)
            
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


class Metric:
    def evaluate(self, positions):
        raise NotImplementedError("This method should be implemented by subclasses.")


class NumberOfCorrectCircuits(Metric):
    def evaluate(self, positions):
        return sum(1 for position in positions if position == 0)

class NumberOfTopTenCircuits(Metric):
    def evaluate(self, positions, top_ten):
        return sum(1 for i in range(len(positions)) if positions[i] <= top_ten[i])

class DirectComparisonWithAgg(Metric):
    def evaluate(self, agg_positions, ref_positions):
        assert len(agg_positions) == len(ref_positions)

        better = 0
        equal = 0
        worse = 0
        for agg_pos, ref_pos in zip(agg_positions, ref_positions):
            if agg_pos == ref_pos:
                equal += 1
            elif agg_pos < ref_pos:
                better += 1
            else:
                worse += 1

        sum = better + equal + worse

        return (worse / sum, equal / sum, better / sum)
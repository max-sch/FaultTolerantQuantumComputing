
class Metric:
    def evaluate(self, positions):
        raise NotImplementedError("This method should be implemented by subclasses.")


class NumberOfCorrectCircuits(Metric):
    def evaluate(self, positions):
        counter = 0
        for position in positions:
            if position == 0:
                counter += 1
        return counter

class NumberOfTopTenCircuits(Metric):
    def evaluate(self, positions, top_ten):
        counter = 0
        for i in range(len(positions)):
            if positions[i] <= top_ten[i]:
                counter += 1
        return counter

class DirectComparison(Metric):
    def evaluate(self, agg_positions, positions):
        assert len(agg_positions) == len(positions)

        greater = 0
        equal = 0
        less = 0
        for agg_pos, pos in zip(agg_positions, positions):
            if agg_pos == pos:
                equal += 1
            if agg_pos < pos:
                greater += 1
            else:
                less += 1

        sum = greater + less + less

        return (less / sum, equal / sum, greater / sum)
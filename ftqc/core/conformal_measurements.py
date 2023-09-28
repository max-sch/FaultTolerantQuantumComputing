from math import exp
from random import randint

default_conformity_threshold = 0.8
agreement_multiplier = 0.75
default_top_n_rate = 0.25
max_top_n = 20
min_top_n = 1

class ConformalSet:
    def __init__(self, measurements, n) -> None:
        '''The measurements must be ordered according to their probabilities'''
        if n <= 0:
            raise Exception("The number of top n values to consider must be greater than zero")

        if n > len(measurements):
            n = len(measurements)
        
        self.state_vecs = measurements[:n]

    def top_n_of(measurements, n):
        elements = measurements.rank().keys()
        return ConformalSet(list(elements), n)

    def intersection(self, other):
        if not isinstance(other, ConformalSet):
            raise Exception("Can only construct intersections with conformal sets")

        return list(set(self.state_vecs) & set(other.state_vecs))

class ConformalBasedMajorityVoting:
    def __init__(self, agreement_threshold, measurements) -> None:
        self.agreement_threshold = agreement_threshold
        self.measurements = measurements

    def _get_highest_votes(self, votes):
        counts = {}
        for key, val in votes.items():
            if val not in counts.keys():
                counts[val] = []
            counts[val].append(key)
        
        sorted_counts = sorted(counts.items(), key=lambda item: item[0], reverse=True)
        return sorted_counts[0][1]
    
    def _handle_equal_majorities(self, votes, highest_votes):
        vote_probs = {}
        for vote in highest_votes:
            vote_probs[vote] = sum(m.get_probability_for(vote) for m in self.measurements)
        prob_votes = self._get_highest_votes(vote_probs)
        ran_idx = randint(0, len(prob_votes) - 1)
        votes[prob_votes[ran_idx]] += 1
        
    def vote(self, conformal_sets):
        votes = {state_vec:0 for conformal_set in conformal_sets for state_vec in conformal_set.state_vecs}
        
        iterator = iter(ConformalSetsIterator(conformal_sets))
        for conf_set_pair in iterator:
            first = conf_set_pair[0]
            second = conf_set_pair[1]
            intersection = first.intersection(second)
            if len(intersection) >= self.agreement_threshold:
                for state_vec in intersection:
                    votes[state_vec] += 1
        
        highest_votes = self._get_highest_votes(votes)
        have_equal_majorities = len(highest_votes) > 1
        if have_equal_majorities:
            self._handle_equal_majorities(votes, highest_votes)

        return votes 

class ConformalSetsIterator:
    def __init__(self, conformal_sets) -> None:
        self.ordered_conf_sets = conformal_sets if isinstance(conformal_sets, list) else list(conformal_sets)
    
    def __iter__(self):
        self.i = 0
        self.j = 0
        return self
    
    def __next__(self):
        if self.i == len(self.ordered_conf_sets) - 1:
            raise StopIteration
        
        if self.j == len(self.ordered_conf_sets) - 1:
            self.i += 1
            self.j = self.i + 1 if self.i + 1 < len(self.ordered_conf_sets) else self.i
        else:
            self.j += 1

        return (self.ordered_conf_sets[self.i], self.ordered_conf_sets[self.j])


def calculate_conformity(conformal_sets, top_n):
    def calculate_score(conformal_sets):
        score = 0

        iterator = iter(ConformalSetsIterator(conformal_sets))
        for conf_set_pair in iterator:
            first = conf_set_pair[0]
            second = conf_set_pair[1]
            matches = len(first.intersection(second))

            score += (2 * matches / top_n) - 1

        return score
    
    def logistic_function(x):
        return 1 / (1 + exp(-x))
    
    return logistic_function(calculate_score(conformal_sets))
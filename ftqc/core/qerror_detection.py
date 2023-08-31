from math import log, sqrt

class QuantumFaultDetector:
    def accept(self, measurments):
        '''Main method for checking measurements in terms of faults'''
        pass

def shannon_entropy(p_dist):
    return sum(p * log(p) for p in p_dist) * (-1)

'''Assuming that the probabilities of p_dist and q_dist are ordered according to the values'''
def kl_divergence(p_dist, q_dist):
    assert len(p_dist) == len(q_dist)

    return sum(p_dist[i] * log(p_dist[i] / q_dist[i]) for i in range(len(p_dist)))

'''Assuming that the probabilities of p_dist and q_dist are ordered according to the values'''
def cross_entropy(p_dist, q_dist):
    assert len(p_dist) == len(q_dist)

    return sum(p_dist[i] * log(q_dist[i]) for i in range(len(p_dist))) * (-1)

'''Assuming that the probabilities of p_dist and q_dist are ordered according to the values'''
def jensen_shannon_divergence(p_dist, q_dist):
    assert len(p_dist) == len(q_dist)

    m = [(p_dist[i] * q_dist[i]) / 2 for i in range(len(p_dist))]
    return 0.5 * kl_divergence(p_dist, m) + 0.5 * kl_divergence(q_dist, m)

'''Assuming that the probabilities of p_dist and q_dist are ordered according to the values'''
def bhattacharyya(p_dist, q_dist):
    assert len(p_dist) == len(q_dist)

    bc = sum(sqrt(p_dist[i] * q_dist[i]) for i in range(len(p_dist)))
    return log(bc) * (-1)

class MeasurementNoiseQuantifier(QuantumFaultDetector):
    def __init__(self, f_divergence, threshold) -> None:
        def closeness_to_uniform_dist(measurements):
            p_dist = measurements.get_probabilities()
            q_dist = [1/measurements.num_counts for _ in range(len(p_dist))]
            return f_divergence(p_dist, q_dist)
        self.measure_closeness_to_uniform_dist = closeness_to_uniform_dist
        self.threshold = threshold

    def using_shannon_entropy(threshold):
        def adapted_shannon_entropy(p_dist, q_dist):
            return shannon_entropy(p_dist)
        return MeasurementNoiseQuantifier(adapted_shannon_entropy, threshold)

    def using_kl_divergence(threshold):
        return MeasurementNoiseQuantifier(kl_divergence, threshold)
    
    def using_cross_entropy(threshold):
        return MeasurementNoiseQuantifier(cross_entropy, threshold)
    
    def using_jensen_shannon_divergence(threshold):
        return MeasurementNoiseQuantifier(jensen_shannon_divergence, threshold)


    def using_bhattacharyya(threshold):
        return MeasurementNoiseQuantifier(bhattacharyya, threshold)

    def accept(self, measurements):
        return not self.reject(measurements)
    
    def reject(self, measurements):
        closeness = self.measure_closeness_to_uniform_dist(measurements)
        return closeness < self.threshold
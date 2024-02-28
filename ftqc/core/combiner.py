from core.entities import Measurements, QuantumDevice

class MeasurementCombiner:
    def combine(self, measurements):
        '''Main method for combining several measurements'''

class LinearOpinionPool(MeasurementCombiner):
    def __init__(self, weights) -> None:
        self.weights = weights

    def with_uniform_weights(qchannels):
        n = len(qchannels)
        uniform_weights = { qchannel:1/n for qchannel in qchannels }
        return LinearOpinionPool(uniform_weights)
    
    def combine(self, measurements):
        self.assert_equal_devices(measurements)
        
        combined_measurements = {}

        measured_states = set()
        for m in measurements:
            measured_states = measured_states.union(m.get_measured_states()) 
        
        for measured_state in measured_states:
            normalized_counts = 0.0
            for measurement in measurements:
                count = measurement.get_count_for(measured_state)
                weight = self.weights[measurement.generated_from_channel]
                normalized_counts += round(count * weight) 
            
            combined_measurements[measured_state] = normalized_counts

        return Measurements(None, combined_measurements)
            

    def assert_equal_devices(self, measurements):
        expected_channels = self.weights.keys()
        actual_channels = {m.generated_from_channel for m in measurements}

        if len(expected_channels) != len(actual_channels):
             raise Exception("The devices of the measurement are in conformance with the registered devices.")

        for actual_channel in actual_channels:
            if actual_channel not in expected_channels:
                raise Exception("The devices of the measurement are in conformance with the registered devices.")
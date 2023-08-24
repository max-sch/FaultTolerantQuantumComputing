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

        measured_states = measurements[0].get_measured_states()
        for measured_state in measured_states:
            normalized_prob = 0.0
            for measurement in measurements:
                probability = measurement.get_probabilitiy(measured_state)
                weight = self.weights[measurement.generated_from_channel]
                normalized_prob += probability * weight 
            
            combined_measurements[measured_state] = normalized_prob

        device_names = [name.unique_name for name in self.weights.keys()]
        quantum_device = QuantumDevice("_".join(device_names))
        return Measurements(quantum_device, combined_measurements)
            

    def assert_equal_devices(self, measurements):
        expected_channels = {channel.device for channel in self.weights.keys()}
        actual_channels = {m.generated_from_channel for m in measurements}

        if len(expected_channels) != len(actual_channels):
             raise Exception("The devices of the measurement are in conformance with the registered devices.")

        for actual_device in actual_channels:
            if actual_device not in expected_channels:
                raise Exception("The devices of the measurement are in conformance with the registered devices.")
from core.combiner import LinearOpinionPool
from core.entities import FaultTolerantQuantumContainer, Measurements
from core.qswitches import QuantumSwitchUnit

class FaultTolerantPatternBuilder:
    def __init__(self, pattern_name) -> None:
        self.pattern_name = pattern_name
    
    def build(self):
        if self.pattern_name == "" or self.pattern_name == None:
            raise Exception("The pattern name must be specified.")
        

class CombinerPatternBuilder(FaultTolerantPatternBuilder):
    def __init__(self, pattern_name) -> None:
        super().__init__(pattern_name)
        self.combiner = None
        self.uniform_weights = False
        self.channels = []

    def add_channel(self, channel):
        self.channels.append(channel)
        return self
    
    def add_n_channels(self, channels):
        self.channels.append(channels)
        return self

    def combine_measurements_with(self, combiner):
        self.combiner = combiner
        return self
    
    def combine_measurements_uniformly(self):
        self.uniform_weights = True
        return self
    
    def build(self):
        super().build()

        if len(self.channels) < 1:
            raise Exception("There must be at least one channel.")

        if self.combiner == None:
            if self.uniform_weights:
                self.combiner = LinearOpinionPool.with_uniform_weights(self.channels)
            else:
                raise Exception("No combiner has been specified.")
        
        return FaultTolerantQuantumContainer(self.pattern_name, self.channels, self.combiner.combine)
    
class ComparisonPatternBuilder(FaultTolerantPatternBuilder):
    class SpecialCaseComparatorMeasurements(Measurements):
        def __init__(self, decorated_measurements, accept) -> None:
            super().__init__(decorated_measurements.generated_from_channel, 
                             decorated_measurements.measurements)
            self.accept = accept

        def accept(measurements):
            return ComparisonPatternBuilder.SpecialCaseComparatorMeasurements(measurements, True)
        
        def reject(measurements):
            return ComparisonPatternBuilder.SpecialCaseComparatorMeasurements(measurements, False)

        def is_accepted(self):
            return self.accept
        
        def is_rejected(self):
            return not self.accept
    
    def __init__(self, pattern_name) -> None:
        super().__init__(pattern_name)
        self.primary_channel = None
        self.comparator_channel = None
        self.num_matching_solutions = 1

    def with_primary_channel(self, channel):
        self.primary_channel = channel
        return self
    
    def and_comparator(self, channel):
        self.comparator_channel = channel
        return self
    
    def num_of_matching_solutions(self, num_matching_solutions):
        self.num_matching_solutions = num_matching_solutions
        return self
    
    def build(self):
        super().build()

        if self.primary_channel == None:
            raise Exception("A primary channel must be specified.")
        
        if self.comparator_channel == None:
            raise Exception("A comparator must be specified.")
        
        if self.num_matching_solutions <= 0:
            raise Exception("The number of matching solutions must be greater than zero.")
        
        def accept(measurements):
            if len(measurements) != 2:
                raise Exception("There must be only two mearuements.")
            
            channel_to_measurements = {channel:None for channel in [self.primary_channel, self.comparator_channel]}
            for m in measurements:
                if m.generated_from_channel == self.primary_channel:
                    channel_to_measurements[self.primary_channel] = m

                if m.generated_from_channel == self.comparator_channel:
                    channel_to_measurements[self.comparator_channel] = m
            
            if any(value == None for value in channel_to_measurements.values()):
                raise Exception("There are only one or no measurements for the primary and comparator channel.")
            
            first_n_solutions_of_primary = []
            for k, _ in channel_to_measurements[self.primary_channel].rank().items():
                first_n_solutions_of_primary.append(k)
                if len(first_n_solutions_of_primary) == self.num_matching_solutions:
                    break

            first_n_solutions_of_comparator = []
            for k, _ in channel_to_measurements[self.comparator_channel].rank().items():
                first_n_solutions_of_comparator.append(k)
                if len(first_n_solutions_of_comparator) == self.num_matching_solutions:
                    break

            for i in range(self.num_matching_solutions):
                if first_n_solutions_of_primary[i] not in first_n_solutions_of_comparator:
                    return ComparisonPatternBuilder.SpecialCaseComparatorMeasurements.reject(channel_to_measurements[self.primary_channel])
            return ComparisonPatternBuilder.SpecialCaseComparatorMeasurements.accept(channel_to_measurements[self.primary_channel])
        
        return FaultTolerantQuantumContainer(self.pattern_name, [self.primary_channel, self.comparator_channel], accept)
            


class SparingPatternBuilder(FaultTolerantPatternBuilder):
    def __init__(self, pattern_name) -> None:
        super().__init__(pattern_name)
        self.operational = None
        self.spares = []
        self.error_detector = None
        self.qswitch = None

    def with_operational(self, channel, error_detector=None):
        self.operational = QuantumSwitchUnit(channel, error_detector)
        return self
    
    def and_spare(self, spare_channel, error_detector=None):
        self.spares.append(QuantumSwitchUnit(spare_channel, error_detector))
        return self
    
    def using_single_error_detection(self, error_detector):
        self.error_detector = error_detector
        return self
    
    def using_quantum_switch(self, qswitch):
        self.qswitch = qswitch
        return self
    
    def build(self):
        super().build()

        if self.operational == None:
            raise Exception("The operational must be specified")
        
        if self.error_detector == None:
            raise Exception("An error detection component must be specified")
        
        if self.qswitch == None:
            raise Exception("A quantum switch must be specified")
        
        if len(self.spares) < 1:
            raise Exception("There must be at least one spare")
        
        self.qswitch.operational = self.operational
        self.qswitch.spares = self.spares

        qswitch_units = [self.operational] + self.spares
        if self.error_detector != None and all(qswitch_unit.error_detector == None for qswitch_unit in qswitch_units):
            for qswitch_unit in qswitch_units:
                qswitch_unit.error_detector = self.error_detector
        elif self.error_detector == None and any(qswitch_unit.error_detector == None for qswitch_unit in qswitch_units):
            raise Exception("There must be either a single error detection component or an assigned error detection component for each channel")
        else:
            raise Exception("The assignment between channels and error detection components is not valid")
        
        channels = [qswitch_unit.channel for qswitch_unit in qswitch_units]
        return FaultTolerantQuantumContainer(self.pattern_name, channels, self.qswitch.switch_if_necessary)
        

        
        




  



from core.combiner import LinearOpinionPool
from core.entities import FaultTolerantQuantumContainer, Measurements
from core.qswitches import QuantumSwitchUnit
from core.qerror_detection import MeasurementComparison
from core.conformal_measurements import (ConformalBasedMajorityVoting, 
                                         ConformalSet, 
                                         calculate_conformity, 
                                         default_conformity_threshold, 
                                         default_top_n_rate, 
                                         agreement_multiplier)

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
            measurements_primary = measurements[0]
            if measurements[1].generated_from_channel == self.primary_channel:
                measurements_primary = measurements[1]
            
            comparator = MeasurementComparison(self.primary_channel, self.comparator_channel, self.num_matching_solutions)
            measurements_primary.accepted = comparator.accept(measurements)

            return measurements_primary
        
        return FaultTolerantQuantumContainer(self.pattern_name, [self.primary_channel, self.comparator_channel], accept)

class SparingPatternBuilder(FaultTolerantPatternBuilder):
    def __init__(self, pattern_name) -> None:
        super().__init__(pattern_name)
        self.operational = None
        self.spares = []
        self.fault_detector = None
        self.qswitch = None

    def with_operational(self, primary_channel, secondary_channels=None, fault_detector=None):
        if not isinstance(secondary_channels, list) and secondary_channels != None:
            secondary_channels = [secondary_channels]

        self.operational = QuantumSwitchUnit(fault_detector, primary_channel, secondary_channels)
        return self
    
    def and_spare(self, primary_channel, secondary_channels=None, fault_detector=None):
        if not isinstance(secondary_channels, list) and secondary_channels != None:
            secondary_channels = [secondary_channels]

        self.spares.append(QuantumSwitchUnit(fault_detector, primary_channel, secondary_channels))
        return self
    
    def using_single_error_detection(self, fault_detector):
        self.fault_detector = fault_detector
        return self
    
    def using_quantum_switch(self, qswitch):
        self.qswitch = qswitch
        return self
    
    def build(self):
        super().build()

        if self.operational == None:
            raise Exception("The operational must be specified")
        
        if self.qswitch == None:
            raise Exception("A quantum switch must be specified")
        
        if len(self.spares) < 1:
            raise Exception("There must be at least one spare")
        
        self.qswitch.operational = self.operational
        self.qswitch.spares = self.spares

        qswitch_units = [self.operational] + self.spares
        all_set = all(qswitch_unit.fault_detector != None for qswitch_unit in qswitch_units)
        none_set = all(qswitch_unit.fault_detector == None for qswitch_unit in qswitch_units)
        if not (none_set ^ all_set):
            raise Exception("The assignment between channels and error detection components is not valid") 
        
        if none_set and self.fault_detector != None:
            for qswitch_unit in qswitch_units:
                qswitch_unit.fault_detector = self.fault_detector
        elif none_set and self.fault_detector == None:
            raise Exception("The assignment between channels and error detection components is not valid")
        
        channels = [channel for qswitch_unit in qswitch_units for channel in qswitch_unit.get_channels()]
        return FaultTolerantQuantumContainer(self.pattern_name, channels, self.qswitch.switch_if_necessary)
    
class ConformalMeasurementsBuilder(FaultTolerantPatternBuilder):
    def __init__(self, pattern_name) -> None:
        super().__init__(pattern_name)
        self.channels = []
        self.top_n_rate = None
        self.conformity_threshold = None

    def add_channel(self, channel):
        self.channels.append(channel)
        return self
    
    def set_optional_top_n_rate(self, top_n_rate):
        self.top_n_rate = top_n_rate
        return self
    
    def with_min_conformity(self, conformity_threshold):
        self.conformity_threshold = conformity_threshold
        return self
    
    def default_conformity(self):
        self.conformity_threshold = default_conformity_threshold
        return self
    
    def build(self):
        super().build()

        if len(self.channels) < 1:
            raise Exception("There must be at least one channel.")
        
        if self.top_n_rate == None:
            self.top_n_rate = default_top_n_rate

        if self.conformity_threshold == None:
            self.conformity_threshold = default_conformity_threshold

        
        def conformal_based_majority_voting(measurements):
            if len(measurements) < 2:
                raise Exception("There must be at least two mearuements.")
            
            top_n = (int) (measurements[0].num_of_measured_states() * self.top_n_rate)
            if (top_n < 1):
                top_n = 1

            agreement_threshold = (int) (agreement_multiplier * top_n)
            if agreement_threshold < 1:
                agreement_threshold = 1

            conformal_sets = [ConformalSet.top_n_of(m, top_n) for m in measurements]
            votes = ConformalBasedMajorityVoting(agreement_threshold).vote(conformal_sets)
            conformity = calculate_conformity(conformal_sets, top_n)
            return Measurements(None, votes, accepted=conformity >= self.conformity_threshold)

        return FaultTolerantQuantumContainer(self.pattern_name, self.channels, conformal_based_majority_voting)

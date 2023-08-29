from core.combiner import LinearOpinionPool
from core.entities import FaultTolerantQuantumContainer
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

        qswitch_units = self.operational + self.spares
        if self.error_detector != None and all(qswitch_unit.error_detector == None for qswitch_unit in qswitch_units):
            for qswitch_unit in qswitch_units:
                qswitch_unit.error_detector = self.error_detector
        elif self.error_detector == None and any(qswitch_unit.error_detector == None for qswitch_unit in qswitch_units):
            raise Exception("There must be either a single error detection component or an assigned error detection component for each channel")
        else:
            raise Exception("The assignment between channels and error detection components is not valid")
        
        channels = [qswitch_unit.channel for qswitch_unit in self.operational + self.spares]
        return FaultTolerantQuantumContainer(self.pattern_name, channels, self.qswitch.switch_if_necessary)
        

        
        




  



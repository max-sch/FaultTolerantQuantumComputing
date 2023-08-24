from core.combiner import LinearOpinionPool
from core.entities import FaultTolerantQuantumContainer

class FaultTolerantPatternBuilder:
    def __init__(self, pattern_name) -> None:
        self.pattern_name = pattern_name
        self.channels = []

    def add_channel(self, channel):
        self.channels.append(channel)
        return self
    
    def add_n_channels(self, channels):
        self.channels.append(channels)
        return self
    
    def build(self):
        if self.pattern_name == "" or self.pattern_name == None:
            raise Exception("The pattern name must be specified.")

        if len(self.channels) < 1:
            raise Exception("There must be at least one channel.")
        

class CombinerPatternBuilder(FaultTolerantPatternBuilder):
    def __init__(self, pattern_name) -> None:
        super().__init__(pattern_name)
        self.combiner = None
        self.uniform_weights = False

    def combine_measurements_with(self, combiner):
        self.combiner = combiner
        return self
    
    def combine_measurements_uniformly(self):
        self.uniform_weights = True
        return self
    
    def build(self):
        super().build()

        if self.combiner == None:
            if self.uniform_weights:
                self.combiner = LinearOpinionPool.with_uniform_weights(self.channels)
            else:
                raise Exception("No combiner has been specified.")
        
        return FaultTolerantQuantumContainer(self.pattern_name, self.channels, self.combiner.combine)

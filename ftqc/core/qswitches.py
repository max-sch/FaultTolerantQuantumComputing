import uuid
from random import randint

class QuantumSwitchUnit:
    def __init__(self, channel, error_detector) -> None:
        self.id = str(uuid.uuid4())
        self.channel = channel
        self.error_detector = error_detector
        self.measurements = None

    def __hash__(self) -> int:
        return hash(self.id)

    def fault_detected(self):
        return self.error_detector.accept(self.measurements)
    
    def has_produced(self, measurements):
        return self.channel == measurements.generated_from_channel

class QuantumRedundancySwitch:
    def __init__(self) -> None:
        self.operational = None
        self.spares = None

    def switch_if_necessary(self, all_measurements):
        qswitch_units = [self.operational] + self.spares
        for qswitch_unit in qswitch_units:
            qswitch_unit.measurements = None
            for measurements in all_measurements:
                if qswitch_unit.has_produced(measurements):
                    qswitch_unit.measurements = measurements
        
        if any(qswitch_unit.measurements == None for qswitch_unit in qswitch_units):
            raise Exception("There is at least one qswitch for which no measurements could be retrieved")

        if self.operational.fault_detected():
            new_operational = self.do_switch()

            self.spares.remove(new_operational)
            self.spares.append(self.operational)
            
            self.operational = new_operational
        
        return self.operational.measurements
    
    def do_switch(self):
        '''Main method for switching between spares and operational'''
        pass

class SimpleQuantumRedundancySwitch(QuantumRedundancySwitch):
    def do_switch(self):
        for spare in self.spares:
            if not spare.fault_detected():
                return spare
        
        return self.spares[randint(0, len(self.spares) - 1)]


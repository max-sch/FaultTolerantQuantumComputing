import uuid
from random import randint

class QuantumSwitchUnit:
    def __init__(self, fault_detector, primary_channel, secondary_channels=None) -> None:
        self.id = str(uuid.uuid4())
        self.primary_channel = primary_channel
        self.secondary_channels = secondary_channels
        self.fault_detector = fault_detector
        self.measurements = None

    def __hash__(self) -> int:
        return hash(self.id)

    def fault_detected(self):
        return not self.fault_detector.accept(self.measurements)
    
    def has_produced(self, measurements):
        return any(channel == measurements.generated_from_channel for channel in self.get_channels())
    
    def get_channels(self):
        if self.secondary_channels == None:
            return [self.primary_channel]
        return [self.primary_channel] + self.secondary_channels
    
    def operational_measurements(self):
        for m in self.measurements:
            if m.generated_from_channel == self.primary_channel:
                return m
            
        raise Exception("None of the measurements was produced by the primary channel")

class QuantumRedundancySwitch:
    def __init__(self) -> None:
        self.operational = None
        self.spares = None

    def switch_if_necessary(self, all_measurements):
        qswitch_units = [self.operational] + self.spares
        for qswitch_unit in qswitch_units:
            qswitch_unit.measurements = []
            for measurements in all_measurements:
                if qswitch_unit.has_produced(measurements):
                    qswitch_unit.measurements.append(measurements)
        
        if any(len(qswitch_unit.measurements) == 0 for qswitch_unit in qswitch_units):
            raise Exception("There is at least one qswitch for which not all measurements could be retrieved")

        if self.operational.fault_detected():
            new_operational = self.do_switch()

            self.spares.remove(new_operational)
            self.spares.append(self.operational)
            
            self.operational = new_operational
        
        return self.operational.operational_measurements()
    
    def do_switch(self):
        '''Main method for switching between spares and operational'''
        pass

class SimpleQuantumRedundancySwitch(QuantumRedundancySwitch):
    def do_switch(self):
        for spare in self.spares:
            if not spare.fault_detected():
                return spare
        
        return self.spares[randint(0, len(self.spares) - 1)]


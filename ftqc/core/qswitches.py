class QuantumSwitchUnit:
    def __init__(self, measurement, error_detector) -> None:
        self.measurement = measurement
        self.error_detector = error_detector

    def fault_detected(self):
        return self.error_detector.accept(self.measurement)

class QuantumRedundancySwitch:
    def __init__(self, operational, spares) -> None:
        self.operational = operational
        self.spares = spares

    def switch_if_necessary(self):
        if self.operational.fault_detected:
            new_operational = self.do_switch()

            self.spares.remove(new_operational)
            self.spares.append(self.operational)
            
            self.operational = new_operational
        
        return self.operational.measurement
    
    def do_switch(self):
        '''Main method for switching between spares and operational'''

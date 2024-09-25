from qiskit.providers.fake_provider import GenericBackendV2
from core.entities import IBMQuantumComputer, QuantumComputerSimulator
#from qiskit_ibm_provider import IBMProvider

class QuantumDeviceProvider:
    def __init__(self, backend_name, ibmq_credentials=None) -> None:
        #if ibmq_credentials == None:
        if True:
            self.backend = GenericBackendV2(num_qubits=10)
        else:
            ibmq_credentials.activate_account()
            
            #self.provider = IBMProvider(instance=ibmq_credentials.instance)
            self.provider = None
            backend = self.provider.get_backend(backend_name)

        self.default_device = IBMQuantumComputer(self.backend)

    def max_job_size_for(self, device):
        return self.backend.configuration().max_experiments 
    
    def provided_devices(self, min_qubits=10):
        #return [IBMQuantumComputer(b) for b in self.provider.backends() if b.configuration().n_qubits >= min_qubits]
        return [IBMQuantumComputer(self.backend)]
    
class FakeQuantumDeviceProvider(QuantumDeviceProvider):
    '''The device provider is mainly considered for testing purposes'''
    def __init__(self) -> None:
        super().__init__("fake_boeblingen")

    def max_job_size_for(self, device):
        return 1
        #return self.backend.configuration().max_experiments
        
        #raise Exception("There is no backend for device: " + device.unique_name)

    #def provided_devices(self, min_qubits=10):
        #return super.provided_devices(self, num_qubits)
        #for b in self.provider.backends():
            #if b.configuration().n_qubits >= min_qubits:
                #try:
                    #devices.append(IBMQuantumComputer(b))
                #except AttributeError:
                    #print("There is no name for backend: " + str(b))
        #return devices
    
class HybridQuantumDeviceProvider(QuantumDeviceProvider):
    def __init__(self, ibmq_credentials) -> None:
        self.fake_device_provider = FakeQuantumDeviceProvider()
        self.ehningen_device_provider = QuantumDeviceProvider("ibmq_ehningen", ibmq_credentials)
        self.default_device = self.ehningen_device_provider.default_device

    def max_job_size_for(self, device):
        if device.unique_name == "ibmq_ehningen":
            return self.ehningen_device_provider.max_job_size_for(device)
        elif device.unique_name == "fake_boeblingen":
            return self.ehningen_device_provider.max_job_size_for(self.default_device)
        else:
            return self.fake_device_provider.max_job_size_for(device)
    
    def provided_devices(self, min_qubits=10):
        filtered = filter(lambda d: (d.unique_name != "fake_boeblingen"), self.fake_device_provider.provided_devices())
        devices = list(filtered)
        devices.append(self.default_device)
        return devices
    
class IBMQCredentials:
    def __init__(self, api_token, api_url, instance) -> None:
        self.api_token = api_token
        self.api_url = api_url
        self.instance = instance

    def activate_account(self, overwrite=False):
        pass
        #if overwrite:
            #IBMProvider.save_account(self.api_token, self.api_url, overwrite=True)
            #return

        #for account in IBMProvider.saved_accounts().values():
            #if account['token'] == self.api_token:
                ##print("Account already exists and doesn't has to be activated")
                #return

        #IBMProvider.save_account(self.api_token, self.api_url)
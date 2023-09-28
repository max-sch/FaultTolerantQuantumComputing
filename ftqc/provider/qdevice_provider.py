from qiskit.test.mock import FakeProvider
from core.entities import IBMQuantumComputer, QuantumComputerSimulator
from qiskit_ibm_provider import IBMProvider

class QuantumDeviceProvider:
    def __init__(self, backend_name, ibmq_credentials=None) -> None:
        if ibmq_credentials == None:
            self.provider = FakeProvider()
            backend = self.provider.get_backend(backend_name if backend_name != "ibmq_ehningen" else "fake_boeblingen")
        else:
            ibmq_credentials.activate_account()
            
            self.provider = IBMProvider(instance=ibmq_credentials.instance)
            backend = self.provider.get_backend(backend_name)

        self.default_device = IBMQuantumComputer(backend)

    def max_job_size_for(self, device):
        backend = self.provider.get_backend(device.unique_name)
        return backend.configuration().max_experiments 
    
    def provided_devices(self, min_qubits=10):
        return [IBMQuantumComputer(b) for b in self.provider.backends() if b.configuration().n_qubits >= min_qubits]
    
class FakeQuantumDeviceProvider(QuantumDeviceProvider):
    '''The device provider is mainly considered for testing purposes'''
    def __init__(self) -> None:
        super().__init__("fake_boeblingen")

    def max_job_size_for(self, device):
        for b in self.provider.backends():
            if b.name() in device.unique_name:
                return b.configuration().max_experiments
        
        raise Exception("There is no backend for device: " + device.unique_name)

    def provided_devices(self, min_qubits=10):
        devices = []
        for b in self.provider.backends():
            if b.configuration().n_qubits >= min_qubits:
                try:
                    devices.append(IBMQuantumComputer(b))
                except AttributeError:
                    print("There is no name for backend: " + str(b))
        return devices
    
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
        if overwrite:
            IBMProvider.save_account(self.api_token, self.api_url, overwrite=True)
            return

        for account in IBMProvider.saved_accounts().values():
            if account['token'] == self.api_token:
                print("Account already exists and doesn't has to be activated")
                return

        IBMProvider.save_account(self.api_token, self.api_url)
from qiskit.test.mock import FakeProvider
from qiskit import IBMQ
from core.entities import IBMQuantumComputer, QuantumComputerSimulator

class QuantumDeviceProvider:
    def __init__(self, backend_name, ibmq_credentials=None) -> None:
        if ibmq_credentials == None:
            self.provider = FakeProvider()
            backend = self.provider.get_backend(backend_name if backend_name != "ibmq_ehningen" else "fake_boeblingen")
        else:
            ibmq_credentials.activate_account()

            self.provider = IBMQ.get_provider(project="ticket")
            backend = self.provider.get_backend(backend_name)

        self.default_device = IBMQuantumComputer(backend)
    
    def provided_devices(self, min_qubits=10):
        return [IBMQuantumComputer(b) for b in self.provider.backends() if b.configuration().n_qubits >= min_qubits]
    
class FakeQuantumDeviceProvider(QuantumDeviceProvider):
    '''The device provider is mainly considered for testing purposes'''
    def __init__(self) -> None:
        super().__init__("fake_boeblingen")

    def provided_devices(self, min_qubits=10):
        return [QuantumComputerSimulator.create_noisy_simulator(b) 
                for b in self.provider.backends() if b.configuration().n_qubits >= min_qubits]
    
class IBMQCredentials:
    def __init__(self, api_token, api_url) -> None:
        self.api_token = api_token
        self.api_url = api_url

    def activate_account(self):
        IBMQ.enable_account(self.api_token, self.api_url)
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit_ibm_runtime.fake_provider import FakeFez
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile


class Func_run_protocol:
    def __init__(
            self, 
            simulator: bool = True, 
            noise: bool = False, 
            qubit_Alice: int = 0, 
            qubit_Bob: int = 1, 
            backend: str = "ibm_fez"
    ) -> None:
        """
        A class with the methods used in both protocols: This includes a method that run the circuit either on simulator
        with no noise, on simulator with noise or on the chosen IBM backend and the method for the communication with
        CNOT gates. 

        Args:
            simulator (bool, optional): Option to run on simulator or not. Defaults to True.
            noise (bool, optional): Option to have a noisy simulation or not. Defaults to False.
            qubit_Alice (int, optional): The qubit to use on the backend for Alice. Defaults to 0.
            qubit_Bob (int, optional): The qubit to use on the backend for Bob. Defaults to 1. 
            backend (str, optional): The name of the backend on which to run the protocol. Defaults to "ibm_fez".
        """

        self.simulator = simulator
        self.noise = noise
        self.backend = backend
        self.qubit_Alice = qubit_Alice
        self.qubit_Bob = qubit_Bob

    def execute_simulator(self, circuit: QuantumCircuit) -> dict:
        """
        This method execute the circuit on the Aer simulator and returns the result.

        Args:
            circuit (QuantumCircuit): The circuit to run on the simulator.

        Returns:
            dict: The counts of the measurement of Alice's qubit.
        """
        
        simulator = AerSimulator()
        transpiled_circuit = transpile(circuit, backend = simulator, optimization_level=0, initial_layout = [qubit for qubit in range(self.qubit_Alice, self.qubit_Bob + 1)])
        print(transpiled_circuit)
        result = simulator.run(transpiled_circuit, shots = 1000).result()
        counts = result.get_counts(transpiled_circuit)
        
        return counts
    
    def execute_simulator_noise(self, circuit: QuantumCircuit) -> str:
        """
        This method execute the circuit on a noisy simulator, Fake Fez, and returns the result.

        Args:
            circuit (QuantumCircuit): The circuit to run on the noisy simulator.

        Returns:
            str: Bit string of the most frequent result.
        """
       
        backend = FakeFez()
        transpiled_circuit = transpile(circuit, backend = backend, optimization_level = 0)
        print(transpiled_circuit)

        sampler = Sampler(mode = backend)
        
        job = sampler.run([transpiled_circuit], shots = 1000)
        pub_result = job.result()[0]
        counts = pub_result.join_data().get_counts()

        return counts
    
    def execute_backend(self, circuit: QuantumCircuit):
        """
        This method execute the circuit on IBM's backend and returns the result.

        Args:
            circuit (QuantumCircuit): The circuit to execute on the backend.
        """

        # Add your token and your instance
        service = QiskitRuntimeService(channel="ibm_cloud")
        backend = service.backend(name = self.backend)
        print(f">>> Backend: {backend}")
        pm = generate_preset_pass_manager(optimization_level = 0, backend = backend, initial_layout=[qubit for qubit in range(self.qubit_Alice, self.qubit_Bob + 1)])
        isa_circuit = pm.run(circuit)
        print(isa_circuit)

        sampler = Sampler(mode = backend)
        sampler.options.default_shots = 1000
        job = sampler.run([isa_circuit])

        print(f">>> Job ID: {job.job_id()}")
        print(f">>> Job Status: {job.status()}")
        
        result = job.result()
        pub_result = result[0]
        counts = pub_result.join_data().get_counts()

        return counts
    
    def execute_protocol(self, circuit: QuantumCircuit) -> tuple[dict, int]:
        """
        Execute the protocol either on simulator, with or without noise, or the specified QPU.

        Args:
            circuit (QuantumCircuit): The circuit to execute.

        Returns:
            tuple[dict, int]: The counts and the bit string of the most frequent result. It is 1 if Bob and Alice inputs 
            are 1 and 0 otherwise.
        """

        if self.simulator and self.noise:
            counts = self.execute_simulator_noise(circuit)

        elif self.simulator and not self.noise:
            counts = self.execute_simulator(circuit)

        else:
            counts = self.execute_backend(circuit)

        final_counts = {"0": 0, "1": 0}
        for key, value in counts.items():
            final_counts[key[0]] += value

        output = max(final_counts, key = final_counts.get)

        print(f"Counts for the output register: {final_counts}")
        
        return final_counts, output
    
    def communication_CNOT(self) -> QuantumCircuit:
        """
        This method execute the communication between Alice and Bob using Control-Not gates.

        Returns:
            QuantumCircuit: The circuit for the communication between the qubits.
        """

        num_qubits = (self.qubit_Bob - self.qubit_Alice) + 1
        qreg = QuantumRegister(num_qubits)
        comm_qc = QuantumCircuit(qreg)

        for i in range(num_qubits - 1):
            comm_qc.cx(i, i + 1)

        for i in range(num_qubits - 1):
            comm_qc.cx(i + 1, i)

        return comm_qc
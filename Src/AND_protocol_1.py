import numpy as np
import warnings
import math

from qiskit.circuit.library import IGate
from Src.Functions import Func_run_protocol as Run_protocol
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


class AND_protocol_1(Run_protocol):
    def __init__(
            self,
            Alice_input: bool,
            Bob_input: bool, 
            type_communication: str, 
            simulator: bool = True, 
            noise: bool = False, 
            qubit_Alice: int = 0, 
            qubit_Bob: int = 1, 
            backend: str = "ibm_fez", 
            r: int = 1
    ) -> None:
        """
        A class to execute a logical AND between the inputs of Alice and Bob using the protocol from Jain, Radhakrishnan, and Sen.
        https://arxiv.org/pdf/1505.03110

        Args:
            Alice_input (bool): Alice's classical input.
            Bob_input (bool): Bob's classical input.
            type_communication (str): The communication between Alice and Bob, it is either "cnot" or "entanglement".
            simulator (bool, optional): Option to run on a simulator or not. Defaults to True.
            noise (bool, optional): Option to have a noisy simulation or not. Defaults to False.
            qubit_Alice (int, optional): The qubit to use on the backend for Alice. Defaults to 0.
            qubit_Bob (int, optional): The qubit to use on the backend for Bob. Defaults to 1.
            backend (str, optional): On which backend to run the protocol. Defaults to "ibm_fez".
            r (int, optional): The number of iterations r (it needs to be odd). Defaults to 1.
        """

        super().__init__(simulator, noise, qubit_Alice, qubit_Bob, backend)

        # inputs
        self.Alice_input = Alice_input
        self.Bob_input = Bob_input

        # results
        self.output = None
        self.counts = None

        # parameters
        self.type_communication = type_communication
        self.num_qubits = (self.qubit_Bob - self.qubit_Alice) + 1
        self.r = r
        self.theta = np.pi/(4 * (self.r + 1))


    def reflection(self):
        """
        This method implements the reflection operator and create the gate for it.

        Returns:
            Gate: The quantum gate for the reflection operator
        """

        qreg = QuantumRegister(1)
        reflection_gate = QuantumCircuit(qreg)

        reflection_gate.ry(-2 * self.theta, qreg)
        reflection_gate.z(qreg)
        reflection_gate.ry(2 * self.theta, qreg)

        reflection_gate = reflection_gate.to_gate(label = "Reflection")

        return reflection_gate
    
    def protocol1_cnot(self) -> tuple[dict, int]:
        """
        Method for the execution of the first protocol for computing the logical operation AND. The communication between Alice and
        Bob is done using CNOT gates.

        Returns:
            tuple[dict, int]: The counts and the output of the most frequent result. It is 1 if Bob and Alice's inputs 
            are 1 and 0 otherwise.
        """

        # Warning for the input "r"
        if (self.r % 2) == 0:
            warnings.warn("The value r needs to be an odd number for this protocol.")

        qreg = QuantumRegister(self.num_qubits)
        creg = ClassicalRegister(1)
        qcircuit = QuantumCircuit(qreg, creg)

        reflection_operator = self.reflection()

        for _ in range(self.r):

            # Alice's operation depending on her input
            if self.Alice_input == 1:
                qcircuit.append(reflection_operator, [0])
                
            else:
                qcircuit.append(IGate(), [0])

            qcircuit.barrier()

            # Alice sends to Bob
            comm_qc = self.communication_CNOT()
            qcircuit.compose(comm_qc, qreg, inplace=True)

            qcircuit.barrier()

            # Bob's operation depending on his input
            if self.Bob_input == 1:
                qcircuit.z([self.num_qubits - 1])
            else:
                qcircuit.append(IGate(), [self.num_qubits - 1])

            qcircuit.barrier()

            # Bob sends back to Alice
            qcircuit.compose(comm_qc.inverse(), qreg, inplace=True)

            qcircuit.barrier()

        # Alice's operation depending on her input
        if self.Alice_input == 1:
            qcircuit.append(reflection_operator, [0])
        else:
            qcircuit.append(IGate(), [0])

        qcircuit.measure(qreg[0], creg)

        counts, output = self.execute_protocol(qcircuit)
        
        return counts, output
    
    def protocol_one_qubit(self) -> tuple[dict, int]:
        """
        This method implements the protocol on a single qubit. This means that there is no communication between Alice and Bob,
        they use the same qubit.

        Returns:
            tuple[dict, int]: The counts and the output of the most frequent result. It is 1 if Bob and Alice's inputs 
            are 1 and 0 otherwise.
        """

        # Warning for the input "r"
        if (self.r % 2) == 0:
            warnings.warn("The value r needs to be an odd number for this protocol.")

        qreg = QuantumRegister(1)
        creg = ClassicalRegister(1)
        qcircuit = QuantumCircuit(qreg, creg)

        reflection_operator = self.reflection()

        for _ in range(self.r):

            # Alice's operation depending on her input
            if self.Alice_input == 1:
                qcircuit.append(reflection_operator, qreg)
                
            else:
                qcircuit.append(IGate(), qreg)

            qcircuit.barrier()

            # Bob's operation depending on his input
            if self.Bob_input == 1:
                qcircuit.z(qreg)
            else:
                qcircuit.append(IGate(), qreg)

            qcircuit.barrier()

        # Alice's operation depending on her input
        if self.Alice_input == 1:
            qcircuit.append(reflection_operator, qreg)
        else:
            qcircuit.append(IGate(), qreg)

        qcircuit.measure(qreg, creg)

        self.counts, self.output = self.execute_protocol(qcircuit)

        return self.counts, self.output
    
    def protocol1_entanglement(self) -> tuple[dict, int]:
        """
        Method for the execution of the first protocol for computing the logical operation AND. The communication between Alice and
        Bob is done using entanglement swapping.

        Returns:
            tuple[dict, int]: The counts and the output of the most frequent result. It is 1 if Bob and Alice's inputs 
            are 1 and 0 otherwise.
        """

        qreg = QuantumRegister(self.num_qubits)
        creg = ClassicalRegister(self.num_qubits - 2)
        final_meas_creg = ClassicalRegister(1)
        qcircuit = QuantumCircuit(qreg, creg, final_meas_creg)

        reflection_operator = self.reflection()

        for _ in range(self.r):

            # Alice's operation depending on her input
            if self.Alice_input == 1:
                qcircuit.append(reflection_operator, [0])
                
            else:
                qcircuit.append(IGate(), [0])

            qcircuit.barrier()

            # Alice sends to Bob
            num_EPR_pairs = int((self.num_qubits/2) - 2)

            # Create the EPR pairs on the qubits between Alice and Bob
            index_EPR = 1
            for _ in range(num_EPR_pairs + 1):
                qcircuit.h(qreg[index_EPR])
                qcircuit.cx(qreg[index_EPR], qreg[index_EPR + 1])
                index_EPR += 2

            # Change the basis for the Bell measure
            index_base = 0
            for _ in range(num_EPR_pairs + 1):
                qcircuit.cx(qreg[index_base], qreg[index_base + 1])
                qcircuit.h(qreg[index_base])
                index_base += 2

            # Measure et reset the qubits
            for i in range(self.num_qubits - 2):
                qcircuit.measure(qreg[i], creg[i])
                qcircuit.reset(qreg[i])

            # Apply the X and Z corrections
            index = 0
            while index < (self.num_qubits - 2):
                with qcircuit.if_test((creg[index + 1], 1)):
                    qcircuit.x(qreg[self.num_qubits - 2])

                with qcircuit.if_test((creg[index], 1)):
                    qcircuit.z(qreg[self.num_qubits - 2])

                index += 2

            qcircuit.swap(qreg[self.num_qubits - 2], qreg[self.num_qubits - 1])

            qcircuit.barrier()

            # Bob's operation depending on his input
            if self.Bob_input == 1:
                qcircuit.z([self.num_qubits - 1])
            else:
                qcircuit.append(IGate(), [self.num_qubits - 1])

            qcircuit.barrier()

            # Bob sends back to Alice
            # Create the EPR pairs on the qubits between Alice and Bob
            index_EPR = self.num_qubits - 2
            for _ in range(num_EPR_pairs + 1):
                qcircuit.h(qreg[index_EPR])
                qcircuit.cx(qreg[index_EPR], qreg[index_EPR - 1])
                index_EPR -= 2

            # Change the basis for the Bell measure
            index_base = self.num_qubits - 1
            for _ in range(num_EPR_pairs + 1):
                qcircuit.cx(qreg[index_base], qreg[index_base - 1])
                qcircuit.h(qreg[index_base])
                index_base -= 2

            # Measure et reset the qubits
            index_meas = self.num_qubits - 1
            while index_meas >= 2:
                qcircuit.measure(qreg[index_meas], creg[index_meas - 2])
                qcircuit.reset(qreg[index_meas])
                index_meas -= 1

            # Apply the X and Z corrections
            index = self.num_qubits - 1
            while index > 2:
                with qcircuit.if_test((creg[index - 3], 1)):
                    qcircuit.x(qreg[1])

                with qcircuit.if_test((creg[index - 2], 1)):
                    qcircuit.z(qreg[1])

                index -= 2

            qcircuit.swap(qreg[1], qreg[0])

            qcircuit.barrier()

        # Alice's operation depending on her input
        if self.Alice_input == 1:
            qcircuit.append(reflection_operator, [0])
        else:
            qcircuit.append(IGate(), [0])

        qcircuit.measure(qreg[0], final_meas_creg)

        counts, output = self.execute_protocol(qcircuit)
        
        return counts, output
    
    def execute_first_protocol(self) -> int:
        """
        This method execute the protocol depending on the chosen type of communication and returns the output.

        Returns:
            int: The output of the AND is 0 or 1.
        """

        if self.type_communication == "cnot":
            self.counts, self.output = self.protocol1_cnot()
        
        else:
            self.counts, self.output = self.protocol1_entanglement()

        print(f"The output for AND({self.Alice_input}, {self.Bob_input}) : {self.output}")

        return self.output
    
    def majority_vote(self) -> None:
        """
        This method displays the output of the logical AND according to a majority vote. The protocol is repeated 3 times and
        the most frequent output is chosen.
        """

        outputs = []
        for _ in range(3):
            output = self.execute_first_protocol()
            outputs.append(output)

        final_output = max(set(outputs), key=outputs.count)

        print(f"The most frequent output for AND({self.Alice_input}, {self.Bob_input}) : {final_output}")
        
        return None
    
    def communication_cost_protocol1(self) -> float:
        """
        This method returns the communication cost of this protocol as described in the following paper
        https://arxiv.org/pdf/1505.03110

        Returns:
            float: The communication cost.
        """

        p = (math.sin(self.theta)) ** 2
        term1 = -p * math.log(p, 2)
        term2 = (1 - p) * math.log(1 - p, 2)

        cost = (self.r + 1) * (term1 - term2)

        return cost
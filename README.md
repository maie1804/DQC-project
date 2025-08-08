# Distributed Quantum Computing Project
## By Elisabeth Mailhot for the Summer 2025 internship

This project contains the functions necessary to compute the logical AND operation between the inputs of two parties, Alice and Bob, using quantum computers. The main goal is to test the communication between Alice and Bob on IBM's hardware to see how it affects the results of the AND operation. The file AND_protocol_1.py contains the first protocol explored which is by Jain, Radhakrishnan, and Sen (https://arxiv.org/pdf/1505.03110). This file contains the methods for the protocol with two types of communication, using control-not gates and entanglement swapping, the protocol using one qubit, a majority vote and the computation of the communication cost. The file AND_protocol_2.py contains the same methods, except on one qubit, but for the protocol by Touchette, Lovitz, and Lütkenhaus (https://arxiv.org/pdf/1801.02771).

To create the project:
1. Create a project using your favorite IDE.
2. Clone the repo.
3. Create a virtual environment using the following command: `python -m venv /path/to/new/virtual/environment`
4. Install the libraries specified in the requirements.txt with the command: `pip install -r requirements.txt`
The project is ready!

To use the project:
1. In the file Functions.py, add to the method execute_backend your token and your instance, if you have one, to access QiskitRuntimeService and use IBM's backend.
2. Follow the notebook Run_protocols.ipynb for more details on how to run the protocols on hardware or simulator.

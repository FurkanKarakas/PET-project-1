# CS-523 Project 1

This is the README.md file for the first project of the Advanced Topics in Privacy Enhancing Technologies class.

## Authors

Furkan Karakaş with student number 306399

Onur Veyisoğlu with student number 309320

## Overview

This project consists of the implementation of 4 parts:

1. **smc_party.py**: This file defines how a participant in the protocol implements the algorithm. The participant is represented as a class called `SMCParty` and its method `run()` is used to implement the logical structure of the algoritm, which data need to be exchanged among participants, etc.
2. **ttp.py**: This file defines the working structure of the "Trusted Third Party". For example, this entity is responsible for providing a Beaver Triplet a, b, and c to the corresponding parties in order to carry out the multiplication operation of two secret values.
3. **secret_sharing.py**: This file defines the structure of the secret values. For instance, we define the `MODULUS` parameter and the computations are carried out in this finite field of integers. It also contains helper functions to split a secret value into multiple secrets and reconstruct a secret value from multiple smaller secrets.
4. **expression.py**: This file defines the semantic nature of the expression to be evaluated by the participants in the protocol. For example, we define helper classes to represent addition, multiplication and subtraction of two expressions. These classes are called `Add`, `Mult` and `Sub`, respectively, which inherit the base class `Expression`.

## Tests

There are various test files defined in the repository. In order to run a test file present in the repository, simply run the following command:

```bash
python3 -m pytest <NAME OF THE TEST FILE>
```

## Benchmarking

For benchmarks, we mainly used the files **test_benchmark.py** and **compute_statistics.py**. When you run the SMC protocol, each participant creates a .txt file, and the computational costs, bytes received and bytes sent are recorded in these .txt files. After doing 25 iterations, we manually call the function in the `compute_statistics.py` file in order to find the statistical information such as min, max, mean, etc. Do not forget to manually delete the .txt files if you want to perform the next performance test.

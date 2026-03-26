"""
Quantum circuit: roll two fair six-sided dice; outcome is the sum (2–12).

Each die uses three qubits in a uniform superposition over basis states |001⟩…|110⟩
(decimal 1–6); |000⟩ and |111⟩ have zero amplitude so every measurement yields 1–6.
"""

from __future__ import annotations

import argparse
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def single_die_state() -> np.ndarray:
    """Uniform amplitude on 3-qubit states encoding 1..6 (binary 001..110)."""
    psi = np.zeros(8, dtype=complex)
    psi[1:7] = 1.0 / np.sqrt(6.0)
    return psi


def build_two_dice_circuit() -> QuantumCircuit:
    """
    Two independent dice: |ψ⟩ ⊗ |ψ⟩ on 6 qubits, then measure all.

    Qubit order (little-endian): die A on q0,q1,q2; die B on q3,q4,q5.
    """
    psi = single_die_state()
    state_2dice = np.kron(psi, psi)

    qc = QuantumCircuit(6, 6)
    qc.initialize(state_2dice, range(6))
    qc.measure(range(6), range(6))
    return qc


def bits_to_die_value(bits: tuple[int, ...]) -> int:
    """3 bits (q0 LSB) -> integer 1..6."""
    return bits[0] + 2 * bits[1] + 4 * bits[2]


def run_once(shots: int = 1, seed: int | None = None) -> tuple[list[int], list[tuple[int, int]]]:
    """
    Execute the circuit; return list of sums and list of (die_a, die_b) pairs.
    """
    qc = build_two_dice_circuit()
    backend = AerSimulator(seed_simulator=seed)
    job = backend.run(transpile(qc, backend), shots=shots)
    counts = job.result().get_counts()

    sums: list[int] = []
    rolls: list[tuple[int, int]] = []

    for bitstring, count in counts.items():
        # Qiskit: bitstring is MSB first (e.g. '000000' = all zeros on classical reg)
        bits = [int(b) for b in bitstring]
        bits.reverse()  # q0 first (LSB convention for int reconstruction)
        a = bits_to_die_value(tuple(bits[0:3]))
        b = bits_to_die_value(tuple(bits[3:6]))
        for _ in range(count):
            sums.append(a + b)
            rolls.append((a, b))

    return sums, rolls


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum two-dice roll (sum 2–12)")
    parser.add_argument("--shots", type=int, default=1000, help="number of samples")
    parser.add_argument("--seed", type=int, default=None, help="simulator seed")
    parser.add_argument(
        "--draw",
        action="store_true",
        help="print the circuit (after transpilation for the simulator)",
    )
    args = parser.parse_args()

    if args.draw:
        qc = build_two_dice_circuit()
        backend = AerSimulator()
        print(transpile(qc, backend).draw(output="text", fold=120))
        print()

    sums, rolls = run_once(shots=args.shots, seed=args.seed)

    # Histogram of sums
    hist: dict[int, int] = {s: 0 for s in range(2, 13)}
    for s in sums:
        hist[s] += 1

    print("Quantum two-dice circuit: uniform 1–6 per die (3 qubits each), sum = 2..12\n")
    print(f"Shots: {args.shots}\n")
    print("Sum | Count | Approx. probability")
    print("----|-------|--------------------")
    for total in range(2, 13):
        c = hist[total]
        p = c / args.shots
        print(f"{total:3d} | {c:5d} | {p:.4f}")

    # Independent single shots for readable samples (histogram uses batched shots)
    _, sample_rolls = run_once(shots=10, seed=(args.seed + 1) if args.seed is not None else None)
    print("\nSample rolls (die_a, die_b) → sum (10 independent shots):")
    for i, (a, b) in enumerate(sample_rolls, 1):
        print(f"  {i}. ({a}, {b}) → {a + b}")


if __name__ == "__main__":
    main()

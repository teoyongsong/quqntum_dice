# Quantum dice

This project demonstrates a **quantum circuit** that models **two fair six-sided dice**. Each measurement gives independent faces **1–6** per die; the **sum** takes every value from **2** through **12**. The implementation uses [Qiskit](https://www.ibm.com/quantum/qiskit) and [Qiskit Aer](https://github.com/Qiskit/qiskit-aer) for simulation.

## Project layout

| File | Purpose |
|------|---------|
| `quantum_two_dice.py` | Command-line simulator: runs the circuit, prints a sum histogram and sample rolls. |
| `streamlit_app.py` | Interactive web UI (Streamlit) that calls the same simulator. |
| `index.html` | Standalone browser page: dice visuals and histogram using the **same statistics** as the circuit (no Python; no Qiskit in the browser). |
| `requirements.txt` | Python dependencies for the CLI and Streamlit app. |

## Requirements

- **Python 3.10+** recommended for the CLI and Streamlit.
- Install dependencies:

```bash
pip install -r requirements.txt
```

Packages include `qiskit`, `qiskit-aer`, `streamlit`, and `pandas`.

## Command-line usage

```bash
python quantum_two_dice.py
```

| Option | Description |
|--------|-------------|
| `--shots N` | Number of simulated measurements (default: 1000). |
| `--seed S` | Aer simulator seed for reproducible runs. |
| `--draw` | Print the transpiled circuit as ASCII (the `Initialize` decomposition can be large). |

Examples:

```bash
python quantum_two_dice.py --shots 20000 --seed 42
python quantum_two_dice.py --draw
```

## Streamlit app

Run the interactive UI locally (same Qiskit + Aer backend as the CLI):

```bash
streamlit run streamlit_app.py
```

Open the URL shown in the terminal (typically `http://localhost:8501`). The sidebar lets you set an optional seed, choose the batch size for “Run batch,” reset the histogram, and expand a text view of the transpiled circuit.

### Deploy on Streamlit Community Cloud

1. Push the repository to a host supported by [Streamlit Community Cloud](https://streamlit.io/cloud) (for example GitHub).
2. Sign in at [share.streamlit.io](https://share.streamlit.io) and create a **New app**.
3. Select the repository and branch; set **Main file path** to `streamlit_app.py`.
4. Deploy. Dependencies install from `requirements.txt`.

If the build fails, inspect the Cloud logs. `qiskit-aer` usually runs on the default Linux image; first-time installs can be slow.

## Browser demo (`index.html`)

Open `index.html` in a modern browser (double-click or `file:///…/index.html`). It shows two dice, the sum, and a histogram. Randomness uses `crypto.getRandomValues` when available. The outcome distribution matches the quantum simulator (uniform **1–6** per die, sum **2–12**); it does **not** execute Qiskit in the browser.

## How the circuit works

- **Six qubits** — three per die. Each die is prepared in a uniform superposition over only the six basis states that encode **1–6** in binary (`001` … `110`). States `000` and `111` have zero amplitude, so every measurement decodes to a valid face.
- **Two dice** — the joint state is **|ψ⟩ ⊗ |ψ⟩**, implemented with `initialize` on six qubits, then all qubits are measured.
- **Statistics** — with many shots, the sum distribution matches **classical** two dice (for example **7** most often, **2** and **12** least often).

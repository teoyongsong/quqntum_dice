"""
Streamlit UI for the quantum two-dice circuit (Qiskit + Aer).
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from qiskit import transpile
from qiskit_aer import AerSimulator

from quantum_two_dice import build_two_dice_circuit, run_once


def _init_state() -> None:
    if "hist" not in st.session_state:
        st.session_state.hist = {s: 0 for s in range(2, 13)}
        st.session_state.total = 0
        st.session_state.last_a = 1
        st.session_state.last_b = 1


def _add_rolls(sums: list[int], rolls: list[tuple[int, int]]) -> None:
    for s, (a, b) in zip(sums, rolls):
        st.session_state.hist[s] += 1
        st.session_state.total += 1
        st.session_state.last_a = a
        st.session_state.last_b = b


def main() -> None:
    st.set_page_config(
        page_title="Quantum two-dice",
        page_icon="🎲",
        layout="wide",
    )
    _init_state()

    st.title("Quantum two-dice")
    st.markdown(
        "Six qubits (three per die): uniform faces **1–6**, then measure. "
        "The **sum** can be **2** through **12** — same model as `quantum_two_dice.py`."
    )

    with st.sidebar:
        st.header("Simulator")
        seed_raw = st.text_input(
            "Random seed (optional)",
            value="",
            placeholder="e.g. 42 — leave empty for non-deterministic",
            help="Set an integer for reproducible Aer simulator runs.",
        )
        seed: int | None = None
        if seed_raw.strip():
            try:
                seed = int(seed_raw.strip())
            except ValueError:
                st.sidebar.error("Seed must be a valid integer.")
        burst = st.number_input(
            'Shots for "Run batch"',
            min_value=1,
            max_value=50_000,
            value=500,
            step=100,
        )
        if st.button("Reset histogram", use_container_width=True):
            st.session_state.hist = {s: 0 for s in range(2, 13)}
            st.session_state.total = 0
            st.session_state.last_a = 1
            st.session_state.last_b = 1
            st.rerun()

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        st.metric("Die A", st.session_state.last_a)
    with c2:
        st.metric("Die B", st.session_state.last_b)
    with c3:
        ssum = st.session_state.last_a + st.session_state.last_b
        st.metric("Sum (2–12)", ssum)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Measure once", type="primary", use_container_width=True):
            sums, rolls = run_once(shots=1, seed=seed)
            _add_rolls(sums, rolls)
            st.rerun()
    with b2:
        if st.button(f"Run {burst} shots", use_container_width=True):
            with st.spinner(f"Running {burst} shots on AerSimulator…"):
                sums, rolls = run_once(shots=burst, seed=seed)
            _add_rolls(sums, rolls)
            st.rerun()

    st.subheader("Sum histogram")
    total = st.session_state.total
    if total == 0:
        st.info("Use the buttons above to measure. Counts appear here.")
    else:
        df = pd.DataFrame(
            {
                "Sum": list(range(2, 13)),
                "Count": [st.session_state.hist[s] for s in range(2, 13)],
            }
        ).set_index("Sum")
        st.bar_chart(df)

        st.caption(
            f"Total measurements: **{total}**. "
            "Classical two-dice shape: peak near **7**, rare **2** and **12**."
        )

    with st.expander("Transpiled circuit (text)"):
        backend = AerSimulator()
        qc = build_two_dice_circuit()
        st.code(transpile(qc, backend).draw(output="text", fold=100), language=None)


if __name__ == "__main__":
    main()

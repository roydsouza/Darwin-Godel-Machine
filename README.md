# Darwin-Gödel Machine (DGM): Self-Referential Evolutionary Research

The Darwin-Gödel Machine is a research laboratory focused on the development of self-referential agentic systems capable of autonomous evolutionary code modification.

## Project Role & Relationships
- **Function**: Implements "Experiment 01" to explore autonomous avenues for hardening system substrates through adversarial selection.
- **Support**: Provides refined detection logic for the **[tachyon_tongs](../tachyon_tongs/)** security suite.
- **Execution**: Utilizes the local MLX-native inference capabilities of **[event-horizon-core](../event-horizon-core/)**.
- **Context**: Methodology for the evolutionary loops is informed by the research conducted in **[madness](../madness/)** and **[bootstrap-paradox-labs](../bootstrap-paradox-labs/)**.

## 🧬 Overview
The DGM operates on the **HyperAgent Principle**: an agent composed of two distinct but self-referential parts:
1. **Task Brain**: The mutable detection logic that classifies incoming attacks (e.g., OWASP ASI categories).
2. **Meta-Agent**: The stable evolutionary engine that analyzes the Brain's performance and rewrites its code using a Local LLM.

## 🚀 How it Works
The evolutionary loop follows a rigorous **Adversarial Selection** process:
1. **Synthesis**: Pathogen (Red Team) generates a fresh batch of mutated agentic attacks.
2. **Evaluation**: The current Task Brain is tested against these attacks to establish a performance baseline.
3. **Evolution**: If accuracy is suboptimal, the Meta-Agent generates a refined version of the Brain's logic.
4. **Governance**: A Human-in-the-Loop review is required before the new "offspring" variant is committed to the archive.

## 💻 Local LLM: MLX Native
To ensure complete autonomy and privacy, this experiment runs **entirely locally** on Apple Silicon via **[MLX](https://github.com/ml-explore/mlx)**. 
- **Model**: Llama-3.2-3B-Instruct (4-bit quantization).
- **Performance**: Leveraging Metal-accelerated GPU inference for near-instant self-modification.
- **Zero-Dependency**: No API keys or internet connection required for the evolutionary loop.

## 📁 Directory Structure
- `src/logic/brain.py`: The currently active evolved logic.
- `archive/`: SQLite database tracking every version and its performance metrics.
- `exploits/`: A local repository of ASI-01 to ASI-11 synthesized exploits.
- `scripts/run_dgm.py`: The main orchestrator for the evolutionary loop.

## 🛠️ Quick Start
Initialize the lab and run focused iterations:
```bash
./scripts/run_dgm.py --iterations 5 --manual-review
```
*For detailed instructions on exploit synthesis, see [exploits/README.md](./exploits/README.md).*

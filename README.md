# Darwin-Gödel Machine (DGM) Lab

> **Experiment 01**: Evolutionary Agent Architecture for Self-Improving Firewalls.

This lab implements a **Darwin-Gödel Machine**, a self-referential agentic system that evolves its own detection logic in response to synthesized attacks. It is the first in a series of "Auto-Research" experiments designed to explore autonomous avenues for hardening the Tachyon Tongs substrate.

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

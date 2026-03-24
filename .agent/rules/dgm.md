# Darwin-Godel Machine Local Rules

These rules apply specifically to code and agents within the `experiments/darwin_godel_machine/` directory.

- **Human-in-the-Loop Modification**: Any self-modification proposed by the Meta Agent MUST be presented to the user for approval. Do NOT overwrite `src/hyperagent.py` without explicit confirmation.
- **Python Comments Required**: All evolved code MUST include human-comprehensible comments explaining the logic and intent.
- **Version Tracking**: Every applied generation MUST be saved into a history/archive correctly before starting the next iteration.
- **Tachyon Tongs Integration**: Prefer reusing existing plugins from `~/antigravity/tachyon_tongs/agents/` rather than re-implementing functionality.
- **Modular First**: Keep all experiment-specific logic within this folder. Do not modify parent directory files unless strictly necessary (e.g., adding a global task in `tachyon_tongs/TASKS.md`).
- **No Signing**: For experiment iterations, cryptographic signing is not required to maintain high-velocity execution.

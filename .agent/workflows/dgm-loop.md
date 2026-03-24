---
description: Run the Darwin-Godel Machine evolutionary loop (1 iteration by default).
---

1. Ensure the user is in the `experiments/darwin_godel_machine/` directory.
2. Run the DGM Orchestrator:
   ```bash
   python scripts/run_dgm.py --iterations 1 --manual-review
   ```
3. Wait for the Meta Agent to propose a modification.
4. Review the diff provided by the orchestrator.
5. If approved, the hyperagent will be updated and evaluated against synthetic attacks from Pathogen.
6. The results will be stored in the local archive and reported via Herald.

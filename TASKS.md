# Darwin-Godel Machine Experiment Tasks

## Phase 1: Infrastructure Initialization [/]
- [x] Initialize directory structure (src, archive, config, scripts, tests) <!-- id: 14 -->
- [x] Implement `src/archive_manager.py` (SQLite based history) <!-- id: 15 -->
- [x] Implement `src/evaluation_engine.py` (Subprocess evaluation) <!-- id: 16 -->
- [x] Implement `src/attack_interface.py` (Integration with Sentinel/Pathogen based on `exploits/`) <!-- id: 17 -->
- [x] Implement `src/detection_interface.py` (Integration with Sentinel/Guardian) <!-- id: 18 -->
- [x] Implement `src/hyperagent.py` (Initial seed from template) <!-- id: 19 -->
- [/] Implement `scripts/run_dgm.py` (Main evolutionary loop with Human-in-the-loop support) <!-- id: 20 -->

## Phase 2: Isolation & Governance [/]
- [x] Define local `.agent/rules/dgm.md` <!-- id: 21 -->
- [x] Define local `/dgm-loop` workflow <!-- id: 22 -->
- [x] Setup Git-based diff history for `hyperagent.py` (via `src/history`) <!-- id: 23 -->

## Phase 3: Baseline Experiment [ ]
- [/] Run Iteration 0 (Initial Seed performance) <!-- id: 24 -->
- [ ] Run first 10 iterations (Manual review mode) <!-- id: 25 -->
- [ ] Evaluate results and emergent strategies <!-- id: 26 -->

## Phase 4: Self-Optimization [ ]
- [ ] Enable metacognitive self-modification <!-- id: 27 -->
- [ ] Monitor Meta Agent improvements <!-- id: 28 -->
- [ ] Compare vs fixed baseline <!-- id: 29 -->

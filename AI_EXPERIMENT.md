# Space Courier: Phase 2 experiment

This is a genuine reinforcement learning run, completed on CPU with PyTorch 2.6.0. The game graphics, controls, spawning, collision radius, scoring, movement speed, and difficulty curve were preserved. No website was built.

## Environment and timing

`ai/environment.py` wraps the existing `game.model.World`. `reset(seed)` returns a fresh float32 observation; `step(action)` returns `(observation, reward, done, info)`. Actions are 0: stay, 1: left, 2: right. Invalid actions and stepping a completed episode raise errors.

Each decision holds its direction for six original 1/60-second physics ticks (10 decisions per simulated second). Collisions are checked every physics tick; repeating actions does not skip collisions. Training has no display or FPS limiter. Rendered inference uses an accumulator and the same six-tick decision cadence. Pause freezes the model's physics too. Observation extraction is shared between training and playback.

Episodes end on collision. A separate 180-second limit bounds experiment runtime; reaching it is a truncation, not a death. Bellman targets bootstrap across truncations, but never across collisions. Playback is not capped at 180 seconds. High scores from human runs are never overwritten by AI playback.

## Every input: 32 numerical features

Four global features:

| Input | Meaning |
| --- | --- |
| player_x / 480 | Current horizontal position |
| (player_x - 25) / 480 | Clearance to the left movement boundary |
| (455 - player_x) / 480 | Clearance to the right movement boundary |
| difficulty | Current game's capped elapsed-time difficulty, 0 to 1 |

Four asteroid slots each contain seven features:

| Input | Meaning |
| --- | --- |
| present | 1 if occupied, 0 if empty |
| x / 480 | Current asteroid horizontal position |
| (x - player_x) / 100 | Current relative horizontal separation |
| (565 - y) / 640 | Current vertical gap to player |
| radius / 40 | Collision radius scaled to typical size |
| speed / 300 | Current falling speed |
| y / 640 | Current vertical position |

Slots are ordered by absolute current vertical distance to the player. Asteroids entirely below the player's collision circle are omitted. Missing slots are all zero. Values are scaled rather than universally clipped to [0, 1]: horizontal separation may exceed 1, and asteroid y can be negative when it has just spawned. Player velocity is unnecessary because movement is instantaneous at a fixed speed for each action.

The model gets no RNG state, spawn timer, future asteroid positions, predicted safe direction, screenshots, or scripted action labels. It can observe current approaching rocks, just as a human can.

## Network and learning

Architecture: **32 → 128 ReLU → 128 ReLU → 3 Q-values**.

The implementation uses Double DQN: the online network selects the next action, and the frozen target network supplies its estimated value. It trains from randomly sampled replay transitions using Adam, Huber loss, and gradient clipping. This follows the replay/target-network approach described in the [official PyTorch DQN tutorial](https://docs.pytorch.org/tutorials/intermediate/reinforcement_q_learning.html), with separate online action selection to reduce overestimation.

Reward is deliberately simple:

- +1/6 for each simulated physics tick, giving +1 for a complete living action.
- +0.5 when an asteroid fully passes the player's collision zone, once per crossing.
- -20 on collision, in addition to the fraction of time advanced that action.

There are no position rewards, bonuses for a prescribed direction, or near-miss exploitation incentives. Staying alive is the main source of reward. Reward is not identical to displayed game score; the game's existing score remains 100 points per survival second.

| Setting | Value |
| --- | --- |
| Training seed | 42 |
| Learning rate | 0.0003 |
| Discount gamma | 0.99 per decision |
| Batch size | 128 |
| Replay capacity | 50,000 transitions |
| Warmup | 3,000 decisions |
| Gradient update | Every 4 decisions |
| Target synchronization | Every 2,000 decisions |
| Gradient norm clip | 10 |
| Exploration | Linear 1.0 → 0.05 over 120,000 decisions, then 0.05 |
| Checkpoint/validation interval | 25,000 decisions |
| Validation games | 20, fixed seeds 200000–200019 |
| Evaluation games | 100, fixed seeds 100000–100099 |
| Episode limit | 180 simulated seconds |

Training resets use random seeds below 90000, separate from validation and evaluation. Replay sampling and epsilon actions use separate NumPy generators. Evaluation is greedy (epsilon=0). Obstacles have matching seeds for random and learned comparisons; random actions use an independent generator.

## Actual training record

One complete experiment ran for **250,000 decisions and 1,059 completed episodes**, with a final unfinished episode excluded from the episode CSV. Training plus validation and final evaluation took approximately **138 seconds** on this CPU. This is not 60-FPS wall-clock gameplay: the run averaged around 1,900 decisions per second including validation overhead.

The untrained network and checkpoints every 25,000 decisions are preserved. The selected model is from **150,000 decisions**, after 833 completed episodes plus part of the next one. It scored 7,920.75 on validation. The final 250,000-decision network scored 6,166.25 on validation, so it remains available as `final_model.pth` but is not the default playback model.

| Decisions | Validation mean score |
| --- | ---: |
| 25,000 | 1,758.80 |
| 50,000 | 4,647.55 |
| 75,000 | 4,352.20 |
| 100,000 | 5,019.25 |
| 125,000 | 6,568.50 |
| 150,000 | 7,920.75 |
| 175,000 | 5,305.95 |
| 200,000 | 4,511.60 |
| 225,000 | 5,275.10 |
| 250,000 | 6,166.25 |

No failed training runs or hyperparameter changes were hidden: the first full run met the performance requirement. Its significant issue was non-monotonic DQN performance after 150,000 decisions. The response was to select checkpoints by validation mean, using a separate final test set, rather than assume the latest weights were best. Epsilon remains 0.05 during late training, so training curves measure exploratory play and need not match greedy evaluation scores.

The original experiment directory is retained verbatim. The delivered CSV includes a derived checkpoint annotation identifying actual saves between episode boundaries; all numeric measurements are unchanged. New runs record that association directly.

## Final held-out evaluation

| Metric | Random agent | Selected DQN |
| --- | ---: | ---: |
| Games | 100 | 100 |
| Mean score | 873.50 | 7,311.00 |
| Median score | 778.50 | 7,731.00 |
| Minimum score | 453 | 621 |
| Maximum score | 2,075 | 18,000 |
| Sample standard deviation | 367.78 | 4,257.00 |
| Mean survival seconds | 8.74 | 73.12 |
| Games reaching 180-second cap | 0 | 2 |

Mean score improvement is **8.37×**. The capped scores are lower bounds on how long those two runs could survive. This is still a fallible agent: the minimum score shows an early crash, and performance varies considerably across obstacle sequences.

Additional controls on the same 100 seeds averaged 1,202.17 points for always staying, 1,933.27 for always holding left, and 1,714.60 for always holding right. The DQN substantially exceeds these simple strategies too. On evaluation seed 100002 it survived to score 9,513 and selected stay 532 times, left 198 times, and right 222 times. A full current-state/action trace is preserved, demonstrating that the policy does not simply stay at one edge.

## Files and commands

| Path | Contents |
| --- | --- |
| `ai/environment.py` | Original-world adapter and observation schema |
| `ai/model.py`, `ai/agent.py` | Network, action selection, updates, save/load |
| `ai/replay_buffer.py` | Bounded replay memory |
| `ai/train.py`, `ai/evaluate.py` | Headless training and paired evaluation |
| `ai/playback.py` | Fixed-tick rendered model inference |
| `ai/plots.py` | Charts from real episode CSV |
| `models/best_model.pth` | Selected trained network plus target and optimizer |
| `models/final_model.pth` | Last trained network |
| `models/checkpoints/` | Untrained plus ten intermediate checkpoints |
| `models/model_metadata.json` | Observation schema, hyperparameters, run totals, results |
| `data/training_history.csv` | Completed episodes, scores, rewards, averages, losses, epsilon, steps, duration, checkpoints |
| `data/validation_history.json` | Model-selection measurements |
| `data/random_baseline.json`, `data/evaluation_results.json` | Aggregate statistics and all 100 individual games |
| `data/behavior_diagnostics.json`, `data/playback_trace.json` | Constant-policy controls and model behavior trace |
| `data/run_config.json`, `data/comparison.json` | Reproducibility settings and comparison |
| `results/` | Score, trailing-50 mean, loss, and epsilon PNG graphs |
| `experiments/run_01/` | Original run artifacts |
| `tests/test_ai.py` | Environment, replay, learning, synchronization, save/load, playback parity, modes |

From the `pixel-panic` directory:

```sh
python -m pip install -r requirements-ai.txt
python main.py                     # Human game; I on title watches AI
python main.py --ai                # Watch selected model
python main.py --ai --debug        # Optional Q-value overlay
python main.py --ai --model models/checkpoints/step_0050000.pth
python -m ai.train --steps 250000 --output experiments/run_02
python -m ai.train --steps 5000 --validate-every 5000 --output experiments/debug --render
python -m ai.evaluate --model models/best_model.pth --episodes 100 --output results/recheck
python -m unittest discover -s tests -v
```

Training refuses to overwrite an existing episode-history file. Evaluation should also use a fresh output directory when preserving past results matters. Saved optimizer and target states can be loaded with `Agent.load(path, training=True)`; the command-line trainer starts a new experiment rather than promising an exact resume. Replay contents, environment state, and RNG positions are not checkpointed, so checkpoints are not exact full-run snapshots. Ctrl+C saves the current weights and completed episode history, then performs final evaluation and plotting.

## Verification and possible next improvements

Tests cover deterministic resets, bounded movement, all actions, observation format, collision termination, time-limit truncation, once-only pass reward, replay wraparound and samples, actual parameter updates, frozen target weights and synchronization, checkpoint round-trips, greedy evaluation, fixed-tick playback equality, ten repeated AI restarts, unchanged human score storage, and switching back to human mode. The existing human-game regression tests also pass.

A separate 3,100-decision rendered trainer smoke run is retained in `experiments/trainer_smoke/`; it verified the final training CLI, real weight updates after warmup, checkpoint generation, metrics, evaluation, and plotting. Its 32 completed episodes are not part of the reported full experiment. An independent evaluation in `results/recheck/` reproduced both saved 100-game datasets exactly. The selected policy beat random play on 95 of the 100 paired games.

Before Phase 3, useful improvements include several independent training seeds to measure robustness, larger validation sets to reduce selection noise, evaluation beyond the current time cap, and analysis of early-crash trajectories. Screenshot-based learning would be a separate future experiment. The website has not been started.

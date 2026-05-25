# synthetic_blow review

Generated: 2026-05-24

Scope: full repository/package review after the v0.5.0 partition-tower and
post-Young-diagram evaluation-environment repair work.

Review lens: I am reviewing this through a Jonathan-Blow-inspired lens: direct,
performance-aware, skeptical of unnecessary abstraction, data-first, and focused
on reducing accidental complexity. This is not Jonathan Blow and does not claim
endorsement by him.

Validation observed during review:

```text
uv run ruff check .                         -> All checks passed
uv run mypy src                             -> Success: no issues found
uv run pytest                               -> 354 passed
uv run coverage report -m                   -> 93% total coverage
```

## Verdict

This repository is much more real than a typical research scaffold: the package
has typed surfaces, a serious test suite, a partition-backed tower runtime, and
multiple examples that actually run. But it is not yet trustworthy as an RL
training package. The tower machinery is ahead of the training machinery. The
highest-risk problems are not style problems; they are silent RL correctness and
runtime-scaling problems: bootstrapping semantics are wrong or inconsistent,
action masks are treated as optional decoration rather than part of the target
calculation, "serializable" snapshots contain live mutable runtime objects, and
the supposedly local partition runtime still rebuilds full compatibility
readouts on every update. The code is solid enough for research iteration, but
not yet solid enough for strangers to trust training results without reading the
source.

## Program map

- Entry point: package import is intentionally tiny in `src/state_collapser/__init__.py`; practical entry points are README examples, `run_tower_training(...)` in example packages, and `state_collapser.examples.tower_depth_probe`.
- Training loop: generic reference loops live in `src/state_collapser/training/reference_loops.py`; most mechanical examples still have local copy-pasted tabular loops in `src/state_collapser/examples/*_env/training.py`; `rl_counterpoint_v3` uses the generic loop.
- Evaluation loop: no serious evaluation loop exists yet. `tower_depth_probe` is a structural probe, not policy evaluation.
- Environment boundary: Gymnasium-compatible example envs live in `src/state_collapser/examples/*_env/env.py`; runtime wrappers live in each example's `runtime.py`.
- Model/update code: there is no PyTorch model path yet. Current learning is tabular Q-style code in `src/state_collapser/training/learners.py` and per-example training files.
- Replay/rollout storage: generic collection uses `CollectedStep`, `CollectedEpisode`, and `TrainingTransition`; `TabularQLearner` stores an unbounded Python `list[TrainingTransition]`.
- Config: small dataclass configs in example training files; no Hydra/config-framework layer, which is good at this stage.
- Checkpoints/logs: no checkpoint, resume, run manifest, or artifact logging surface exists.
- Tests: broad and useful. Current suite covers core graph/tower invariants, environment contracts, schema behavior, probe behavior, and training smoke paths. It does not yet cover RL target semantics, action-mask target semantics, serialization, or performance budgets.

## The real data path

Representative path for `rl_counterpoint_v3`:

- `RlCounterpointEnv.reset(...)` returns an `np.ndarray` observation with dtype `int64` plus an `info` dict containing state, history, action mask, and action-space metadata at `src/state_collapser/examples/rl_counterpoint_v3/env.py:709` and `src/state_collapser/examples/rl_counterpoint_v3/env.py:791`.
- `RlCounterpointEnv.step(action)` accepts an integer action, applies `primitive_transition`, returns `(observation, reward, terminated, truncated, info)` at `src/state_collapser/examples/rl_counterpoint_v3/env.py:723`.
- `RlCounterpointEnvRuntime.step(action)` forwards the action to the env, steps `TowerRuntime`, and packages the env result plus runtime snapshot at `src/state_collapser/examples/rl_counterpoint_v3/runtime.py:278`.
- `StepCollector.reset_episode(...)` and `StepCollector.collect_step(...)` build `ActionSelectionInput` objects from observations and runtime snapshots at `src/state_collapser/training/collectors.py:92` and `src/state_collapser/training/collectors.py:123`.
- `ActionSelectionInput` carries `observation: object`, `current_base_state`, `runtime_snapshot`, `tower_position_key`, and optional `action_mask` at `src/state_collapser/training/inputs.py:17`.
- `TabularQLearner.act(...)` chooses an epsilon-greedy integer action over its Q row at `src/state_collapser/training/learners.py:63`.
- `TrainingTransition` stores source input, chosen action, reward, target input, terminated, truncated, diagnostics, and tower metadata at `src/state_collapser/training/transitions.py:36`.
- `TabularQLearner.update(...)` updates from only the last transition in an unbounded replay list at `src/state_collapser/training/learners.py:105`.

Visible contracts:

- Observation shape/dtype: visible in envs, usually `np.ndarray` with `int64`.
- Action shape/dtype: mostly `int`, but several envs cast instead of validate.
- Device: CPU only. No tensor/device surface is implemented yet.
- Autograd: none in current package code.
- Copies/ownership: runtime snapshots pass live graph/tower objects by reference, not copies.
- Unknowns: no manifest, no checkpoint payload, no reproducibility artifact, no benchmark artifact.

## Highest-severity issues

### 1. Terminal/truncated bootstrapping semantics are wrong or inconsistent

- Severity: blocker
- Location: `src/state_collapser/training/learners.py:117`, `src/state_collapser/examples/articulated_loop_env/training.py:109`, `src/state_collapser/examples/plate_support_env/training.py:245`, `src/state_collapser/examples/cable_parallel_env/training.py:101`, `src/state_collapser/examples/dual_arm_manipulation_env/training.py:116`, `src/state_collapser/examples/parallelogram_singularity_env/training.py:106`
- Problem: the generic `TabularQLearner` zeroes bootstrap when `terminated or truncated`; the per-example loops go the other direction and always bootstrap before checking either flag. Both choices are wrong as a package default. Termination and truncation are different RL events. A true terminal transition should usually zero bootstrap. A time-limit truncation often should not zero bootstrap unless the caller intentionally wants episodic time-limit semantics. The mechanical example loops also bootstrap terminal success states, which contaminates terminal targets.
- Why it matters: this silently changes Q targets. The result can look like "RL is noisy" when the actual problem is the target calculation. This is exactly the sort of bug that invalidates training claims while leaving tests green.
- Fix: make bootstrap semantics explicit in the transition/update surface.

Patch sketch:

```python
@dataclass(frozen=True, slots=True)
class BootstrapSemantics:
    bootstrap_on_truncation: bool = True

def bootstrap_allowed(terminated: bool, truncated: bool, semantics: BootstrapSemantics) -> bool:
    if terminated:
        return False
    if truncated:
        return semantics.bootstrap_on_truncation
    return True
```

Then in `TabularQLearner.update(...)`:

```python
allowed = bootstrap_allowed(
    transition.terminated,
    transition.truncated,
    self.bootstrap_semantics,
)
bootstrap = max_next_q if allowed else 0.0
```

The copied example loops should either use the generic learner or apply the same
function before computing `td_target`.

Tests that should exist:

- terminal transition gives `td_target = reward`
- truncated non-terminal transition bootstraps by default
- truncated non-terminal transition can be configured not to bootstrap
- all example training loops share the same target semantics

#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that the learner needs to know whether there is still
"future value" after the transition it just observed. Bootstrapping is exactly
the act of saying: "this step gave me reward now, and I should also include my
estimate of what can still be earned later." That is correct when the episode
was merely cut off by an administrative limit, but it is wrong when the task
really ended.

Right now the codebase has two incompatible instincts. The generic learner says
"if the episode stopped for any reason, there is no future." Some example loops
say "there is always future value, even after a true terminal state." Both can
produce clean-looking runs and still give the learner the wrong training target.
So the package needs one explicit contract: for this transition, is
bootstrapping allowed or not? Once that is explicit, the learner no longer has
to guess what `terminated` and `truncated` mean.

#### PO Follow-up:
I see. Tell me if this modifies your thinking: How this "should" work is entirely dictated, I think, by the logic of lifts. Specifically, terminatation at tier-$(i+1)$ does not mean process stops dead there. There is still the possiblity of further forward action at tier-$i$.

#### LLM Follow-up:
Yes, this modifies and sharpens the review. The original complaint is still
right for ordinary Gymnasium episode semantics, but it is too flat for this
package. In `state_collapser`, "terminated at tier $(i+1)$" and "the whole
environment episode is over" are not the same statement. A tier can be done as a
quotient-level decision problem while the lifted/base process still has legal
forward motion at tier $i$.

So the more correct package-level contract is not merely
`terminated/truncated -> bootstrap or not`. It is: what is the next valid
decision surface after this transition? If the top or quotient tier has no
further action but the lift resolves to a lower-tier/base continuation, then the
transition should still be allowed to bootstrap from that lower decision
surface. In other words, the learner should not infer continuation semantics
from a raw Boolean alone.

This points to a better design than the first patch sketch: keep Gymnasium
`terminated` and `truncated` as external episode facts, but add package-native
continuation metadata. Something like `bootstrap_allowed`,
`bootstrap_surface`, or even `target_decision_input` should be computed by the
collector/runtime after lift resolution. Then the learner trains against the
actual next decision surface, not against a guessed interpretation of
`terminated` at one tier.

#### PO Response:
Correct.

### 2. Action masks exist but are not part of the default learner target path

- Severity: high
- Location: `src/state_collapser/examples/rl_counterpoint_v3/env.py:796`, `src/state_collapser/training/collectors.py:92`, `src/state_collapser/training/collectors.py:123`, `src/state_collapser/training/learners.py:74`, `src/state_collapser/training/learners.py:117`
- Problem: `RlCounterpointEnv` computes an `action_mask` in `info`, but the default collector does not extract it. `StepCollector` only attaches an action mask if the caller supplied an `action_mask_factory`. The learner respects a mask during action selection if one is already present, but its update bootstraps over `max(next_row.values())`, which includes every action, including invalid target-state actions.
- Why it matters: this breaks the decision surface the package says it is building. In constrained RL environments, masks are not decoration; they define the legal action surface. Bootstrapping through invalid actions can overestimate bad or impossible continuations. Collecting invalid actions as negative samples can be useful, but that should be explicit, not an accidental consequence of losing the mask.
- Fix: make masks first-class in the runtime-to-training contract.

Patch sketch:

```python
def mask_from_info(info: Mapping[str, object]) -> tuple[bool, ...] | None:
    mask = info.get("action_mask")
    if mask is None:
        return None
    return tuple(bool(item) for item in mask)
```

Then:

- `StepCollector.reset_episode(...)` should use `action_mask_factory` if provided, otherwise extract `info["action_mask"]` when present.
- `StepCollector.collect_step(...)` should reject `decision.chosen_action` when the source input has a mask and the chosen action is masked off.
- `TabularQLearner.update(...)` should compute target bootstrap over legal target actions only:

```python
allowed_next = legal_actions(transition.target_input.action_mask, self.action_count)
bootstrap = max(next_row[action] for action in allowed_next) if allowed_next else 0.0
```

Tests that should exist:

- collector picks up `action_mask` from runtime `info`
- collector rejects masked-off chosen actions
- learner action selection never chooses masked-off actions
- learner bootstrap ignores masked-off target actions
- no-legal-actions target state is handled intentionally


#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that in constrained RL, the action space is not just
"all possible integers." At each state, the real decision surface is the subset
of actions that are legal there. The action mask is the package's way of saying:
"these choices exist at the interface, but only these ones are actually allowed
right now."

The environment already knows this, but the training pipeline does not treat it
as part of the core contract. It may use the mask when choosing an action, but
then ignore the mask when estimating the value of the next state. That is like
training a chess agent while letting the value function imagine illegal future
moves. The fix is not cosmetic: masks need to travel with the transition and
constrain both action selection and target computation.

#### PO Follow-up:
I fully support this assessment.

### 3. The partition runtime still pays global readout costs on every update

- Severity: high
- Location: `src/state_collapser/tower/runtime.py:336`, `src/state_collapser/tower/partition/readout.py:23`, `src/state_collapser/tower/partition/readout.py:25`, `src/state_collapser/tower/partition/readout.py:36`, `src/state_collapser/tower/partition/tower.py:281`, `src/state_collapser/tower/partition/tower.py:451`
- Problem: the new partition tower is structurally local, but the runtime still rebuilds full `QuotientTierView` compatibility readouts after every partition update. `to_quotient_tier_views(...)` loops over every tier, every registered state, and active action collections. `update_with_delta(...)` also captures a full morphism domain before mutation. That is not fatal for small tests, but it is exactly the kind of compatibility tax that eats the speedup the refactor was supposed to unlock.
- Why it matters: this can turn "amortized local maintenance" back into "do a bunch of full scans every step." The code can be mathematically better and still operationally slow because the hot path keeps rebuilding views for old consumers.
- Fix: separate hot runtime state from debug/readout compatibility state.

Concrete rewrite:

- Keep `PartitionTower` as the authoritative runtime object.
- Make `RuntimeSnapshot.current_position_at_every_tier` come directly from partition cell ids.
- Stop eagerly assigning `self._quotient_tiers = self._partition_tower.to_quotient_tier_views()` in the hot path.
- Add `TowerRuntime.compatibility_quotient_tiers()` or `snapshot(include_quotient_readout=True)` for tests/debugging.
- Make morphism construction optional:

```python
def update_with_delta(..., build_morphism: bool = False) -> TowerUpdateResult:
    morphism_domain = self._capture_morphism_domain() if build_morphism else None
```

Tests/benchmarks that should exist:

- benchmark incremental update with readout disabled
- benchmark incremental update with readout enabled
- benchmark probe throughput as discovered graph grows
- assert the default runtime path does not call full readout construction


#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that the Young-tableaux refactor changed the intended
runtime model from "rebuild the quotient tower" to "maintain partition tables
locally." That is the whole performance win. But after doing the local update,
the current runtime still eagerly reconstructs old-style quotient readout views
for compatibility.

So the code has the right new internal structure, but then it pays an old global
cost anyway. It is like updating one row in a database and then exporting the
entire database after every write because an older API wants a full report. That
may be fine for debugging or tests, but it should not be the default hot path.
The default runtime path should preserve the local-update story; full quotient
views should be requested explicitly when someone actually needs them.

### PO Follow-up:
I fully support this assesement.

### 4. `RuntimeSnapshot` says serializable but carries live mutable runtime objects

- Severity: high
- Location: `src/state_collapser/tower/snapshot.py:13`, `src/state_collapser/tower/snapshot.py:18`, `src/state_collapser/tower/snapshot.py:19`, `src/state_collapser/tower/snapshot.py:27`, `src/state_collapser/tower/runtime.py:112`, `src/state_collapser/tower/runtime.py:177`
- Problem: `RuntimeSnapshot` is documented as a "Serializable runtime handoff object", but it stores live `ExploredGraph`, live `VistaGraph`, live `PartitionTower`, and raw `TowerUpdateResult` objects. These are mutable object graphs, not stable serialized facts. A user can keep a snapshot from time `t`, step the runtime, and the snapshot's graph references now point at later state.
- Why it matters: this destroys reproducibility and makes debugging dishonest. A snapshot should either be a frozen value object or it should be named as a live view. Right now it claims the former and implements the latter.
- Fix: split the concept.

Concrete rewrite:

- Rename the current object to `RuntimeView` or `LiveRuntimeSnapshot`.
- Create a real serializable `RuntimeSnapshot` containing only value data:
  - current base-state identity
  - discovered state/edge ids
  - current tower positions
  - reward summaries
  - update diagnostics
  - optional compact partition ids
- Add `to_dict()` / `from_dict()` only once the schema is stable.
- Add tests:
  - `json.dumps(snapshot.to_dict())` succeeds
  - old snapshot does not change after `runtime.step(...)`
  - no live graph object is stored in the serializable snapshot

#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that a "snapshot" should be a photograph, but the
current object is more like a live camera feed. It says "serializable handoff,"
but it contains references to mutable runtime objects. If the runtime advances,
an old snapshot can still point into the advanced world.

That matters because training and debugging depend on being able to say: "this
is exactly what the agent saw at time `t`." If the object can change underneath
you, logs, replay records, checkpoints, and bug reports become slippery. The
right split is simple: keep a live runtime view for internal convenience, and
create a separate real snapshot that contains only stable value data.

#### PO Follow-up
I fully support this assessment.

### 5. Loop policy alternatives are mostly nominal, and one path hard-codes the default

- Severity: medium
- Location: `src/state_collapser/tower/partition/loop_policy.py:16`, `src/state_collapser/tower/partition/action_layer.py:123`, `src/state_collapser/tower/partition/action_layer.py:128`, `tests/tower/partition/test_loop_policy.py:18`
- Problem: the package exposes `DROP_INTERNAL`, `AGGREGATE_INTERNAL`, and `FORMAL_STUTTER`, but current behavior records internal edges and mostly treats all policies the same. Worse, `ActionPartitionLayer.carry_forward_from(...)` reconstructs inherited internal-edge records with `LoopPolicy.drop_internal()` hard-coded, ignoring a caller's configured policy.
- Why it matters: this is stringly promise inflation. It gives the impression that loop/stutter semantics exist when the implementation is not yet there. If downstream reward aggregation starts depending on policy names, this becomes a real bug.
- Fix:
  - Pass `loop_policy` into `carry_forward_from(...)`.
  - Add a test that `LoopPolicy.aggregate_internal()` survives carry-forward and incremental updates.
  - Either implement distinct semantics for aggregate/stutter or remove those named constructors until they are real.



#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that the public API currently advertises more loop
semantics than the implementation really owns. A loop policy is supposed to say
what happens to edges that become internal after contraction: drop them,
aggregate them, or remember them as formal stutters. Those are genuinely
different mathematical choices.

But the code mostly treats the alternatives as names, and one carry-forward path
hard-codes the default. That creates fake configurability: a caller can appear
to choose a policy without actually getting different behavior. This is exactly
the kind of abstraction that should either be implemented and tested or kept out
of the public surface until it is real.

#### PO Follow-up
I fully support this assessment. The other possiblitiy for loops we should implement is aggregation over pre-image loops, `avg` or `max`. Does this fit with your thinking?

#### LLM Follow-up:
Yes, this fits exactly, and I would separate it from the simple loop-policy
question. There are really two different choices hiding under the word "loop":

- whether internal/pre-image loops are retained as data after contraction
- how retained pre-image loop data is aggregated into the quotient-level signal

The second choice is the one you are pointing at. `avg` says "what is the
typical lifted behavior inside this contracted cell?" `max` says "what is the
best available lifted behavior inside this contracted cell?" Those are both
legitimate, but they answer different RL questions. For many control problems,
`max` is more natural because the quotient policy wants to know what the best
lift can achieve, not what a random lift achieves.

So I would not bury this inside a string-valued `LoopPolicy`. I would make it an
explicit aggregation surface, probably adjacent to reward/value aggregation:
`PreimageLoopAggregator`, `InternalEdgeAggregator`, or a more general
`QuotientAggregator`. It should support at least `sum`, `mean`, `max`, and
eventually soft/p-norm style choices such as log-sum-exp. That preserves the
mathematical point: quotient contraction creates fibers/pre-images, and the
package must say how information over those fibers is pushed downstairs.

#### PO Response:
I fully support this.

### 6. Several Gymnasium environments coerce actions instead of validating them

- Severity: medium
- Location: `src/state_collapser/examples/articulated_loop_env/env.py:294`, `src/state_collapser/examples/cable_parallel_env/env.py:349`, `src/state_collapser/examples/dual_arm_manipulation_env/env.py:397`, `src/state_collapser/examples/parallelogram_singularity_env/env.py:269`; contrast with `src/state_collapser/examples/plate_support_env/env.py:413`
- Problem: four example envs call `primitive_transition(self.state, int(action))` without first checking `self.action_space.contains(action)`. This means values like `1.9`, `True`, or NumPy scalar oddities can be silently coerced to a valid action. `PlateSupportEnv` does the right thing and checks the action space first.
- Why it matters: environment boundaries need to be boring and strict. Silent coercion creates training bugs that look like policy behavior, especially once wrappers or model outputs enter the picture.
- Fix:

```python
if not self.action_space.contains(action):
    raise ValueError(f"Unsupported action index: {action}")
action_index = int(action)
```

Tests that should exist for every env:

- `env.step(-1)` raises
- `env.step(ACTION_COUNT)` raises
- `env.step(1.9)` raises
- `env.step(True)` is either explicitly accepted or explicitly rejected

#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that the environment boundary should be strict about
what counts as an action. In RL, the environment is the source of truth for the
action space. If it silently turns `1.9` into `1`, or `True` into `1`, then the
agent may appear to be taking valid actions while the boundary is quietly
rewriting them.

That kind of permissiveness is convenient for toy code but bad for training
infrastructure. Once policies, wrappers, masks, tensors, and logged actions are
involved, silent coercion makes bugs look like model behavior. The env should
first ask "is this action actually in my action space?" and only then convert it
to the internal representation.

#### PO Follow-up
I fully support this assessment.

### 7. The "Gymnasium adapter" is not actually a Gymnasium environment

- Severity: low
- Location: `src/state_collapser/adapters/gymnasium.py:14`, `src/state_collapser/adapters/gymnasium.py:26`, `src/state_collapser/adapters/gymnasium.py:32`
- Problem: `GymnasiumAdapter` has Gymnasium-shaped `reset` and `step` methods, but it is not a `gymnasium.Env`, has no `action_space`, has no `observation_space`, and does not accept Gymnasium-style `seed` or `options` on `reset`. The real example envs are much more honest Gymnasium surfaces than this adapter.
- Why it matters: the name overclaims. A user looking for Gymnasium integration may start here and get the weakest integration path.
- Fix: either delete it, rename it to `RobotConstraintRuntimeAdapter`, or make it an actual `gymnasium.Env` with spaces and seeding semantics.

#### PO Follow-up
I need more detail here. This is really getting at this 3-worlds thing that underlies all the thinking on this project. The problem is that even if I understand what you're saying, assessing how correct it is sort of requires getting a clear picture of what kind of gymnasium "thing" an RL engineer might bring to `state_collapser`. If that thing is always a `gymansium` environment, then I'm confused abotu your complaint here. Do you see my confusion?

#### LLM Follow-up:
Yes, I see the confusion, and I think the review needs this qualification. If an
RL engineer brings something to `state_collapser`, the most natural thing they
bring is indeed a `gymnasium.Env`. That part is not the problem. In fact, that
is probably the right default outsider-facing posture.

The problem is the direction and honesty of the adapter. There are three worlds
that need to stay distinct:

- the external environment world, where Gymnasium owns `reset`, `step`,
  observations, actions, rewards, termination, and truncation
- the `state_collapser` structural world, where the package owns discovered
  graph state, vistas, partition towers, quotient cells, lift resolution, and
  cross-tier position
- the training/model world, where a learner consumes decision inputs, masks,
  tower context, rewards, and targets

An RL engineer bringing a Gymnasium env is bringing the first world. The package
then needs an adapter that constructs or maintains the second world on top of
that env, and exposes clean inputs to the third world. That adapter may itself
look like a Gymnasium wrapper, or it may be a runtime object sitting beside the
env. Both are reasonable.

My complaint about the current `GymnasiumAdapter` is narrower: the name suggests
one of those serious integration roles, but the implementation is only a toy
object with Gymnasium-shaped `reset` and `step` methods. It does not wrap an
arbitrary `gymnasium.Env`; it does not subclass `gymnasium.Env`; it does not
define spaces; and it does not clarify whether it is world-one-facing,
world-two-facing, or world-three-facing. So the issue is not "Gymnasium is the
wrong thing." The issue is that this particular adapter does not yet express the
real three-world boundary clearly enough.

The better public surface is probably something like
`StateCollapserGymWrapper` or `TowerAugmentedEnv` for the case where a user
brings an existing Gymnasium env, plus a separate lower-level runtime adapter
for package-native hidden graphs. That would make the architecture legible:
Gymnasium remains the environment shell, while `state_collapser` adds the graph
and tower machinery rather than pretending Gymnasium already contains it.

#### PO Response
Yes I completely agree now that I understand. This may be the part of your code review that needs the biggest discussion. My main concern is how complex this `StateCollapserGymWrapper` or `TowerAugmentedEnv` is going to be. How specific is its function to the details of the `state_collapser` package? How generic of a piece of code is it? How complex are the problems it has to solve?

#### LLM Reply:
Yes, this is exactly the right concern. The wrapper should not be a giant magic
object. If it tries to infer the whole `state_collapser` ontology from an
arbitrary Gymnasium env, it will become overcomplicated and dishonest very fast.
The clean design is to make the wrapper generic in plumbing, but explicit about
the problem-specific hooks it needs.

The generic part is fairly small:

- call `env.reset(...)` and `env.step(...)`
- read observations, rewards, `terminated`, `truncated`, and `info`
- maintain the discovered transition graph from observed `(state, action,
  next_state)` events
- update the partition/tower runtime from newly discovered graph data
- attach tower context, masks, and diagnostics to the returned `info` or to a
  separate training-facing runtime view

The non-generic part is where we must not pretend. A Gymnasium observation is
not automatically a mathematical state. An action object is not automatically a
stable edge label. An `info` dict may or may not contain legal-action masks,
ground-truth state, graph labels, or enough metadata to construct quotient
schemas. So a serious wrapper needs user-supplied hooks such as:

- `state_key(observation, info)`: what object should be treated as the graph
  state?
- `action_key(action, observation, info)`: what should be recorded as the edge
  action?
- `action_mask(info, env)`: which actions are legal at this decision point, if
  the env exposes that?
- `edge_labeler(s, a, s_next, info)`: what labels/contraction features does this
  transition carry?
- `contraction_schema`: how should edges be partitioned into quotient tiers?
- optional `vista_provider` or `model_provider`: does the env expose local
  outgoing structure beyond the single sampled transition?

That last distinction is crucial. If the RL engineer brings an ordinary opaque
Gymnasium env, `state_collapser` can only build an empirical discovered graph
from actually observed transitions. It cannot know unseen outgoing edges unless
the environment or an adapter hook exposes a model/vista. If the engineer brings
a transparent discrete env, or a package-native env with `out_edges(...)`, then
the wrapper can build much richer local vistas. Those are different operating
modes, and the code should name them honestly.

So my updated recommendation is: do not build one enormous
`StateCollapserGymWrapper` that tries to solve everything. Build a small generic
Gymnasium bridge plus typed hook/config objects. The bridge handles trajectory
plumbing and tower updates. The hooks handle semantic interpretation. That keeps
the wrapper professional: generic where Gymnasium is generic, package-specific
where the tower machinery is package-specific, and explicit wherever the env's
meaning cannot be inferred automatically.

#### PO Question:
Ok I like this very much. One important question, then, is how standard this suite of named things (`state_key(observation, info)`, `action_key(action, observation, info)`, `action_mask(info, env)`, `edge_labeler(s, a, s_next, info)`) is in a general `gymnasium`-formulated RL problem? This doesn't mean the engineer has to have them pre-formulated. It means something more like: For a general RL problem formulated in `gymnasium`, could the RL engineer who set of the `gymnasium` formulation easily name these object when asked, i.e., could an engineer at least set this up if need?"

#### LLM Answer:
Yes, mostly. The exact hook names are not standard Gymnasium vocabulary, but the
objects they ask the engineer to identify are standard, or at least natural, in
most serious RL formulations.

`state_key(observation, info)` is the least automatic one, because Gymnasium
officially gives the agent an observation, not necessarily a full Markov state.
In many environments the observation is already the state, especially in small
discrete control examples. In partially observed problems, pixel-based problems,
history-dependent tasks, or robotics tasks with hidden simulator state, the
engineer may need to say explicitly what should count as the graph node. That is
not a weird `state_collapser` demand; it is the usual distinction between
observation and state, made operational.

`action_key(action, observation, info)` is usually easy. Gymnasium already has an
action space, so in a discrete env the action itself is usually the edge label.
In a continuous or structured action space, the engineer may need to discretize,
bucket, normalize, or name the action for graph purposes. Again, this is not
foreign to RL engineering; it is the ordinary question of how actions are
represented for logging, replay, abstraction, or model learning.

`action_mask(info, env)` is standard in constrained discrete-action RL, but not
universal. Many Gymnasium envs have no action mask because every action is
always nominally available. But in board games, combinatorial control,
counterpoint, scheduling, routing, and many constrained robotics abstractions,
legal-action masks are exactly the right object. If the env has such a concept,
the engineer can usually name it immediately. If it does not, the hook simply
returns `None`.

`edge_labeler(s, a, s_next, info)` is the most `state_collapser`-specific hook,
because ordinary Gymnasium does not ask for quotient/contraction labels. But the
underlying act is still familiar: choose transition features. In normal RL this
shows up as reward features, constraint flags, task predicates, option labels,
success/failure diagnostics, or model-based transition metadata. What is new is
that `state_collapser` uses those transition features to drive graph
coarsening, not merely to log or reward the transition.

So the right answer is: a competent RL engineer may not already have these hooks
written down, but they should usually understand the questions quickly. The only
hook that is truly package-native is the quotient/contraction labeler. The rest
are ways of making explicit concepts that already sit near the surface of a
well-designed Gymnasium problem: what is the state identity, what is the action
identity, which actions are legal, and what transition features matter.

#### PO Decision:
I think the right way to proceed here is to implement exactly the thing you are describing, but then in the TODOs of the `README.md` at root, and maybe in `CONTRIBUTING.md`, we clarify that there's this harder problem that would be interesting to work on, at the interface with gymnasium, concerning observations versus states. Like a more serious interface problem still remains, but is not critical to the package, only critical to breadth of package application. Please let me know if you think this is the rigth direction.

#### LLM Conclusion:
Yes, I think this is exactly the right direction. It separates the implementable
near-term bridge from the harder general interface problem.

The package should implement the explicit-hook version now: a Gymnasium-facing
bridge that can maintain discovered graph/tower structure when the user tells
it how to interpret observations, actions, masks, and transition labels. That
is useful, honest, and within scope. It gives serious users a way to attach
ordinary Gymnasium environments to `state_collapser` without pretending the
package can automatically solve state identification for every possible RL
problem.

Then the README TODO and `CONTRIBUTING.md` should call out the broader
observation-versus-state problem as a future contribution area. That problem is
real and important, but it is not the same as the core package runtime. It is
about widening applicability: how much can `state_collapser` infer or assist
when an environment exposes observations but not clean graph states? For some
envs the answer is easy; for partially observed, continuous, pixel, simulator,
or robotics envs, it becomes a serious representation problem.

So the conclusion I would encode is: build the explicit bridge now, document its
contract clearly, and name the harder automatic/state-reconstruction interface
as future work. That keeps the package shippable without sweeping the hard
problem under the rug.

## Abstractions that should justify themselves or die

| abstraction | users | cost | benefit | recommendation |
|---|---:|---|---|---|
| `RuntimeSnapshot` as live graph carrier | many training/runtime surfaces | hidden mutation, false serialization claim, heavy payloads | convenient access during tests | split into `LiveRuntimeView` and real serializable snapshot |
| eager `QuotientTierView` compatibility readouts | runtime, tests, legacy APIs | global scans on every update | backward compatibility | make lazy/debug-only; default hot path should use partition ids |
| `ContractionPolicy` beside `ContractionSchema` | legacy path, vista annotations | two contraction concepts with similar names | preserves old local-star machinery | keep, but quarantine as legacy/annotation-only and remove from new examples unless needed |
| per-example tabular training loops | five mechanical examples | duplicated target bugs and divergent behavior | very explicit examples | replace with generic reference loop or one shared helper |
| `LoopPolicy` alternatives | tests only, records | promises semantics that do not exist | names future design space | implement or remove non-default choices |
| `GymnasiumAdapter` | tiny toy adapter tests | misleading name and weaker API than real envs | smoke surface | delete or rename |
| `ExploitExploreTowerRuntime` | plate support path | controller/executor/learner machinery before enough examples | captures real research direction | keep experimental, but label harder as experimental and avoid letting it define public API yet |


#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is abstraction budget. Every abstraction in a package
costs the reader something: they have to learn the name, infer the promise, and
decide whether it is stable enough to build on. Some abstractions in the repo
are earning that cost. Others are mostly compatibility shims, future-design
placeholders, or names that sound more mature than their implementation.

This does not mean "delete everything clever." It means the package should be
more ruthless about which concepts become public load-bearing surfaces. The
tower/partition concepts are central and worth developing. But live snapshots
called serializable, nominal loop policies, copied training loops, and a
not-quite-Gymnasium adapter all increase cognitive load without yet buying
enough reliability.

## RL correctness traps

- Termination/truncation: currently the biggest correctness problem. Generic Q-learning treats truncation as terminal; example loops bootstrap through terminal states. This must be fixed before training results are trustworthy.
- Bootstrap masks: no explicit bootstrap-mask surface exists. Add one. Do not make every learner rediscover Gymnasium semantics.
- Action masks: masks exist in counterpoint info, but are not automatically transferred into `ActionSelectionInput`, not enforced before stepping, and not used during bootstrap.
- Seeding: example loops use `random.Random(seed)` and env reset seeds. There is no package-level seed manifest, no action-space seed convention, and no NumPy/PyTorch seed convention yet. This is acceptable for pre-alpha but not for benchmark claims.
- Eval/train mode: tabular learner uses `mode="eval"` to suppress epsilon exploration, which is fine for tabular smoke. There is no PyTorch model mode surface yet.
- Replay correctness: current `TabularQLearner.replay` is an unbounded list and only updates from the last transition. Fine for smoke tests, not fine for serious replay. No wraparound, sampling, or terminal-observation tests exist because no real replay buffer exists.
- Metrics: metrics count episode reward, steps, success, and max tower depth. They do not distinguish env steps, agent steps, control steps, gradient updates, truncations, invalid actions, or wall-clock time.
- Checkpointing: none. This is an explicit maturity gap.


#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that RL systems can fail scientifically while still
passing ordinary software tests. A training run can complete, rewards can move,
and coverage can be high, while the learner is still updating toward the wrong
target because termination, truncation, masks, seeds, replay, or eval mode were
handled ambiguously.

That is why these are "correctness traps" rather than style complaints. They
are exactly the places where an experiment can look plausible but not mean what
we think it means. Before adding heavier model machinery, the repo needs to
make these contracts explicit enough that a training result is interpretable:
what actions were legal, whether bootstrapping was allowed, what randomness was
used, and what exactly was evaluated.

## Performance and feedback loop

The package passes tests fast, which is good. The danger is that tests are small
enough to hide the cost shape.

Likely hot paths:

- `TowerRuntime.step(...)`
- `PartitionTower.update_with_delta(...)`
- `PartitionTower._capture_morphism_domain(...)`
- `to_quotient_tier_views(...)`
- example env `out_edges(...)`
- `tower_depth_probe` continuous probing

Likely wasted work:

- full compatibility readout rebuild after every partition update
- full morphism-domain capture even when no caller needs the morphism
- Python object graphs in snapshots
- repeated construction of label schemas inside `DimensionwiseSchema.assign_edge(...)`
- copy-pasted training loops that force fixes to be repeated

Shortest profiling plan:

```bash
uv run python -m state_collapser.examples.tower_depth_probe --steps 1000 --seed 0 --summary-only
uv run python -m cProfile -o /tmp/tower_probe.prof -m state_collapser.examples.tower_depth_probe --steps 1000 --seed 0 --summary-only
uv run python -m pstats /tmp/tower_probe.prof
```

Minimum benchmark table to add:

| benchmark | metric |
|---|---|
| no-schema flat probe | steps/sec |
| default schema probe | steps/sec |
| partition update without readout | updates/sec |
| partition update with readout | updates/sec |
| full rebuild legacy tower | updates/sec |

The benchmark target should be blunt: prove the Young-tableaux runtime actually
buys local update cost when compatibility readouts are not requested.

#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that fast tests do not prove scalable runtime
behavior. The current tests are small, so a full scan hidden inside each step can
look harmless. But the mathematical point of the Young-tableaux/partition
runtime is that exploration should update the tower locally as the graph grows.

So performance has to be tested against the claimed cost shape, not just against
wall-clock convenience on tiny examples. We need benchmarks that separate the
local update from optional compatibility readouts. If the local update is fast
but the default path always triggers a global readout, then the implementation
has lost the practical benefit of the theory.

## Tests that actually matter

Highest-value missing tests:

- Q-learning terminal bootstrap test: true terminal transition must not bootstrap.
- Q-learning truncation bootstrap test: time-limit truncation must follow explicit configured semantics.
- Example-loop target test: every `run_tower_training(...)` path must share the same target semantics.
- Mask propagation test: `info["action_mask"]` becomes `ActionSelectionInput.action_mask`.
- Mask enforcement test: collector rejects a masked-off selected action.
- Masked bootstrap test: learner does not bootstrap over invalid target actions.
- Snapshot immutability test: snapshot from time `t` does not change after time `t+1`.
- Snapshot serialization test: the serializable snapshot can be JSON/pickle serialized without live runtime objects.
- Loop policy carry-forward test: `aggregate_internal` and `formal_stutter` survive incremental update records if they remain public.
- Gym action boundary tests for all envs: invalid types and out-of-range values are rejected consistently.
- Performance regression tests or benchmarks around partition update/readout cost.
- Minimal run-manifest test once benchmark/training artifacts are introduced.



#### PO Response:
Step up one level, i.e., slightly higher level, and explain this issue to me.

#### LLM Response:
The higher-level issue is that the existing tests mostly prove that the parts
run and that many structural invariants hold. That is good and genuinely worth
keeping. But the next tests need to prove the things that would make training
claims trustworthy.

In practice, that means tests for the semantic edges: terminal targets,
truncation targets, action masks, invalid actions, immutable snapshots, loop
policy behavior, and hot-path performance. These are not random extra tests.
They are the tests that stop the package from producing clean-looking but
misleading RL results.

## What I would delete first

1. Delete or rename `GymnasiumAdapter`. The real Gymnasium envs are better; this adapter overclaims.
2. Delete eager compatibility readout from the default `TowerRuntime` hot path. Keep it as an explicit debug/readout call.
3. Delete copied tabular Q-learning loops in mechanical examples after moving them onto `state_collapser.training`.
4. Delete non-default `LoopPolicy` constructors unless their semantics are implemented now.
5. Delete live graph/tower references from any object called `Serializable`.

## What I would rewrite first

Rewrite the training transition/update contract before adding any neural model
surface. This is the smallest rewrite with the highest leverage.

Required shape:

```python
@dataclass(frozen=True, slots=True)
class TrainingTransition:
    source_input: ActionSelectionInput
    chosen_action: object
    reward: float
    target_input: ActionSelectionInput
    terminated: bool
    truncated: bool
    bootstrap_allowed: bool
```

Then make the collector own the Gymnasium semantics:

```python
bootstrap_allowed = not terminated and (
    not truncated or collector_config.bootstrap_on_truncation
)
```

Then make the learner own only the learning rule:

```python
bootstrap = masked_max_q(target_input) if transition.bootstrap_allowed else 0.0
```

This removes the worst ambiguity from every downstream learner: the learner no
longer has to guess whether `truncated` should mean terminal.

## Final standard

Before this package should be trusted for serious RL results, the code must make
the training target semantics explicit, make masks first-class, stop calling
live mutable graph objects "serializable", and prove with benchmarks that the
partition runtime is actually local in the default hot path. The tower code is
promising and the tests are much better than average, but the current training
surface can still compute the wrong target while looking clean. That is the
line: no more model work should be treated as meaningful until the transition
contract, masks, snapshots, and hot-path readouts are made honest.

## PO-requested language/runtime addendum

The PO explicitly asked for one additional synthetic-Blow-style pass over the
most basic implementation choice: the fact that this project is written in
Python, with a script/runtime package architecture, rather than in a language
that naturally builds compact binaries and gives direct control over memory
layout, allocation, data locality, and performance boundaries. This section is
not claiming to represent Jonathan Blow's actual view or endorsement. It is a
synthesis in the same review spirit used above: direct, performance-aware,
skeptical of accidental complexity, and biased toward simple data and
measurable behavior.

From that lens, the biggest possible criticism is not any one function. It is
that the entire package is trying to do a performance-sensitive graph-runtime
thing in the wrong execution environment. The core story of `state_collapser` is
about maintaining a growing discovered graph, nested partition tables, quotient
views, tower positions, action masks, reward aggregations, and training
transitions. That is a lot of small data moving through tight loops. Python is
not naturally good at that. It encourages object graphs, dictionaries,
dataclasses, dynamic dispatch, boxed values, and pointer chasing. Those are
exactly the shapes that make local algorithms less local on real hardware.

A harsher version of the complaint would be: the project is about making RL
training faster by changing the geometry of the search problem, but the
implementation language makes it easy to spend the speedup on interpreter
overhead, allocations, compatibility views, and abstract objects. The theory
can be right while the runtime still loses because every "cell", "edge",
"state", "snapshot", and "transition" is a Python object with hidden allocation
and cache behavior. If the serious claim is speed, then eventually the code has
to answer the machine, not just the type checker.

This is not a reason to stop using Python right now. For this project, Python
has been the correct research language so far. It made the mathematical model
easy to change, made Gymnasium integration natural, made tests cheap to write,
made examples easy to inspect, and kept the project accessible to RL engineers.
Those are real advantages. The project is still discovering its own correct
abstractions. Rewriting too early into C, C++, Zig, Rust, or Jai-style systems
code would probably freeze the wrong design.

But the language choice should impose discipline. The repo should not confuse
"Python implementation is clean" with "runtime model is efficient." The
professional path is:

1. Keep Python as the research/control surface.
2. Make the hot path explicit and benchmarked.
3. Keep data layouts simple enough that they could later be moved behind a
   compiled extension.
4. Avoid public APIs that require arbitrary Python object graphs in the tower
   core.
5. Treat compatibility readouts, live snapshots, and rich debug objects as
   outer-layer conveniences, not as the runtime representation.

If the package succeeds, the eventual architecture may want a split: Python for
Gymnasium integration, experiment setup, training orchestration, tests, and
model glue; a compiled core for partition-table maintenance, edge ingestion,
loop aggregation, quotient readout construction, and high-volume benchmark
paths. That does not need to happen yet. But the code should be written now so
that this split remains possible.

So the synthetic language-level verdict is: Python is acceptable for the
current research phase, but it is not a neutral choice. It is a tax on exactly
the part of the system that wants to be fast. The way to make that tax
acceptable is not to rewrite immediately; it is to keep the core data model
plain, benchmark the hot path, stop hiding global work behind friendly objects,
and make sure the eventual compiled boundary is not blocked by today's API
decisions.

#### PO Response:
Fantastic. Ok. What about the current Python codebase shape. Does it meet these conditions: "The repo should not confuse 'Python implementation is clean' with 'runtime model is efficient.' The professional path is: • keep Python as the research/control surface • make the hot path explicit and benchmarked • keep data layouts simple enough that they could later be moved behind a compiled extension • avoid public APIs that require arbitrary Python object graphs in the tower core • treat compatibility readouts, live snapshots, and rich debug objects as outer-layer conveniences, not as the runtime representation."

#### LLM Reply:
Short answer: partially, but not yet. The current codebase is a good Python
research/control implementation. It is not yet shaped like a Python front-end
over a future compiled runtime core. The strongest parts are the typed package
surfaces, the test suite, and the move toward partition-table runtime objects.
The weakest parts are still the places identified earlier: eager compatibility
readouts, live mutable snapshots, and object-rich tower/runtime payloads.

Condition by condition:

1. **Keep Python as the research/control surface.** Yes. This is the part the
   repo does well. Python is currently being used for exactly the right things:
   examples, Gymnasium integration, training loops, readable tests, design
   exploration, and fast iteration on the mathematical model.

2. **Make the hot path explicit and benchmarked.** Not yet. The likely hot path
   is visible to a reviewer, but it is not encoded as a first-class benchmark
   surface. The repo still relies mostly on correctness tests and small smoke
   runs. That means the code can pass everything while hiding global scans inside
   `TowerRuntime.step(...)`, partition updates, quotient readouts, snapshot
   construction, or morphism capture.

3. **Keep data layouts simple enough to move behind a compiled extension.**
   Partially. The Young-tableaux/partition refactor moves in the right
   direction because it introduces explicit partition layers, ids, cell records,
   and table-like concepts. But the implementation is still very Python-object
   heavy: dataclasses, dictionaries, arbitrary state/action objects, live graph
   references, rich result objects, and compatibility views. A compiled core
   would want stable integer ids, dense arrays or struct-like records, explicit
   ownership, and minimal callback boundaries.

4. **Avoid public APIs that require arbitrary Python object graphs in the tower
   core.** Not yet. The current public/runtime surfaces still expose and accept
   rich Python objects in important places: `RuntimeSnapshot` carries live graph
   and tower objects, states/actions are package-level Python values rather than
   consistently normalized core ids, and readout objects are still part of the
   ordinary runtime story. This is fine for research ergonomics, but it makes a
   future compiled boundary harder unless we introduce a stricter kernel layer.

5. **Treat compatibility readouts, live snapshots, and debug objects as
   outer-layer conveniences.** Not yet. This is the clearest failure against the
   standard. Compatibility quotient-tier readouts and live snapshots are still
   too close to the default runtime path. They should become opt-in views over
   the authoritative partition state, not the thing the runtime eagerly
   reconstructs and hands around by default.

So the current verdict is: the repo is in the correct Python phase, but it has
not yet earned the stronger runtime-shape claim. It is clean Python research
code with a serious test suite, not yet a clean Python shell around a
machine-friendly core.

The minimum move that would change the answer is not a language rewrite. It is
to introduce a stricter split:

- a small, boring partition-kernel layer using stable ids and simple tables
- a Python adapter layer that maps user states/actions/Gymnasium data into
  those ids
- lazy compatibility readouts outside the hot path
- real serializable value snapshots separate from live runtime views
- benchmarks that prove local update cost independently of debug/readout cost

If those changes are made, the code can stay Python while being written in a
way that does not block a future compiled kernel. Without those changes, Python
will remain convenient, but the package will keep paying Python-object costs in
exactly the runtime region where the theory is trying to win.

#### PO Decision:
Ok. I totally support your assessment. However, let's pause any direct addressing of this issue for now. Many of our implementations proposed above address issues you raise here in this last addendum. At a later Phase.Stage of work, we can tackle this anew.
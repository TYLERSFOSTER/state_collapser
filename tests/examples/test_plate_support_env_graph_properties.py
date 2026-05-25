from __future__ import annotations

from collections import deque

from state_collapser.examples.plate_support_env import (
    CANDIDATE_GOAL_STATE,
    START_STATE,
    all_valid_states,
    primitive_transition,
    valid_outgoing_transitions,
)


def _reachable_states_from_start() -> set[object]:
    seen = {START_STATE}
    queue: deque[object] = deque([START_STATE])
    while queue:
        state = queue.popleft()
        for _, next_state in valid_outgoing_transitions(state):
            if next_state not in seen:
                seen.add(next_state)
                queue.append(next_state)
    return seen


def test_start_state_has_valid_outgoing_transition() -> None:
    assert len(valid_outgoing_transitions(START_STATE)) > 0


def test_goal_state_is_reachable_from_start() -> None:
    reachable = _reachable_states_from_start()
    assert CANDIDATE_GOAL_STATE in reachable


def test_hidden_graph_is_nontrivial() -> None:
    assert len(all_valid_states()) > 20


def test_invalid_moves_exist() -> None:
    result = primitive_transition(START_STATE, 7)
    assert result.invalid_move is True
    assert result.next_state == START_STATE

"""
State Machine Module

Deterministic workflow state management for MDSA orchestration.
"""

import logging
from enum import Enum
from typing import Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """
    Workflow states for MDSA orchestration.

    State Flow:
    INIT -> CLASSIFY -> VALIDATE_PRE -> LOAD_SLM -> EXECUTE ->
    VALIDATE_POST -> LOG -> RETURN

    Error states can be entered from any state.
    """
    INIT = "init"
    CLASSIFY = "classify"
    VALIDATE_PRE = "validate_pre"
    LOAD_SLM = "load_slm"
    EXECUTE = "execute"
    VALIDATE_POST = "validate_post"
    LOG = "log"
    RETURN = "return"
    ERROR = "error"
    ROLLBACK = "rollback"


class StateMachineError(Exception):
    """Exception raised for state machine errors."""
    pass


class StateMachine:
    """
    Deterministic state machine for workflow control.

    Enforces valid state transitions and provides rollback capability.

    Example:
        >>> sm = StateMachine()
        >>> sm.transition(WorkflowState.CLASSIFY)
        >>> current = sm.get_current_state()
        >>> print(current)  # WorkflowState.CLASSIFY
    """

    # Valid state transitions (from_state -> [to_states])
    VALID_TRANSITIONS: Dict[WorkflowState, Set[WorkflowState]] = {
        WorkflowState.INIT: {
            WorkflowState.CLASSIFY,
            WorkflowState.ERROR,
        },
        WorkflowState.CLASSIFY: {
            WorkflowState.VALIDATE_PRE,
            WorkflowState.ERROR,
            WorkflowState.RETURN,  # Low confidence bypass
        },
        WorkflowState.VALIDATE_PRE: {
            WorkflowState.LOAD_SLM,
            WorkflowState.ERROR,
            WorkflowState.ROLLBACK,
        },
        WorkflowState.LOAD_SLM: {
            WorkflowState.EXECUTE,
            WorkflowState.ERROR,
            WorkflowState.ROLLBACK,
        },
        WorkflowState.EXECUTE: {
            WorkflowState.VALIDATE_POST,
            WorkflowState.ERROR,
            WorkflowState.ROLLBACK,
        },
        WorkflowState.VALIDATE_POST: {
            WorkflowState.LOG,
            WorkflowState.ROLLBACK,
            WorkflowState.ERROR,
        },
        WorkflowState.LOG: {
            WorkflowState.RETURN,
            WorkflowState.ERROR,
        },
        WorkflowState.RETURN: set(),  # Terminal state
        WorkflowState.ERROR: {
            WorkflowState.ROLLBACK,
            WorkflowState.RETURN,
        },
        WorkflowState.ROLLBACK: {
            WorkflowState.RETURN,
            WorkflowState.ERROR,
        },
    }

    def __init__(self, initial_state: WorkflowState = WorkflowState.INIT):
        """
        Initialize state machine.

        Args:
            initial_state: Starting state (default: INIT)
        """
        self.current_state = initial_state
        self.state_history: List[WorkflowState] = [initial_state]
        self.callbacks: Dict[WorkflowState, List[Callable]] = {}
        self.metadata: Dict[str, any] = {}

        logger.debug(f"StateMachine initialized at state: {initial_state}")

    def transition(self, to_state: WorkflowState, force: bool = False) -> bool:
        """
        Transition to a new state.

        Args:
            to_state: Target state
            force: Force transition even if invalid (dangerous!)

        Returns:
            bool: True if transition succeeded

        Raises:
            StateMachineError: If transition is invalid and not forced
        """
        if not force and not self._is_valid_transition(to_state):
            raise StateMachineError(
                f"Invalid state transition: {self.current_state} -> {to_state}. "
                f"Valid transitions from {self.current_state}: "
                f"{self.VALID_TRANSITIONS.get(self.current_state, set())}"
            )

        # Log transition
        logger.info(f"State transition: {self.current_state} -> {to_state}")

        # Update state
        previous_state = self.current_state
        self.current_state = to_state
        self.state_history.append(to_state)

        # Execute callbacks
        self._execute_callbacks(to_state, previous_state)

        return True

    def _is_valid_transition(self, to_state: WorkflowState) -> bool:
        """
        Check if transition is valid.

        Args:
            to_state: Target state

        Returns:
            bool: True if valid
        """
        valid_next_states = self.VALID_TRANSITIONS.get(self.current_state, set())
        return to_state in valid_next_states

    def get_current_state(self) -> WorkflowState:
        """
        Get current state.

        Returns:
            WorkflowState: Current state
        """
        return self.current_state

    def get_state_history(self) -> List[WorkflowState]:
        """
        Get state history.

        Returns:
            list: List of states in order
        """
        return self.state_history.copy()

    def reset(self, initial_state: WorkflowState = WorkflowState.INIT):
        """
        Reset state machine to initial state.

        Args:
            initial_state: State to reset to
        """
        logger.info(f"Resetting state machine to {initial_state}")
        self.current_state = initial_state
        self.state_history = [initial_state]
        self.metadata.clear()

    def register_callback(self, state: WorkflowState, callback: Callable):
        """
        Register callback for state entry.

        Args:
            state: State to register callback for
            callback: Function to call (signature: callback(from_state, to_state))

        Example:
            >>> def on_execute(from_state, to_state):
            ...     print("Entered EXECUTE state")
            >>> sm.register_callback(WorkflowState.EXECUTE, on_execute)
        """
        if state not in self.callbacks:
            self.callbacks[state] = []
        self.callbacks[state].append(callback)
        logger.debug(f"Registered callback for state: {state}")

    def _execute_callbacks(self, to_state: WorkflowState, from_state: WorkflowState):
        """
        Execute callbacks for state transition.

        Args:
            to_state: Target state
            from_state: Previous state
        """
        # Execute exit callbacks for previous state
        if hasattr(self, '_exit_callbacks') and from_state in self._exit_callbacks:
            for callback in self._exit_callbacks[from_state]:
                try:
                    callback(from_state, to_state)
                except Exception as e:
                    logger.error(f"Exit callback error for {from_state}: {e}")

        # Execute entry callbacks for new state
        if to_state in self.callbacks:
            for callback in self.callbacks[to_state]:
                try:
                    callback(from_state, to_state)
                except Exception as e:
                    logger.error(f"Callback error for {to_state}: {e}")

    def is_terminal_state(self) -> bool:
        """
        Check if current state is terminal.

        Returns:
            bool: True if in terminal state (RETURN or ERROR)
        """
        return self.current_state in {WorkflowState.RETURN, WorkflowState.ERROR}

    def set_metadata(self, key: str, value: any):
        """
        Store metadata for current workflow.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: any = None) -> any:
        """
        Retrieve metadata.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def get_all_metadata(self) -> Dict[str, any]:
        """
        Get all metadata.

        Returns:
            dict: Copy of all metadata
        """
        return self.metadata.copy()

    def clear_metadata(self):
        """Clear all metadata."""
        self.metadata.clear()

    def on_enter(self, state: WorkflowState, callback: Callable):
        """
        Register callback for state entry (alias for register_callback).

        Args:
            state: State to register callback for
            callback: Function to call on state entry
        """
        self.register_callback(state, callback)

    def on_exit(self, state: WorkflowState, callback: Callable):
        """
        Register callback for state exit.

        Args:
            state: State to register callback for (will fire when LEAVING this state)
            callback: Function to call on state exit

        Note: This is stored separately from entry callbacks.
        """
        if not hasattr(self, '_exit_callbacks'):
            self._exit_callbacks: Dict[WorkflowState, List[Callable]] = {}

        if state not in self._exit_callbacks:
            self._exit_callbacks[state] = []
        self._exit_callbacks[state].append(callback)
        logger.debug(f"Registered exit callback for state: {state}")

    def get_valid_next_states(self) -> Set[WorkflowState]:
        """
        Get valid next states from current state.

        Returns:
            set: Set of valid next states
        """
        return self.VALID_TRANSITIONS.get(self.current_state, set())

    def can_transition_to(self, to_state: WorkflowState) -> bool:
        """
        Check if can transition to target state.

        Args:
            to_state: Target state

        Returns:
            bool: True if transition is valid
        """
        return self._is_valid_transition(to_state)

    def __repr__(self) -> str:
        """String representation."""
        return f"<StateMachine state={self.current_state.value} history_length={len(self.state_history)}>"


if __name__ == "__main__":
    # Demo usage
    print("=== StateMachine Demo ===\n")

    sm = StateMachine()
    print(f"Initial state: {sm.get_current_state()}")
    print(f"Valid next states: {sm.get_valid_next_states()}\n")

    # Valid transitions
    print("--- Valid Workflow ---")
    try:
        sm.transition(WorkflowState.CLASSIFY)
        print(f"Current: {sm.get_current_state()}")

        sm.transition(WorkflowState.VALIDATE_PRE)
        print(f"Current: {sm.get_current_state()}")

        sm.transition(WorkflowState.LOAD_SLM)
        print(f"Current: {sm.get_current_state()}")

        sm.transition(WorkflowState.EXECUTE)
        print(f"Current: {sm.get_current_state()}")

        sm.transition(WorkflowState.VALIDATE_POST)
        print(f"Current: {sm.get_current_state()}")

        sm.transition(WorkflowState.LOG)
        print(f"Current: {sm.get_current_state()}")

        sm.transition(WorkflowState.RETURN)
        print(f"Current: {sm.get_current_state()}")
        print(f"Terminal state: {sm.is_terminal_state()}")

    except StateMachineError as e:
        print(f"Error: {e}")

    print(f"\nState history: {[s.value for s in sm.get_state_history()]}")

    # Invalid transition
    print("\n--- Invalid Transition ---")
    sm.reset()
    try:
        sm.transition(WorkflowState.EXECUTE)  # Can't go directly from INIT to EXECUTE
    except StateMachineError as e:
        print(f"Caught expected error: {e}")

    # Callback demo
    print("\n--- Callback Demo ---")
    sm.reset()

    def on_execute(from_state, to_state):
        print(f"  Callback: Entered EXECUTE from {from_state}")

    sm.register_callback(WorkflowState.EXECUTE, on_execute)
    sm.transition(WorkflowState.CLASSIFY)
    sm.transition(WorkflowState.VALIDATE_PRE)
    sm.transition(WorkflowState.LOAD_SLM)
    sm.transition(WorkflowState.EXECUTE)  # Callback will fire

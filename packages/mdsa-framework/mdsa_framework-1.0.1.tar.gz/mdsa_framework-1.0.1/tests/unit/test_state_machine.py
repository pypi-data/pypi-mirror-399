"""
Unit tests for State Machine module.

Tests workflow state transitions, validation, and callbacks.
"""

import unittest
from mdsa.core.state_machine import StateMachine, WorkflowState, StateMachineError


class TestWorkflowState(unittest.TestCase):
    """Test suite for WorkflowState enum."""

    def test_workflow_states_exist(self):
        """Test all expected workflow states exist."""
        expected_states = [
            'INIT', 'CLASSIFY', 'VALIDATE_PRE', 'LOAD_SLM',
            'EXECUTE', 'VALIDATE_POST', 'LOG', 'RETURN',
            'ERROR', 'ROLLBACK'
        ]

        for state_name in expected_states:
            self.assertTrue(hasattr(WorkflowState, state_name))

    def test_state_values(self):
        """Test state values are lowercase strings."""
        self.assertEqual(WorkflowState.INIT.value, "init")
        self.assertEqual(WorkflowState.CLASSIFY.value, "classify")
        self.assertEqual(WorkflowState.ERROR.value, "error")


class TestStateMachine(unittest.TestCase):
    """Test suite for StateMachine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sm = StateMachine()

    def test_initialization(self):
        """Test StateMachine initialization."""
        self.assertEqual(self.sm.current_state, WorkflowState.INIT)
        self.assertEqual(len(self.sm.get_state_history()), 1)

    def test_valid_transition_init_to_classify(self):
        """Test valid transition from INIT to CLASSIFY."""
        result = self.sm.transition(WorkflowState.CLASSIFY)
        self.assertTrue(result)
        self.assertEqual(self.sm.current_state, WorkflowState.CLASSIFY)

    def test_valid_transition_sequence(self):
        """Test complete valid transition sequence."""
        transitions = [
            WorkflowState.CLASSIFY,
            WorkflowState.VALIDATE_PRE,
            WorkflowState.LOAD_SLM,
            WorkflowState.EXECUTE,
            WorkflowState.VALIDATE_POST,
            WorkflowState.LOG,
            WorkflowState.RETURN
        ]

        for state in transitions:
            self.assertTrue(self.sm.transition(state))
            self.assertEqual(self.sm.current_state, state)

    def test_invalid_transition_raises_error(self):
        """Test invalid transition raises StateMachineError."""
        # Can't go from INIT directly to EXECUTE
        with self.assertRaises(StateMachineError):
            self.sm.transition(WorkflowState.EXECUTE)

    def test_force_transition_bypasses_validation(self):
        """Test force parameter bypasses validation."""
        # Invalid transition, but with force=True
        result = self.sm.transition(WorkflowState.EXECUTE, force=True)
        self.assertTrue(result)
        self.assertEqual(self.sm.current_state, WorkflowState.EXECUTE)

    def test_transition_to_error_from_any_state(self):
        """Test transition to ERROR allowed from any state."""
        self.sm.transition(WorkflowState.CLASSIFY)
        self.sm.transition(WorkflowState.VALIDATE_PRE)

        # Should be able to transition to ERROR from any state
        result = self.sm.transition(WorkflowState.ERROR)
        self.assertTrue(result)
        self.assertEqual(self.sm.current_state, WorkflowState.ERROR)

    def test_terminal_state_detection(self):
        """Test terminal state detection."""
        self.assertFalse(self.sm.is_terminal_state())

        self.sm.transition(WorkflowState.CLASSIFY)
        self.assertFalse(self.sm.is_terminal_state())

        # Transition to RETURN (terminal)
        self.sm.transition(WorkflowState.VALIDATE_PRE)
        self.sm.transition(WorkflowState.LOAD_SLM)
        self.sm.transition(WorkflowState.EXECUTE)
        self.sm.transition(WorkflowState.VALIDATE_POST)
        self.sm.transition(WorkflowState.LOG)
        self.sm.transition(WorkflowState.RETURN)

        self.assertTrue(self.sm.is_terminal_state())

    def test_error_is_terminal_state(self):
        """Test ERROR is a terminal state."""
        self.sm.transition(WorkflowState.ERROR)
        self.assertTrue(self.sm.is_terminal_state())

    def test_state_history_tracking(self):
        """Test state history is tracked correctly."""
        self.sm.transition(WorkflowState.CLASSIFY)
        self.sm.transition(WorkflowState.VALIDATE_PRE)

        history = self.sm.get_state_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], WorkflowState.INIT)
        self.assertEqual(history[1], WorkflowState.CLASSIFY)
        self.assertEqual(history[2], WorkflowState.VALIDATE_PRE)

    def test_reset_state_machine(self):
        """Test resetting state machine to INIT."""
        self.sm.transition(WorkflowState.CLASSIFY)
        self.sm.transition(WorkflowState.VALIDATE_PRE)

        self.sm.reset()

        self.assertEqual(self.sm.current_state, WorkflowState.INIT)
        self.assertEqual(len(self.sm.get_state_history()), 1)

    def test_metadata_storage(self):
        """Test metadata can be stored and retrieved."""
        self.sm.set_metadata('correlation_id', 'req-123')
        self.sm.set_metadata('query', 'Test query')

        self.assertEqual(self.sm.get_metadata('correlation_id'), 'req-123')
        self.assertEqual(self.sm.get_metadata('query'), 'Test query')

    def test_metadata_default_value(self):
        """Test getting non-existent metadata returns default."""
        value = self.sm.get_metadata('nonexistent', default='default_val')
        self.assertEqual(value, 'default_val')

    def test_get_all_metadata(self):
        """Test getting all metadata."""
        self.sm.set_metadata('key1', 'value1')
        self.sm.set_metadata('key2', 'value2')

        metadata = self.sm.get_all_metadata()
        self.assertEqual(metadata['key1'], 'value1')
        self.assertEqual(metadata['key2'], 'value2')

    def test_clear_metadata(self):
        """Test clearing all metadata."""
        self.sm.set_metadata('key1', 'value1')
        self.sm.clear_metadata()

        metadata = self.sm.get_all_metadata()
        self.assertEqual(len(metadata), 0)

    def test_on_enter_callback(self):
        """Test on_enter callback is called."""
        callback_called = []

        def callback(from_state, to_state):
            callback_called.append((from_state, to_state))

        self.sm.on_enter(WorkflowState.CLASSIFY, callback)
        self.sm.transition(WorkflowState.CLASSIFY)

        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], (WorkflowState.INIT, WorkflowState.CLASSIFY))

    def test_on_exit_callback(self):
        """Test on_exit callback is called."""
        callback_called = []

        def callback(from_state, to_state):
            callback_called.append((from_state, to_state))

        self.sm.on_exit(WorkflowState.INIT, callback)
        self.sm.transition(WorkflowState.CLASSIFY)

        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], (WorkflowState.INIT, WorkflowState.CLASSIFY))

    def test_multiple_callbacks(self):
        """Test multiple callbacks can be registered."""
        callbacks_called = {'cb1': False, 'cb2': False}

        def callback1(from_state, to_state):
            callbacks_called['cb1'] = True

        def callback2(from_state, to_state):
            callbacks_called['cb2'] = True

        self.sm.on_enter(WorkflowState.CLASSIFY, callback1)
        self.sm.on_enter(WorkflowState.CLASSIFY, callback2)
        self.sm.transition(WorkflowState.CLASSIFY)

        self.assertTrue(callbacks_called['cb1'])
        self.assertTrue(callbacks_called['cb2'])

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.sm)
        self.assertIn("StateMachine", repr_str)
        self.assertIn("init", repr_str)


class TestStateMachineEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_transition_from_terminal_state(self):
        """Test transition from terminal state raises error."""
        sm = StateMachine()
        sm.transition(WorkflowState.CLASSIFY)
        sm.transition(WorkflowState.VALIDATE_PRE)
        sm.transition(WorkflowState.LOAD_SLM)
        sm.transition(WorkflowState.EXECUTE)
        sm.transition(WorkflowState.VALIDATE_POST)
        sm.transition(WorkflowState.LOG)
        sm.transition(WorkflowState.RETURN)

        # Can't transition from terminal state
        with self.assertRaises(StateMachineError):
            sm.transition(WorkflowState.CLASSIFY)

    def test_transition_from_terminal_state_with_force(self):
        """Test force transition from terminal state works."""
        sm = StateMachine()
        sm.transition(WorkflowState.ERROR)

        # Force should work
        sm.transition(WorkflowState.INIT, force=True)
        self.assertEqual(sm.current_state, WorkflowState.INIT)

    def test_callback_exception_handling(self):
        """Test callback exceptions don't break state machine."""
        sm = StateMachine()

        def bad_callback(from_state, to_state):
            raise ValueError("Callback error")

        sm.on_enter(WorkflowState.CLASSIFY, bad_callback)

        # Should still transition despite callback error
        sm.transition(WorkflowState.CLASSIFY)
        self.assertEqual(sm.current_state, WorkflowState.CLASSIFY)


if __name__ == '__main__':
    unittest.main()

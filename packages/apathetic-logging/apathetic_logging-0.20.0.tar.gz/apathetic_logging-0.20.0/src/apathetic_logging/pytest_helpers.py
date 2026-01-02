"""Pytest helpers for isolated logging in tests.

This module provides pytest fixtures and utilities to help downstream projects
that use apathetic-logging to properly isolate logging in their test suites.

Three main scenarios are addressed:

1. **Scenario A - Debugging with TEST Level**: Set root logger to TEST level
   (most verbose) and prevent apps from downgrading the level, so all logs
   appear when tests break.

2. **Scenario B - Testing Level Changes**: Test that your app correctly changes
   log levels (e.g., CLI --log-level argument). Start with a baseline level,
   run the app, then verify it changed as expected.

3. **Scenario C - Complete Isolation**: Prevent log level settings from bleeding
   between tests. All logger state is saved before each test and restored after.

Example usage:

    # Scenario A: Debugging
    def test_with_verbose_logs(logging_test_level):
        my_app.initialize()  # Won't downgrade from TEST
        my_app.run()  # All logs visible

    # Scenario B: Testing level changes
    @pytest.mark.initial_level("ERROR")
    def test_cli_sets_debug(logging_level_testing):
        cli.main(["--log-level", "debug"])
        logging_level_testing.assert_level_changed_from("ERROR", to="DEBUG")

    # Scenario C: Complete isolation
    def test_isolation(isolated_logging):
        isolated_logging.set_root_level("DEBUG")
        # Next test gets fresh state
"""

from __future__ import annotations

import logging
import sys
import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeAlias, cast

import pytest

import apathetic_logging


if TYPE_CHECKING:
    from .logger_namespace import ApatheticLogging_Internal_Logger
    from .namespace import apathetic_logging as apathetic_logging_class

    Logger: TypeAlias = ApatheticLogging_Internal_Logger.Logger
else:
    Logger = apathetic_logging.Logger


# ============================================================================
# State Management Classes
# ============================================================================


@dataclass(frozen=True)
class RootLoggerState:
    """Snapshot of root logger state."""

    level: int
    """The explicit log level set on the root logger."""

    handlers: list[logging.Handler]
    """List of handlers attached to the root logger."""

    propagate: bool
    """Whether the root logger propagates to parent (always False for root)."""

    disabled: bool
    """Disabled state of the root logger."""

    filters: list[logging.Filter]
    """List of filters attached to the root logger."""


@dataclass(frozen=True)
class LoggingState:
    """Complete snapshot of logging state for save/restore."""

    logger_class: type[logging.Logger]
    """The registered logger class."""

    registry_data: dict[str, Any]
    """Registry data (8 configurable fields)."""

    root_logger_user_configured: bool | None
    """Value of _root_logger_user_configured flag."""

    logger_dict: dict[str, logging.Logger | logging.PlaceHolder]
    """Copy of logging.Logger.manager.loggerDict."""

    root_logger_state: RootLoggerState
    """Snapshot of root logger's state."""


# ============================================================================
# Helper Classes for Fixtures
# ============================================================================


class LoggingIsolation:
    """Helper object for the isolated_logging fixture.

    Provides utilities for managing logger state during a test.
    """

    def __init__(self, saved_state: LoggingState) -> None:
        """Initialize with saved state.

        Args:
            saved_state: The logging state that was saved before the test.
        """
        self._saved_state = saved_state

    def getRootLogger(self) -> Logger:
        """Get the root logger.

        Returns:
            The root logger instance.
        """
        return logging.getLogger("")  # type: ignore[return-value]

    def getLogger(self, name: str | None = None) -> Logger:
        """Get a logger by name, creating it if needed.

        Args:
            name: Logger name. If None, returns root logger.

        Returns:
            The requested logger instance.
        """
        return logging.getLogger(name)  # type: ignore[return-value]

    def setRootLevel(self, level: str | int) -> None:
        """Set the root logger's level.

        Args:
            level: The log level (string or int).
        """
        root = self.getRootLogger()
        if isinstance(level, str):
            try:
                # Try apathetic_logging first for custom levels
                level_int = apathetic_logging.getLevelNumber(level)
            except ValueError:
                # If not a custom level, raise an error
                msg = f"Invalid log level: {level}"
                raise ValueError(msg) from None
        else:
            level_int = level

        root.setLevel(level_int)

    def getAllLoggers(self) -> dict[str, logging.Logger]:
        """Get all loggers in the logging registry.

        Returns:
            Dictionary of logger name to logger instance.
        """
        return {
            name: logger
            for name, logger in logging.Logger.manager.loggerDict.items()
            if isinstance(logger, logging.Logger)
        }

    def assertRootLevel(self, expected: str | int) -> None:
        """Assert that the root logger has the expected level.

        Args:
            expected: The expected log level (string or int).

        Raises:
            AssertionError: If the levels don't match.
        """
        root = self.getRootLogger()
        expected_int = (
            apathetic_logging.getLevelNumber(expected)
            if isinstance(expected, str)
            else expected
        )
        actual = root.level

        if actual != expected_int:
            expected_name = logging.getLevelName(expected_int)
            actual_name = logging.getLevelName(actual)
            msg = (
                f"Expected root logger level {expected_name} ({expected_int}), "
                f"but got {actual_name} ({actual})"
            )
            raise AssertionError(msg)

    def assertLoggerLevel(self, name: str, expected: str | int) -> None:
        """Assert that a logger has the expected level.

        Args:
            name: The logger name.
            expected: The expected log level (string or int).

        Raises:
            AssertionError: If the levels don't match or logger not found.
        """
        logger = self.getLogger(name)
        expected_int = (
            apathetic_logging.getLevelNumber(expected)
            if isinstance(expected, str)
            else expected
        )
        actual = logger.level

        if actual != expected_int:
            expected_name = logging.getLevelName(expected_int)
            actual_name = logging.getLevelName(actual)
            msg = (
                f"Expected logger '{name}' level {expected_name} ({expected_int}), "
                f"but got {actual_name} ({actual})"
            )
            raise AssertionError(msg)


class LoggingTestLevel:
    """Helper object for the logging_test_level fixture.

    Prevents the root logger level from being downgraded below TEST level.
    """

    def __init__(
        self,
        isolation: LoggingIsolation,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Initialize and install prevention mechanism.

        Args:
            isolation: The LoggingIsolation helper.
            monkeypatch: pytest's monkeypatch fixture.
        """
        self._isolation = isolation
        self._monkeypatch = monkeypatch
        self._prevention_enabled = True
        self._original_set_root_level = apathetic_logging.setRootLevel

        # Set root to TEST level
        isolation.setRootLevel("TEST")

        # Install monkey-patch to prevent downgrades
        self._installPrevention()

    def _installPrevention(self) -> None:
        """Install monkey-patch to prevent level downgrades."""

        def protectedSetRootLevel(level: str | int, **kwargs: Any) -> None:
            """Wrapper that prevents downgrades from TEST."""
            if not self._prevention_enabled:
                self._original_set_root_level(level, **kwargs)
                return

            # Get numeric level
            if isinstance(level, str):
                level_int = apathetic_logging.getLevelNumber(level)
            else:
                level_int = level

            # Only prevent downgrades (higher numbers = less verbose)
            # TEST level is 2 (DEBUG - 8)
            test_level = apathetic_logging.TEST_LEVEL
            if level_int > test_level:
                # Attempting to downgrade, silently ignore
                return

            # More verbose or equal, allow
            self._original_set_root_level(level, **kwargs)

        self._monkeypatch.setattr(
            apathetic_logging,
            "setRootLevel",
            protectedSetRootLevel,
        )

    def allowAppLevelChange(self) -> None:
        """Temporarily allow the app to change the log level.

        This disables the downgrade prevention, allowing setRootLevel to work
        normally for the rest of the test or until preventAppLevelChange()
        is called.
        """
        self._prevention_enabled = False

    def preventAppLevelChange(self) -> None:
        """Re-enable the downgrade prevention.

        This re-enables the monkey-patch that prevents downgrades.
        """
        self._prevention_enabled = True

    def getCurrentLevel(self) -> int:
        """Get the current root logger level.

        Returns:
            The numeric log level of the root logger.
        """
        return self._isolation.getRootLogger().level

    @contextmanager
    def temporarilyAllowChanges(self) -> Generator[None, None, None]:
        """Context manager to temporarily allow level changes.

        Example:
            with logging_test_level.temporarilyAllowChanges():
                app.configure_logging(level="INFO")
        """
        self.allowAppLevelChange()
        try:
            yield
        finally:
            self.preventAppLevelChange()


class LoggingLevelTesting:
    """Helper object for the logging_level_testing fixture.

    Tracks log level changes for testing that your app sets levels correctly.
    """

    def __init__(
        self,
        isolation: LoggingIsolation,
        initial_level: str | int,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Initialize level testing helper.

        Args:
            isolation: The LoggingIsolation helper.
            initial_level: The initial root logger level.
            monkeypatch: pytest's monkeypatch fixture.
        """
        self._isolation = isolation
        self._initial_level_str = (
            initial_level if isinstance(initial_level, str) else str(initial_level)
        )
        self._initial_level_int = (
            apathetic_logging.getLevelNumber(initial_level)
            if isinstance(initial_level, str)
            else initial_level
        )
        self._monkeypatch = monkeypatch
        self._history: list[tuple[float, int, str]] = []

        # Set initial level
        isolation.setRootLevel(initial_level)
        self._recordLevel(self._initial_level_int)

        # Install monkey-patch to track changes
        self._original_set_root_level = apathetic_logging.setRootLevel
        self._installTracking()

    def _installTracking(self) -> None:
        """Install monkey-patch to track level changes."""

        def trackedSetRootLevel(level: str | int, **kwargs: Any) -> None:
            """Wrapper that tracks level changes."""
            self._original_set_root_level(level, **kwargs)

            # Record the new level
            if isinstance(level, str):
                level_int = apathetic_logging.getLevelNumber(level)
            else:
                level_int = level

            self._recordLevel(level_int)

        self._monkeypatch.setattr(
            apathetic_logging,
            "setRootLevel",
            trackedSetRootLevel,
        )

    def _recordLevel(self, level_int: int) -> None:
        """Record a level change to the history.

        Args:
            level_int: The numeric level value.
        """
        level_name = logging.getLevelName(level_int)
        timestamp = time.time()
        self._history.append((timestamp, level_int, level_name))

    def assertRootLevel(self, expected: str | int) -> None:
        """Assert that the root logger currently has the expected level.

        Args:
            expected: The expected log level (string or int).

        Raises:
            AssertionError: If the levels don't match.
        """
        self._isolation.assertRootLevel(expected)

    def assertLevelChangedFrom(
        self,
        old_level: str | int,
        *,
        to: str | int,
    ) -> None:
        """Assert that the level changed from one value to another.

        Args:
            old_level: The previous level.
            to: The new level.

        Raises:
            AssertionError: If the transition wasn't found in history.
        """
        old_int = (
            apathetic_logging.getLevelNumber(old_level)
            if isinstance(old_level, str)
            else old_level
        )
        to_int = apathetic_logging.getLevelNumber(to) if isinstance(to, str) else to

        # Look for the transition in history
        for i in range(len(self._history) - 1):
            if self._history[i][1] == old_int and self._history[i + 1][1] == to_int:
                return  # Found it

        # Not found, raise error
        old_name = logging.getLevelName(old_int)
        to_name = logging.getLevelName(to_int)
        history_names = [h[2] for h in self._history]
        msg = (
            f"Expected level change from {old_name} to {to_name}, "
            f"but history is: {history_names}"
        )
        raise AssertionError(msg)

    def assertLevelNotChanged(self) -> None:
        """Assert that the level was never changed from the initial value.

        Raises:
            AssertionError: If the level was changed.
        """
        if len(self._history) > 1:
            history_names = [h[2] for h in self._history]
            msg = f"Expected level to not change, but history is: {history_names}"
            raise AssertionError(msg)

    def getLevelHistory(self) -> list[tuple[float, int, str]]:
        """Get the complete history of level changes.

        Returns:
            List of (timestamp, level_int, level_name) tuples.
        """
        return self._history.copy()

    def resetToInitial(self) -> None:
        """Reset the root logger back to its initial level."""
        self._isolation.setRootLevel(self._initial_level_int)


# ============================================================================
# State Management Functions
# ============================================================================


def saveLoggingState() -> LoggingState:
    """Save the complete logging state.

    This saves everything needed to restore logging to its current state,
    including logger class, registry data, user configuration flags, all
    loggers in the registry, and the root logger's state.

    Returns:
        LoggingState: A snapshot of the current logging state.
    """
    # Save logger class
    logger_class = logging.getLoggerClass()

    # Save registry data (8 fields)
    # In package mode: module exports the class via __init__.py
    # In stitched mode: the class is available directly
    registry = cast(
        "type[apathetic_logging_class]",
        (
            apathetic_logging.apathetic_logging
            if hasattr(apathetic_logging, "apathetic_logging")
            else apathetic_logging
        ),
    )
    registry_data = {
        "registered_internal_logger_name": (registry.registered_internal_logger_name),
        "registered_internal_default_log_level": (
            registry.registered_internal_default_log_level
        ),
        "registered_internal_log_level_env_vars": (
            registry.registered_internal_log_level_env_vars
        ),
        "registered_internal_compatibility_mode": (
            registry.registered_internal_compatibility_mode
        ),
        "registered_internal_propagate": registry.registered_internal_propagate,
        "registered_internal_replace_root_logger": (
            registry.registered_internal_replace_root_logger
        ),
        "registered_internal_port_handlers": (
            registry.registered_internal_port_handlers
        ),
        "registered_internal_port_level": (registry.registered_internal_port_level),
    }

    # Save _root_logger_user_configured flag
    logger_module = sys.modules.get("apathetic_logging.logger")
    root_logger_user_configured = (
        getattr(logger_module, "_root_logger_user_configured", None)
        if logger_module
        else None
    )

    # Save logger dict (copy the dict, not the loggers themselves)
    logger_dict = logging.Logger.manager.loggerDict.copy()

    # Save root logger state
    root = logging.getLogger("")
    root_logger_state = RootLoggerState(
        level=root.level,
        handlers=root.handlers.copy(),
        propagate=root.propagate,
        disabled=root.disabled,
        filters=[f for f in root.filters if isinstance(f, logging.Filter)],
    )

    return LoggingState(
        logger_class=logger_class,
        registry_data=registry_data,
        root_logger_user_configured=root_logger_user_configured,
        logger_dict=logger_dict,
        root_logger_state=root_logger_state,
    )


def restoreLoggingState(state: LoggingState) -> None:
    """Restore logging to a previously saved state.

    Args:
        state: The LoggingState to restore from.
    """
    # Restore logger class
    logging.setLoggerClass(state.logger_class)

    # Restore registry data
    # In package mode: module exports the class via __init__.py
    # In stitched mode: the class is available directly
    registry = cast(
        "type[apathetic_logging_class]",
        (
            apathetic_logging.apathetic_logging
            if hasattr(apathetic_logging, "apathetic_logging")
            else apathetic_logging
        ),
    )
    registry.registered_internal_logger_name = state.registry_data[
        "registered_internal_logger_name"
    ]
    registry.registered_internal_default_log_level = state.registry_data[
        "registered_internal_default_log_level"
    ]
    registry.registered_internal_log_level_env_vars = state.registry_data[
        "registered_internal_log_level_env_vars"
    ]
    registry.registered_internal_compatibility_mode = state.registry_data[
        "registered_internal_compatibility_mode"
    ]
    registry.registered_internal_propagate = state.registry_data[
        "registered_internal_propagate"
    ]
    registry.registered_internal_replace_root_logger = state.registry_data[
        "registered_internal_replace_root_logger"
    ]
    registry.registered_internal_port_handlers = state.registry_data[
        "registered_internal_port_handlers"
    ]
    registry.registered_internal_port_level = state.registry_data[
        "registered_internal_port_level"
    ]

    # Restore _root_logger_user_configured flag
    logger_module = sys.modules.get("apathetic_logging.logger")
    if logger_module:
        if state.root_logger_user_configured is None:
            if hasattr(logger_module, "_root_logger_user_configured"):
                delattr(logger_module, "_root_logger_user_configured")
        else:
            logger_module._root_logger_user_configured = (  # type: ignore[attr-defined]  # noqa: SLF001
                state.root_logger_user_configured
            )

    # Restore logger dict (remove all current, restore from saved)
    current_names = list(logging.Logger.manager.loggerDict.keys())
    for name in current_names:
        logging.Logger.manager.loggerDict.pop(name, None)

    for name, logger in state.logger_dict.items():
        logging.Logger.manager.loggerDict[name] = logger

    # Restore root logger state
    root = logging.getLogger("")
    root.setLevel(state.root_logger_state.level)
    root.propagate = state.root_logger_state.propagate
    root.disabled = state.root_logger_state.disabled

    # Clear current handlers
    root.handlers.clear()

    # Restore handlers
    for handler in state.root_logger_state.handlers:
        root.addHandler(handler)

    # Restore filters
    if hasattr(root, "filters"):
        root.filters.clear()
        for filt in state.root_logger_state.filters:
            root.addFilter(filt)


def clearAllLoggers() -> None:
    """Remove all loggers from the logging registry except the root logger.

    This is useful for test cleanup to ensure a clean state for the next test.
    """
    logger_names = list(logging.Logger.manager.loggerDict.keys())
    for name in logger_names:
        if name not in {"root", ""}:
            logging.Logger.manager.loggerDict.pop(name, None)


# ============================================================================
# Pytest Fixtures
# ============================================================================


@pytest.fixture
def isolatedLogging() -> Generator[LoggingIsolation, None, None]:
    """Fixture providing complete test isolation for logging.

    This fixture saves the complete logging state before the test, clears
    all loggers and resets to defaults, and then restores the saved state
    after the test. This ensures that:

    - Logger class is reset
    - Registry data is reset
    - All loggers are removed
    - Root logger state is reset
    - No state bleeding between tests

    Yields:
        LoggingIsolation: Helper object with methods to manage logger state.

    Example:
        def test_logger_isolation(isolatedLogging):
            isolatedLogging.setRootLevel("DEBUG")
            assert isolatedLogging.getRootLogger().level == logging.DEBUG

        def test_no_state_bleeding(isolatedLogging):
            # Previous test's state is not present here
            root = isolatedLogging.getRootLogger()
            assert root.level != logging.DEBUG
    """
    # Save state
    saved_state = saveLoggingState()

    # Clear all loggers
    clearAllLoggers()

    # Reset to defaults (via apathetic_logging's defaults)
    try:
        apathetic_logging.Logger.extendLoggingModule()
    except (AttributeError, TypeError):
        # In case apathetic_logging is not fully initialized
        logging.setLoggerClass(logging.Logger)

    # Explicitly reset root logger to default level (WARNING)
    root = logging.getLogger("")
    root.setLevel(logging.WARNING)

    # Create and yield helper
    isolation = LoggingIsolation(saved_state)
    yield isolation

    # Cleanup: Remove all loggers again
    clearAllLoggers()

    # Restore state
    restoreLoggingState(saved_state)


@pytest.fixture
def loggingTestLevel(
    isolatedLogging: LoggingIsolation,  # noqa: N803
    monkeypatch: pytest.MonkeyPatch,
) -> LoggingTestLevel:
    """Fixture that sets root logger to TEST level and prevents downgrades.

    Use this fixture when you want your tests to default to maximum verbosity
    (TEST level) so you can see all debug logs if tests fail. The fixture
    prevents the app from downgrading the log level below TEST, ensuring
    debugging logs are always available.

    Yields:
        LoggingTestLevel: Helper with methods to control the prevention.

    Example:
        def test_with_verbose_logs(loggingTestLevel):
            # Root logger is at TEST level
            app.initialize()  # App calls setRootLevel("INFO"), but it's ignored
            app.run()  # All logs visible because level stays at TEST

        def test_allow_app_to_change(loggingTestLevel):
            # Sometimes you need to let the app change levels
            with loggingTestLevel.temporarilyAllowChanges():
                app.configure_logging(level="WARNING")
            # Level is now WARNING, but prevention re-enabled

    Note:
        The "TEST" level is 2 (DEBUG - 8), which is the most verbose level
        and bypasses pytest's capsys to write directly to sys.__stderr__.
        This allows you to see all output even if other tests capture output.
    """
    return LoggingTestLevel(isolatedLogging, monkeypatch)


@pytest.fixture
def loggingLevelTesting(
    isolatedLogging: LoggingIsolation,  # noqa: N803
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> LoggingLevelTesting:
    """Fixture for testing that your app correctly changes log levels.

    Use this when you want to test that your app's log level configuration
    works correctly (e.g., testing a CLI app's --log-level argument).

    The fixture sets a baseline log level, tracks all changes to the root
    logger level, and provides assertions to verify the changes.

    You can set the initial level via a pytest mark:

        @pytest.mark.initial_level("ERROR")
        def test_cli_sets_debug(loggingLevelTesting):
            cli.main(["--log-level", "debug"])
            loggingLevelTesting.assertLevelChangedFrom("ERROR", to="DEBUG")

    If no mark is provided, the default initial level is "ERROR" (quiet).

    Yields:
        LoggingLevelTesting: Helper with assertion methods.

    Example:
        @pytest.mark.initial_level("WARNING")
        def test_quiet_flag(logging_level_testing):
            # Starts at WARNING
            logging_level_testing.assert_root_level("WARNING")

            cli.main(["--quiet"])

            # Verify changed to ERROR or higher
            logging_level_testing.assert_root_level("ERROR")

        @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR"])
        def test_all_levels(logging_level_testing, level):
            cli.main(["--log-level", level.lower()])
            logging_level_testing.assert_root_level(level)
    """
    # Extract initial level from pytest mark if provided
    marker = request.node.get_closest_marker("initial_level")  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
    initial_level = marker.args[0] if marker else "ERROR"  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType,reportOptionalSubscript]  # Default to quiet

    return LoggingLevelTesting(isolatedLogging, initial_level, monkeypatch)  # pyright: ignore[reportUnknownArgumentType]


@pytest.fixture
def apatheticLogger(isolatedLogging: LoggingIsolation) -> Logger:  # noqa: N803
    """Fixture providing a test logger with a unique name.

    This fixture creates a new logger with a unique name and sets it to
    TEST level (most verbose). It's useful for testing logger methods
    in isolation.

    Yields:
        Logger: A freshly created logger with a unique name.

    Example:
        def test_logger_methods(apatheticLogger):
            apatheticLogger.debug("This is visible")
            apatheticLogger.trace("So is this")
            assert apatheticLogger.levelName == "TEST"
    """
    logger = isolatedLogging.getLogger(f"test_logger_{uuid.uuid4().hex[:6]}")
    logger.setLevel(apathetic_logging.TEST_LEVEL)
    return logger


# ============================================================================
# Utility Functions
# ============================================================================


def assertLevelEquals(
    logger: logging.Logger,
    expected: str | int,
    *,
    effective: bool = True,
) -> None:
    """Assert that a logger has the expected level.

    Args:
        logger: The logger to check.
        expected: The expected level (string or int).
        effective: If True, check effective (inherited) level;
            if False, check explicit level.

    Raises:
        AssertionError: If the levels don't match.
    """
    expected_int = (
        apathetic_logging.getLevelNumber(expected)
        if isinstance(expected, str)
        else expected
    )

    actual = logger.getEffectiveLevel() if effective else logger.level

    if actual != expected_int:
        expected_name = logging.getLevelName(expected_int)
        actual_name = logging.getLevelName(actual)
        msg = (
            f"Expected logger level {expected_name} ({expected_int}), "
            f"but got {actual_name} ({actual})"
        )
        raise AssertionError(msg)


def assertRootLevelEquals(expected: str | int) -> None:
    """Assert that the root logger has the expected level.

    Args:
        expected: The expected level (string or int).

    Raises:
        AssertionError: If the levels don't match.
    """
    root = logging.getLogger("")
    assertLevelEquals(root, expected, effective=False)


def assertHandlerCount(
    logger: logging.Logger,
    expected: int,
    *,
    handler_type: type[logging.Handler] | None = None,
) -> None:
    """Assert that a logger has the expected number of handlers.

    Args:
        logger: The logger to check.
        expected: The expected number of handlers.
        handler_type: If provided, only count handlers of this type.

    Raises:
        AssertionError: If the count doesn't match.
    """
    handlers = logger.handlers
    if handler_type:
        handlers = [h for h in handlers if isinstance(h, handler_type)]

    actual = len(handlers)
    if actual != expected:
        type_str = f" of type {handler_type.__name__}" if handler_type else ""
        msg = (
            f"Expected logger to have {expected} handler(s){type_str}, but got {actual}"
        )
        raise AssertionError(msg)


__all__ = [
    "LoggingIsolation",
    "LoggingLevelTesting",
    "LoggingState",
    "LoggingTestLevel",
    "RootLoggerState",
    "apatheticLogger",
    "assertHandlerCount",
    "assertLevelEquals",
    "assertRootLevelEquals",
    "clearAllLoggers",
    "isolatedLogging",
    "loggingLevelTesting",
    "loggingTestLevel",
    "restoreLoggingState",
    "saveLoggingState",
]

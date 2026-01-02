from functools import wraps
import logging
from typing import Callable, ParamSpec, TypeVar
import inspect
import typer

P = ParamSpec("P")
R = TypeVar("R")


class Verbose:
    """
    A utility class to add a `--verbose/-v` flag to Typer CLI commands and manage verbose logging.

    Args:
        loggers (str | list[str] | None, optional): Logger name(s) to set to DEBUG when verbose is enabled.
        callback (Callable | None, optional): A callback function to be called during initialization.

    ```python
    # Example usage
    app = Typer()
    verbose = Verbose("my_logger")
    logger = logging.getLogger("my_logger")
    
    @app.command()
    @verbose()
    def main():
        if verbose:
            print("Verbose mode is on")
        else:
            print("Verbose mode is off")
        logger.debug("This will show in verbose mode")
    """
    verbose: bool = False
    """Verbose state"""
    loggers: list[str] | None = None
    """Collection of standard Python loggers to set as DEBUG"""

    def __init__(self, loggers: str | list[str] | None = None, callback: Callable | None = None) -> None:
        """
        :param loggers: Logger name(s) to set to DEBUG when verbose is enabled.
        :type loggers: str | list[str] | None
        :param callback: A callback function to be called during initialization.
        :type callback: Callable | None
        """
        self.verbose = False
        if isinstance(loggers, str):
            self.loggers = [loggers]
        else:
            self.loggers = loggers
        if callback:
            callback()

    def flag(self) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Decorator that adds a `--verbose/-v` flag to a Typer command.

        If the decorated function already has a `verbose` parameter, it will be replaced.
        """

        def _add_flag(func: Callable[P, R]) -> Callable[P, R]:  # type: ignore[type-arg]
            # Get the original signature
            sig = inspect.signature(func)
            has_verbose = "verbose" in sig.parameters

            # Build new parameter list with verbose having proper Typer annotations
            verbose_param = inspect.Parameter(
                "verbose",
                inspect.Parameter.KEYWORD_ONLY,
                default=typer.Option(
                    False, "--verbose", "-v", help="Enable verbose output"
                ),
                annotation=bool,
            )

            if has_verbose:
                # Replace existing verbose param with annotated version
                new_params = [
                    p if p.name != "verbose" else verbose_param
                    for p in sig.parameters.values()
                ]
            else:
                # Add verbose param
                new_params = list(sig.parameters.values()) + [verbose_param]

            new_sig = sig.replace(parameters=new_params)

            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                self.verbose = kwargs.pop("verbose", False)

                if self.verbose:
                    for logger in self.loggers or []:
                        logging.getLogger(logger).setLevel(logging.DEBUG)

                if has_verbose:
                    return func(*args, verbose=self.verbose, **kwargs)
                return func(*args, **kwargs)

            wrapper.__signature__ = new_sig  # type: ignore
            return wrapper

        return _add_flag

    def __call__(self, *args, **kwds) -> Callable[[Callable[P, R]], Callable[P, R]]:
        return self.flag()
    
    def __bool__(self) -> bool:
        return self.verbose

# src/paramiko_batch/models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, List
import time

@dataclass(frozen=True)
class Command:
    '''
    Represents a command to be executed in a batch process.

    This class encapsulates all the information needed to execute a command
    through paramiko, including the command string, execution context,
    and execution options.

    Attributes:
        cmd (str): The command string to be executed.
        timeout (Optional[float]): The timeout in seconds for command execution.
            If None, no timeout is applied.
        env (Optional[Dict[str, str]]): Environment variables to set for the command.
            If None, the current environment is used.
        cwd (Optional[str]): The working directory for command execution.
            If None, the default working directory is used.
        sudo (bool): Whether to execute the command with sudo privileges.
            Defaults to False.
        name (Optional[str]): A human-readable name for the command.
            Used for better batch output and logging.
    '''
    cmd: str
    timeout: Optional[float] = None
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None
    sudo: bool = False
    name: Optional[str] = None  # for nicer batch output

@dataclass
class CommandResult:
    '''
    Represents the result of executing a command.

    This class holds all the information about a command execution,
    including the command itself, exit status, output streams,
    and timing information.

    Attributes:
        command (Command): The original command that was executed.
        exit_status (Optional[int]): The exit status code of the command.
            None if the command failed to start or was interrupted.
        stdout (str): The standard output of the command.
        stderr (str): The standard error output of the command.
        started_at (float): The timestamp when the command execution started.
        finished_at (float): The timestamp when the command execution finished.
    '''
    command: Command
    exit_status: Optional[int]
    stdout: str
    stderr: str
    started_at: float
    finished_at: float

    @property
    def ok(self) -> bool:
        return self.exit_status == 0

    @property
    def duration_s(self) -> float:
        return self.finished_at - self.started_at

@dataclass(frozen=True)
class BatchPolicy:
    '''
    Represents the policy for executing a batch of commands.

    This class defines how a batch of commands should be executed,
    particularly whether to continue execution if a command fails.

    Attributes:
        stop_on_failure (bool): If True, the batch execution will stop
            as soon as any command fails (i.e., returns a non-zero exit status).
            If False, the batch will continue executing all commands
            regardless of individual command failures.
            Defaults to True.
    '''
    stop_on_failure: bool = True

@dataclass
class BatchResult:
    '''
    Represents the result of executing a batch of commands.

    This class aggregates the results of individual command executions
    and provides utility properties for evaluating the overall success
    or failure of the batch.

    Attributes:
        results (List[CommandResult]): A list of CommandResult objects
            representing the outcomes of each command in the batch.
    '''
    results: List[CommandResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(r.ok for r in self.results)

    @property
    def failed(self) -> List[CommandResult]:
        return [r for r in self.results if not r.ok]

from datetime import datetime
import shlex
import fnmatch
from typing import Any, Dict, List, Literal, Optional, Union, overload

from inspect_ai.util import SandboxEnvironment, SandboxConnection, ExecResult, sandboxenv
from inspect_ai.event import SandboxEvent
from inspect_ai.log import transcript

from .policy import SandboxPolicy, SandboxPolicyViolationError

@sandboxenv(name="policy-sandbox")
class PolicySandboxEnvironment(SandboxEnvironment):
    """Sandbox environment that enforces a policy on a wrapped sandbox."""

    def __init__(self, inner: SandboxEnvironment, policy: SandboxPolicy):
        super().__init__()
        self._inner = inner
        self._policy = policy

    async def exec(
        self,
        cmd: list[str],
        input: str | bytes | None = None,
        cwd: str | None = None,
        env: dict[str, str] = {},
        user: str | None = None,
        timeout: int | None = None,
    ) -> ExecResult:
        # Check Policy
        command_str = cmd[0] if cmd else ""
        
        allowed = True
        
        if self._policy.deny_exec:
             for pattern in self._policy.deny_exec:
                 if fnmatch.fnmatch(command_str, pattern):
                     allowed = False
                     break
        
        if allowed and self._policy.allow_exec:
            allowed = False
            for pattern in self._policy.allow_exec:
                 if fnmatch.fnmatch(command_str, pattern):
                     allowed = True
                     break
        
        if not allowed:
            metadata = {
                "command": command_str,
                "policy": "exec",
                "reason": "policy"
            }
            transcript()._event(SandboxEvent(
                action="exec",
                cmd=command_str,
                result=1,
                metadata=metadata,
                timestamp=datetime.now()
            ))
            raise SandboxPolicyViolationError(f"Execution of '{command_str}' is denied by policy.")

        return await self._inner.exec(cmd, input, cwd, env, user, timeout)

    async def read_file(self, file: str, text: bool = True) -> Union[str, bytes]:
        # Check Policy
        allowed = True
        if self._policy.deny_read:
             for pattern in self._policy.deny_read:
                 if fnmatch.fnmatch(file, pattern):
                     allowed = False
                     break
        
        if allowed and self._policy.allow_read:
            allowed = False
            for pattern in self._policy.allow_read:
                 if fnmatch.fnmatch(file, pattern):
                     allowed = True
                     break

        if not allowed:
            metadata = {
                "file": file,
                "policy": "read_file",
                "reason": "policy"
            }
            transcript()._event(SandboxEvent(
                action="read_file",
                file=file,
                result=1,
                metadata=metadata,
                timestamp=datetime.now()
            ))
            raise SandboxPolicyViolationError(f"Reading file '{file}' is denied by policy.")
            
        return await self._inner.read_file(file, text)

    async def write_file(self, file: str, content: Union[str, bytes]) -> None:
        # Check Policy
        allowed = True
        if self._policy.deny_write:
             for pattern in self._policy.deny_write:
                 if fnmatch.fnmatch(file, pattern):
                     allowed = False
                     break
        
        if allowed and self._policy.allow_write:
            allowed = False
            for pattern in self._policy.allow_write:
                 if fnmatch.fnmatch(file, pattern):
                     allowed = True
                     break

        if not allowed:
            metadata = {
                "file": file,
                "policy": "write_file",
                "reason": "policy"
            }
            transcript()._event(SandboxEvent(
                action="write_file",
                file=file,
                result=1,
                metadata=metadata,
                timestamp=datetime.now()
            ))
            raise SandboxPolicyViolationError(f"Writing to file '{file}' is denied by policy.")

        await self._inner.write_file(file, content)

    async def connection(self) -> SandboxConnection:
        return await self._inner.connection()
        
    def as_type(self, type: type[Any]) -> Any | None:
        # Delegate to inner if not self
        if isinstance(self, type):
            return self
        return self._inner.as_type(type)
    
    @classmethod
    async def sample_cleanup(cls, task_name: str, config: Any, environments: Dict[str, "SandboxEnvironment"], interrupted: bool) -> None:
        # NO-OP as per requirements. 
        pass

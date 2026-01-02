from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from ..models import Transaction


@runtime_checkable
class BaseJudge(Protocol):
    """
    Protocol-based judge contract.
    Any external developer can implement this with minimal code.
    """

    def judge(
        self,
        tx: Transaction,
        schema: Dict[str, Any],
        repair_mode: bool = False,
        **kwargs: Any,
    ) -> str:
        ...


class JudgeBase(ABC):
    """
    Backward compatible abstract base class.
    """

    @abstractmethod
    def judge(
        self,
        tx: Transaction,
        schema: Optional[Dict[str, Any]] = None,
        repair_mode: bool = False,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError

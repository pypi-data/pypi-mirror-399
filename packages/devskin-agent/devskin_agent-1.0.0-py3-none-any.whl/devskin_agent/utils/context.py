"""Context management using contextvars"""

from contextvars import ContextVar
from typing import Optional
from ..types import Span, Transaction

# Context variables for trace context propagation
_transaction_var: ContextVar[Optional[Transaction]] = ContextVar('transaction', default=None)
_current_span_var: ContextVar[Optional[Span]] = ContextVar('current_span', default=None)
_trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
_span_id_var: ContextVar[Optional[str]] = ContextVar('span_id', default=None)


class Context:
    """Context manager for trace context"""

    @staticmethod
    def set_transaction(transaction: Transaction) -> None:
        """Set the current transaction"""
        _transaction_var.set(transaction)
        _trace_id_var.set(transaction.trace_id)
        _span_id_var.set(transaction.span_id)

    @staticmethod
    def get_transaction() -> Optional[Transaction]:
        """Get the current transaction"""
        return _transaction_var.get()

    @staticmethod
    def set_span(span: Span) -> None:
        """Set the current span"""
        _current_span_var.set(span)
        _span_id_var.set(span.span_id)

    @staticmethod
    def get_span() -> Optional[Span]:
        """Get the current span"""
        return _current_span_var.get()

    @staticmethod
    def get_trace_id() -> Optional[str]:
        """Get the current trace ID"""
        return _trace_id_var.get()

    @staticmethod
    def get_span_id() -> Optional[str]:
        """Get the current span ID"""
        return _span_id_var.get()

    @staticmethod
    def clear() -> None:
        """Clear all context"""
        _transaction_var.set(None)
        _current_span_var.set(None)
        _trace_id_var.set(None)
        _span_id_var.set(None)

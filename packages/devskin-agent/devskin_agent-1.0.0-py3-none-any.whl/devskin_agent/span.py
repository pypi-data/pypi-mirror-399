"""Span and Transaction builders"""

from datetime import datetime
from typing import Optional, Any, Dict
from .types import Span, Transaction, SpanKind, SpanStatus, SpanEvent
from .utils import generate_span_id, generate_trace_id, Context


class SpanBuilder:
    """Builder for creating and managing spans"""

    def __init__(
        self,
        name: str,
        kind: SpanKind,
        service_name: str,
        service_version: Optional[str] = None,
        environment: Optional[str] = None,
        agent: Optional[Any] = None,
    ):
        parent_span = Context.get_span()
        trace_id = Context.get_trace_id() or generate_trace_id()

        self.span = Span(
            span_id=generate_span_id(),
            trace_id=trace_id,
            parent_span_id=parent_span.span_id if parent_span else None,
            name=name,
            kind=kind,
            start_time=datetime.utcnow(),
            status=SpanStatus.OK,
            attributes={},
            events=[],
            service_name=service_name,
            service_version=service_version,
            environment=environment,
        )

        self.agent = agent

        # Set this span as current in context
        Context.set_span(self.span)

    def set_attribute(self, key: str, value: Any) -> 'SpanBuilder':
        """Set an attribute on the span"""
        self.span.attributes[key] = value
        return self

    def set_attributes(self, attributes: Dict[str, Any]) -> 'SpanBuilder':
        """Set multiple attributes"""
        self.span.attributes.update(attributes)
        return self

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> 'SpanBuilder':
        """Add an event to the span"""
        event = SpanEvent(
            timestamp=datetime.utcnow(),
            name=name,
            attributes=attributes or {},
        )
        self.span.events.append(event)
        return self

    def set_status(self, status: SpanStatus, message: Optional[str] = None) -> 'SpanBuilder':
        """Set the span status"""
        self.span.status = status
        if message:
            self.span.status_message = message
        return self

    def record_error(self, error: Exception) -> 'SpanBuilder':
        """Mark the span as having an error"""
        self.set_status(SpanStatus.ERROR, str(error))
        self.set_attributes({
            'error.type': type(error).__name__,
            'error.message': str(error),
            'error.stack': self._get_traceback(error),
        })
        self.add_event('exception', {
            'exception.type': type(error).__name__,
            'exception.message': str(error),
        })
        return self

    def end(self) -> None:
        """End the span"""
        self.span.end_time = datetime.utcnow()
        self.span.duration_ms = (
            self.span.end_time - self.span.start_time
        ).total_seconds() * 1000

        # Report span to agent
        if self.agent and hasattr(self.agent, 'report_span'):
            self.agent.report_span(self.span)

    def get_span(self) -> Span:
        """Get the span data"""
        return self.span

    @staticmethod
    def _get_traceback(error: Exception) -> Optional[str]:
        """Get traceback from exception"""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))


class TransactionBuilder(SpanBuilder):
    """Builder for creating root spans (transactions)"""

    def __init__(
        self,
        name: str,
        transaction_type: str,
        service_name: str,
        service_version: Optional[str] = None,
        environment: Optional[str] = None,
        sampled: bool = True,
        agent: Optional[Any] = None,
    ):
        # Create parent span first
        super().__init__(name, SpanKind.SERVER, service_name, service_version, environment, agent)

        # Convert to transaction
        self.transaction = Transaction(
            span_id=self.span.span_id,
            trace_id=self.span.trace_id,
            parent_span_id=self.span.parent_span_id,
            name=name,
            kind=SpanKind.SERVER,
            start_time=self.span.start_time,
            status=self.span.status,
            attributes=self.span.attributes,
            events=self.span.events,
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            transaction_type=transaction_type,
            transaction_name=name,
            sampled=sampled,
        )

        # Set transaction in context
        Context.set_transaction(self.transaction)

    def set_result(self, result: str) -> 'TransactionBuilder':
        """Set the transaction result"""
        self.transaction.result = result
        return self

    def end(self) -> None:
        """End the transaction"""
        self.transaction.end_time = datetime.utcnow()
        self.transaction.duration_ms = (
            self.transaction.end_time - self.transaction.start_time
        ).total_seconds() * 1000

        # Report transaction to agent
        if self.agent and hasattr(self.agent, 'report_transaction'):
            self.agent.report_transaction(self.transaction)

    def get_transaction(self) -> Transaction:
        """Get the transaction data"""
        return self.transaction

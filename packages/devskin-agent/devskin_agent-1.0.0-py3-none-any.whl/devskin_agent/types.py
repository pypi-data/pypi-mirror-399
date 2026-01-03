"""Type definitions for DevSkin APM Agent"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


class SpanKind(str, Enum):
    """Span kind enumeration"""
    SERVER = 'server'
    CLIENT = 'client'
    INTERNAL = 'internal'
    PRODUCER = 'producer'
    CONSUMER = 'consumer'


class SpanStatus(str, Enum):
    """Span status enumeration"""
    OK = 'ok'
    ERROR = 'error'


@dataclass
class SpanEvent:
    """Span event data"""
    timestamp: datetime
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Span data structure"""
    span_id: str
    trace_id: str
    name: str
    kind: SpanKind
    start_time: datetime
    status: SpanStatus
    service_name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[SpanEvent] = field(default_factory=list)
    parent_span_id: Optional[str] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status_message: Optional[str] = None
    service_version: Optional[str] = None
    environment: Optional[str] = None


@dataclass
class Transaction(Span):
    """Transaction (root span) data structure"""
    transaction_type: str = ''
    transaction_name: str = ''
    result: Optional[str] = None
    sampled: bool = True


@dataclass
class LogEntry:
    """Log entry data structure"""
    timestamp: datetime
    level: str
    message: str
    service_name: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    environment: Optional[str] = None


@dataclass
class ErrorData:
    """Error data structure"""
    timestamp: datetime
    message: str
    type: str
    service_name: str
    stack_trace: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    environment: Optional[str] = None


@dataclass
class AgentConfig:
    """Agent configuration"""
    server_url: str
    api_key: str
    service_name: str
    service_version: Optional[str] = None
    environment: Optional[str] = None
    enabled: bool = True
    sample_rate: float = 1.0
    instrument_flask: bool = True
    instrument_django: bool = True
    instrument_fastapi: bool = True
    batch_size: int = 100
    flush_interval: float = 10.0
    debug: bool = False

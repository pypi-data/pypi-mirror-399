"""Core DevSkin APM Agent"""

import threading
import time
import sys
from typing import Optional, List
from .types import AgentConfig, Span, Transaction, LogEntry, ErrorData
from .api_client import ApiClient
from .utils import should_sample


class Agent:
    """DevSkin APM Agent"""

    def __init__(self, config: AgentConfig):
        self.config = config

        if not self.config.enabled:
            print('[DevSkin Agent] Agent is disabled')
            return

        if not all([config.server_url, config.api_key, config.service_name]):
            raise ValueError('[DevSkin Agent] server_url, api_key, and service_name are required')

        self.api_client = ApiClient(
            config.server_url,
            config.api_key,
            config.service_name,
            config.debug
        )

        self.span_buffer: List[Span] = []
        self.transaction_buffer: List[Transaction] = []
        self.log_buffer: List[LogEntry] = []
        self.error_buffer: List[ErrorData] = []

        self.flush_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.initialized = False

    def start(self) -> None:
        """Start the agent"""
        if not self.config.enabled:
            return

        if self.initialized:
            return

        self.initialized = True

        if self.config.debug:
            print(f'[DevSkin Agent] Starting agent for service: {self.config.service_name}')

        # Send service metadata
        self._send_service_metadata()

        # Start flush thread
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()

        if self.config.debug:
            print('[DevSkin Agent] Agent started successfully')

    def stop(self) -> None:
        """Stop the agent"""
        if not self.config.enabled:
            return

        if self.config.debug:
            print('[DevSkin Agent] Stopping agent...')

        self.stop_event.set()

        if self.flush_thread:
            self.flush_thread.join(timeout=5)

        self.flush()

        self.initialized = False

        if self.config.debug:
            print('[DevSkin Agent] Agent stopped')

    def _send_service_metadata(self) -> None:
        """Send service metadata for discovery"""
        try:
            self.api_client.send_service_metadata({
                'service_version': self.config.service_version,
                'environment': self.config.environment,
                'language': 'python',
                'language_version': f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}',
                'metadata': {
                    'platform': sys.platform,
                    'python_version': sys.version,
                },
            })
        except Exception as e:
            if self.config.debug:
                print(f'[DevSkin Agent] Failed to send service metadata: {e}')

    def _flush_loop(self) -> None:
        """Background thread for periodic flushing"""
        while not self.stop_event.is_set():
            time.sleep(self.config.flush_interval)
            self.flush()

    def report_span(self, span: Span) -> None:
        """Report a span"""
        if not self.config.enabled:
            return

        with self.lock:
            self.span_buffer.append(span)

            if len(self.span_buffer) >= self.config.batch_size:
                self.flush()

    def report_transaction(self, transaction: Transaction) -> None:
        """Report a transaction"""
        if not self.config.enabled:
            return

        with self.lock:
            self.transaction_buffer.append(transaction)

            if len(self.transaction_buffer) >= self.config.batch_size:
                self.flush()

    def report_log(self, log: LogEntry) -> None:
        """Report a log entry"""
        if not self.config.enabled:
            return

        with self.lock:
            self.log_buffer.append(log)

            if len(self.log_buffer) >= self.config.batch_size:
                self.flush()

    def report_error(self, error: ErrorData) -> None:
        """Report an error"""
        if not self.config.enabled:
            return

        with self.lock:
            self.error_buffer.append(error)

            if len(self.error_buffer) >= self.config.batch_size:
                self.flush()

    def flush(self) -> None:
        """Flush all buffered data"""
        if not self.config.enabled:
            return

        with self.lock:
            spans = self.span_buffer[:]
            transactions = self.transaction_buffer[:]
            logs = self.log_buffer[:]
            errors = self.error_buffer[:]

            self.span_buffer.clear()
            self.transaction_buffer.clear()
            self.log_buffer.clear()
            self.error_buffer.clear()

        try:
            self.api_client.send_spans(spans)
            self.api_client.send_transactions(transactions)
            self.api_client.send_logs(logs)
            self.api_client.send_errors(errors)
        except Exception as e:
            if self.config.debug:
                print(f'[DevSkin Agent] Failed to flush data: {e}')

    def get_config(self) -> AgentConfig:
        """Get agent configuration"""
        return self.config

    def should_sample(self) -> bool:
        """Check if sampling is enabled for this request"""
        return should_sample(self.config.sample_rate)


# Global agent instance
_global_agent: Optional[Agent] = None


def init(
    server_url: str,
    api_key: str,
    service_name: str,
    service_version: Optional[str] = None,
    environment: Optional[str] = None,
    enabled: bool = True,
    sample_rate: float = 1.0,
    batch_size: int = 100,
    flush_interval: float = 10.0,
    debug: bool = False,
) -> Agent:
    """Initialize the global agent"""
    global _global_agent

    if _global_agent:
        print('[DevSkin Agent] Agent already initialized')
        return _global_agent

    config = AgentConfig(
        server_url=server_url,
        api_key=api_key,
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        enabled=enabled,
        sample_rate=sample_rate,
        batch_size=batch_size,
        flush_interval=flush_interval,
        debug=debug,
    )

    _global_agent = Agent(config)
    return _global_agent


def get_agent() -> Optional[Agent]:
    """Get the global agent instance"""
    return _global_agent


def start_agent() -> None:
    """Start the global agent"""
    if not _global_agent:
        raise RuntimeError('[DevSkin Agent] Agent not initialized. Call init() first.')
    _global_agent.start()


def stop_agent() -> None:
    """Stop the global agent"""
    if _global_agent:
        _global_agent.stop()

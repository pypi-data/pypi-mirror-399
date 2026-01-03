"""API client for sending data to DevSkin backend"""

import requests
from typing import List
from .types import Span, Transaction, LogEntry, ErrorData


class ApiClient:
    """API client for DevSkin backend"""

    def __init__(self, server_url: str, api_key: str, service_name: str, debug: bool = False):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.service_name = service_name
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-DevSkin-API-Key': api_key,
        })

    def send_spans(self, spans: List[Span]) -> None:
        """Send spans to the backend"""
        if not spans:
            return

        try:
            if self.debug:
                print(f'[DevSkin Agent] Sending {len(spans)} spans')

            # Convert dataclass instances to dicts
            spans_data = [self._span_to_dict(span) for span in spans]

            self.session.post(
                f'{self.server_url}/api/v1/apm/spans',
                json={
                    'service_name': self.service_name,
                    'spans': spans_data,
                },
                timeout=30
            )
        except Exception as e:
            print(f'[DevSkin Agent] Failed to send spans: {e}')

    def send_transactions(self, transactions: List[Transaction]) -> None:
        """Send transactions to the backend"""
        if not transactions:
            return

        try:
            if self.debug:
                print(f'[DevSkin Agent] Sending {len(transactions)} transactions')

            # Convert dataclass instances to dicts
            transactions_data = [self._span_to_dict(txn) for txn in transactions]

            self.session.post(
                f'{self.server_url}/api/v1/apm/transactions',
                json={
                    'service_name': self.service_name,
                    'transactions': transactions_data,
                },
                timeout=30
            )
        except Exception as e:
            print(f'[DevSkin Agent] Failed to send transactions: {e}')

    def send_logs(self, logs: List[LogEntry]) -> None:
        """Send logs to the backend"""
        if not logs:
            return

        try:
            if self.debug:
                print(f'[DevSkin Agent] Sending {len(logs)} logs')

            logs_data = [self._log_to_dict(log) for log in logs]

            self.session.post(
                f'{self.server_url}/api/v1/logs/batch',
                json={
                    'service_name': self.service_name,
                    'logs': logs_data,
                },
                timeout=30
            )
        except Exception as e:
            print(f'[DevSkin Agent] Failed to send logs: {e}')

    def send_errors(self, errors: List[ErrorData]) -> None:
        """Send errors to the backend"""
        if not errors:
            return

        try:
            if self.debug:
                print(f'[DevSkin Agent] Sending {len(errors)} errors')

            errors_data = [self._error_to_dict(error) for error in errors]

            self.session.post(
                f'{self.server_url}/api/v1/apm/errors',
                json={
                    'service_name': self.service_name,
                    'errors': errors_data,
                },
                timeout=30
            )
        except Exception as e:
            print(f'[DevSkin Agent] Failed to send errors: {e}')

    def send_service_metadata(self, metadata: dict) -> None:
        """Send service metadata for discovery"""
        try:
            if self.debug:
                print('[DevSkin Agent] Sending service metadata')

            self.session.post(
                f'{self.server_url}/api/v1/apm/services',
                json={
                    'service_name': self.service_name,
                    **metadata,
                },
                timeout=30
            )
        except Exception as e:
            print(f'[DevSkin Agent] Failed to send service metadata: {e}')

    @staticmethod
    def _span_to_dict(span: Span) -> dict:
        """Convert Span dataclass to dict with proper datetime serialization"""
        data = {
            'span_id': span.span_id,
            'trace_id': span.trace_id,
            'parent_span_id': span.parent_span_id,
            'name': span.name,
            'kind': span.kind.value if hasattr(span.kind, 'value') else span.kind,
            'start_time': span.start_time.isoformat(),
            'end_time': span.end_time.isoformat() if span.end_time else None,
            'duration_ms': span.duration_ms,
            'status': span.status.value if hasattr(span.status, 'value') else span.status,
            'status_message': span.status_message,
            'attributes': span.attributes,
            'service_name': span.service_name,
            'service_version': span.service_version,
            'environment': span.environment,
            'events': [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'name': event.name,
                    'attributes': event.attributes,
                }
                for event in span.events
            ],
        }

        # Add transaction-specific fields
        if isinstance(span, Transaction):
            data.update({
                'transaction_type': span.transaction_type,
                'transaction_name': span.transaction_name,
                'result': span.result,
                'sampled': span.sampled,
            })

        return data

    @staticmethod
    def _log_to_dict(log: LogEntry) -> dict:
        """Convert LogEntry dataclass to dict"""
        return {
            'timestamp': log.timestamp.isoformat(),
            'level': log.level,
            'message': log.message,
            'trace_id': log.trace_id,
            'span_id': log.span_id,
            'attributes': log.attributes,
            'service_name': log.service_name,
            'environment': log.environment,
        }

    @staticmethod
    def _error_to_dict(error: ErrorData) -> dict:
        """Convert ErrorData dataclass to dict"""
        return {
            'timestamp': error.timestamp.isoformat(),
            'message': error.message,
            'type': error.type,
            'stack_trace': error.stack_trace,
            'trace_id': error.trace_id,
            'span_id': error.span_id,
            'attributes': error.attributes,
            'service_name': error.service_name,
            'environment': error.environment,
        }

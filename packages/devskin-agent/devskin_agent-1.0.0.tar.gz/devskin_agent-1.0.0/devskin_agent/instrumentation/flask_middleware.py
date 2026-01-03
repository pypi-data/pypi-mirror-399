"""Flask middleware for DevSkin APM Agent"""

from functools import wraps
from datetime import datetime
from flask import Flask, request, g
from ..agent import Agent
from ..span import TransactionBuilder
from ..utils.context import Context
from ..types import ErrorData


def flask_middleware(app: Flask, agent: Agent):
    """
    Flask middleware for automatic transaction creation

    Usage:
        from flask import Flask
        from devskin_agent import init, start_agent
        from devskin_agent.instrumentation import flask_middleware

        agent = init(...)
        start_agent()

        app = Flask(__name__)
        flask_middleware(app, agent)
    """

    @app.before_request
    def before_request():
        # Check if we should sample this request
        if not agent.should_sample():
            return

        # Extract trace context from headers
        incoming_trace_id = request.headers.get('X-Trace-Id')
        incoming_span_id = request.headers.get('X-Span-Id')

        # Create transaction
        config = agent.get_config()
        route = str(request.url_rule) if request.url_rule else request.path

        transaction = TransactionBuilder(
            name=f'{request.method} {route}',
            transaction_type='http.request',
            service_name=config.service_name,
            service_version=config.service_version,
            environment=config.environment,
            sampled=True,
            agent=agent,
        )

        # If there's an incoming trace ID, use it
        if incoming_trace_id:
            transaction.get_transaction().trace_id = incoming_trace_id
            if incoming_span_id:
                transaction.get_transaction().parent_span_id = incoming_span_id

        transaction.set_attributes({
            'http.method': request.method,
            'http.url': request.url,
            'http.target': request.path,
            'http.route': route,
            'http.host': request.host,
            'http.scheme': request.scheme,
            'http.user_agent': request.headers.get('User-Agent'),
            'net.peer.ip': request.remote_addr,
        })

        # Store transaction in Flask's g object
        g.devskin_transaction = transaction

    @app.after_request
    def after_request(response):
        transaction = getattr(g, 'devskin_transaction', None)
        if transaction:
            transaction.set_attributes({
                'http.status_code': response.status_code,
            })

            if response.status_code >= 400:
                transaction.set_status('error', f'HTTP {response.status_code}')

            transaction.set_result('success' if response.status_code < 400 else 'error')
            transaction.end()

        return response

    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        transaction = getattr(g, 'devskin_transaction', None)
        if transaction:
            transaction.record_error(error)
            transaction.set_result('error')
            transaction.end()

        # Report error to agent
        config = agent.get_config()
        agent.report_error(ErrorData(
            timestamp=datetime.utcnow(),
            message=str(error),
            type=type(error).__name__,
            stack_trace=_get_traceback(error),
            trace_id=Context.get_trace_id(),
            span_id=Context.get_span_id(),
            attributes={
                'http.method': request.method,
                'http.url': request.url,
                'http.route': str(request.url_rule) if request.url_rule else request.path,
            },
            service_name=config.service_name,
            environment=config.environment,
        ))

        # Re-raise the exception
        raise


def _get_traceback(error: Exception) -> str:
    """Get traceback from exception"""
    import traceback
    return ''.join(traceback.format_exception(type(error), error, error.__traceback__))

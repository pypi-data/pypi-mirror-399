"""Django middleware for DevSkin APM Agent"""

from datetime import datetime
from ..agent import Agent, get_agent
from ..span import TransactionBuilder
from ..utils.context import Context
from ..types import ErrorData


class DjangoMiddleware:
    """
    Django middleware for automatic transaction creation

    Usage in settings.py:

        MIDDLEWARE = [
            'devskin_agent.instrumentation.DjangoMiddleware',
            ...
        ]

        # At the end of settings.py:
        from devskin_agent import init, start_agent

        DEVSKIN_AGENT = init(
            server_url='http://localhost:3000',
            api_key='your-api-key',
            service_name='my-django-app',
        )
        start_agent()
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.agent = None

    def __call__(self, request):
        # Get agent instance
        if not self.agent:
            self.agent = get_agent()

        if not self.agent or not self.agent.should_sample():
            return self.get_response(request)

        # Extract trace context from headers
        incoming_trace_id = request.META.get('HTTP_X_TRACE_ID')
        incoming_span_id = request.META.get('HTTP_X_SPAN_ID')

        # Create transaction
        config = self.agent.get_config()
        route = request.resolver_match.route if hasattr(request, 'resolver_match') and request.resolver_match else request.path

        transaction = TransactionBuilder(
            name=f'{request.method} {route}',
            transaction_type='http.request',
            service_name=config.service_name,
            service_version=config.service_version,
            environment=config.environment,
            sampled=True,
            agent=self.agent,
        )

        # If there's an incoming trace ID, use it
        if incoming_trace_id:
            transaction.get_transaction().trace_id = incoming_trace_id
            if incoming_span_id:
                transaction.get_transaction().parent_span_id = incoming_span_id

        transaction.set_attributes({
            'http.method': request.method,
            'http.url': request.build_absolute_uri(),
            'http.target': request.path,
            'http.route': route,
            'http.host': request.get_host(),
            'http.scheme': request.scheme,
            'http.user_agent': request.META.get('HTTP_USER_AGENT'),
            'net.peer.ip': self._get_client_ip(request),
        })

        # Store transaction
        request.devskin_transaction = transaction

        try:
            response = self.get_response(request)

            transaction.set_attributes({
                'http.status_code': response.status_code,
            })

            if response.status_code >= 400:
                transaction.set_status('error', f'HTTP {response.status_code}')

            transaction.set_result('success' if response.status_code < 400 else 'error')
            transaction.end()

            return response

        except Exception as error:
            transaction.record_error(error)
            transaction.set_result('error')
            transaction.end()

            # Report error to agent
            self.agent.report_error(ErrorData(
                timestamp=datetime.utcnow(),
                message=str(error),
                type=type(error).__name__,
                stack_trace=self._get_traceback(error),
                trace_id=Context.get_trace_id(),
                span_id=Context.get_span_id(),
                attributes={
                    'http.method': request.method,
                    'http.url': request.build_absolute_uri(),
                    'http.route': route,
                },
                service_name=config.service_name,
                environment=config.environment,
            ))

            raise

    @staticmethod
    def _get_client_ip(request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    @staticmethod
    def _get_traceback(error: Exception) -> str:
        """Get traceback from exception"""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))

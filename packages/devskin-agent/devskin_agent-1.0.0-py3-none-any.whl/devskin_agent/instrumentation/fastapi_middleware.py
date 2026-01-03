"""FastAPI middleware for DevSkin APM Agent"""

from datetime import datetime
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ..agent import Agent
from ..span import TransactionBuilder
from ..utils.context import Context
from ..types import ErrorData


class FastAPIMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic transaction creation"""

    def __init__(self, app: FastAPI, agent: Agent):
        super().__init__(app)
        self.agent = agent

    async def dispatch(self, request: Request, call_next):
        # Check if we should sample this request
        if not self.agent.should_sample():
            return await call_next(request)

        # Extract trace context from headers
        incoming_trace_id = request.headers.get('x-trace-id')
        incoming_span_id = request.headers.get('x-span-id')

        # Create transaction
        config = self.agent.get_config()
        route = request.url.path

        # Try to get route pattern from FastAPI
        if hasattr(request, 'scope') and 'route' in request.scope:
            route_obj = request.scope['route']
            if hasattr(route_obj, 'path'):
                route = route_obj.path

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
            'http.url': str(request.url),
            'http.target': request.url.path,
            'http.route': route,
            'http.host': request.url.hostname,
            'http.scheme': request.url.scheme,
            'http.user_agent': request.headers.get('user-agent'),
            'net.peer.ip': request.client.host if request.client else None,
        })

        try:
            response = await call_next(request)

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
                    'http.url': str(request.url),
                    'http.route': route,
                },
                service_name=config.service_name,
                environment=config.environment,
            ))

            raise

    @staticmethod
    def _get_traceback(error: Exception) -> str:
        """Get traceback from exception"""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))


def fastapi_middleware(app: FastAPI, agent: Agent):
    """
    Add FastAPI middleware for automatic transaction creation

    Usage:
        from fastapi import FastAPI
        from devskin_agent import init, start_agent
        from devskin_agent.instrumentation import fastapi_middleware

        agent = init(...)
        start_agent()

        app = FastAPI()
        fastapi_middleware(app, agent)
    """
    app.add_middleware(FastAPIMiddleware, agent=agent)

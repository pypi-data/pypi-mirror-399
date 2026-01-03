"""
DevSkin APM Agent for Python

Example usage:

```python
from devskin_agent import init, start_agent

agent = init(
    server_url='http://localhost:3000',
    api_key='your-api-key',
    service_name='my-python-service',
    service_version='1.0.0',
    environment='production',
)

start_agent()
```
"""

from .agent import Agent, init, get_agent, start_agent, stop_agent
from .span import SpanBuilder, TransactionBuilder
from .types import SpanKind, SpanStatus, AgentConfig

__version__ = '1.0.0'

__all__ = [
    'Agent',
    'init',
    'get_agent',
    'start_agent',
    'stop_agent',
    'SpanBuilder',
    'TransactionBuilder',
    'SpanKind',
    'SpanStatus',
    'AgentConfig',
]

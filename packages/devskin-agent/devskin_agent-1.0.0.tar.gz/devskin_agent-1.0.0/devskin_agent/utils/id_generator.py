"""ID generation utilities"""

import secrets
import random


def generate_trace_id() -> str:
    """Generate a random trace ID (16 bytes / 32 hex chars)"""
    return secrets.token_hex(16)


def generate_span_id() -> str:
    """Generate a random span ID (8 bytes / 16 hex chars)"""
    return secrets.token_hex(8)


def should_sample(sample_rate: float) -> bool:
    """Check if a value should be sampled based on sample rate"""
    return random.random() < sample_rate

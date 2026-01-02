"""
Libra AI SDK for Python

Official Python SDK for interacting with Libra AI API.

Usage:
    from libra_ai import LibraAI
    
    libra = LibraAI('lak_your_api_key')
    answer = libra.ask('Hello!')
    print(answer)
"""

from .client import LibraAI, LibraError

__all__ = ['LibraAI', 'LibraError']
__version__ = '1.0.0'

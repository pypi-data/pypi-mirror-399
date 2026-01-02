"""
Libra AI Client

This module provides the main LibraAI client class for interacting with the Libra AI API.
"""

import requests
from typing import Optional, Dict, Any, TypedDict


class UsageLimits(TypedDict):
    """Rate limit information."""
    requestsPerMinute: int
    requestsPerDay: int


class UsageInfo(TypedDict):
    """Usage information in response."""
    tier: str
    limits: UsageLimits


class ResponseData(TypedDict, total=False):
    """Data returned in successful response."""
    message: str
    model: str
    usage: UsageInfo
    keyName: str


class LibraResponse(TypedDict):
    """Response from Libra AI API."""
    success: bool
    data: Optional[ResponseData]
    error: Optional[str]
    timestamp: str


class LibraError(Exception):
    """Exception raised when Libra AI API returns an error."""
    pass


class LibraAI:
    """
    Libra AI Python SDK
    
    A client for interacting with the Libra AI API.
    
    Attributes:
        api_key: Your Libra API key (starts with lak_)
        base_url: The base URL for the API
    
    Example:
        >>> libra = LibraAI('lak_your_api_key')
        >>> answer = libra.ask('What is Python?')
        >>> print(answer)
    """
    
    def __init__(self, api_key: str, base_url: str = 'https://libra-ai.com'):
        """
        Create a new LibraAI client.
        
        Args:
            api_key: Your Libra API key (starts with lak_)
            base_url: Optional custom base URL (default: https://libra-ai.com)
        
        Raises:
            ValueError: If the API key is invalid
        """
        if not api_key or not api_key.startswith('lak_'):
            raise ValueError('Invalid API key. API key must start with "lak_"')
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        })
    
    def chat(
        self,
        message: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> LibraResponse:
        """
        Send a chat message to Libra AI.
        
        Args:
            message: Your message to Libra AI
            model: Optional model to use
            max_tokens: Maximum tokens in response (default: 2048)
            temperature: Creativity 0-1 (default: 0.7)
            system_prompt: Custom system instructions
            
        Returns:
            LibraResponse with success status and data
            
        Raises:
            ValueError: If message is empty
            LibraError: If API returns an error
        
        Example:
            >>> response = libra.chat('Explain Python', temperature=0.5)
            >>> print(response['data']['message'])
        """
        if not message or not message.strip():
            raise ValueError('Message cannot be empty')
        
        payload: Dict[str, Any] = {
            'message': message.strip()
        }
        
        if model:
            payload['model'] = model
        if max_tokens:
            payload['maxTokens'] = max_tokens
        if temperature is not None:
            payload['temperature'] = temperature
        if system_prompt:
            payload['systemPrompt'] = system_prompt
        
        response = self._session.post(
            f'{self.base_url}/api/v1/chat',
            json=payload
        )
        
        data: LibraResponse = response.json()
        
        if not data.get('success'):
            raise LibraError(data.get('error', 'Unknown error occurred'))
        
        return data
    
    def ask(
        self,
        message: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Simple chat - returns just the message string.
        
        Args:
            message: Your message to Libra AI
            model: Optional model to use
            max_tokens: Maximum tokens in response
            temperature: Creativity 0-1
            system_prompt: Custom system instructions
            
        Returns:
            AI response message as string
        
        Example:
            >>> answer = libra.ask('What is AI?')
            >>> print(answer)
        """
        response = self.chat(
            message=message,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt
        )
        data = response.get('data')
        if data:
            return data.get('message', '')
        return ''
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get API info and rate limits.
        
        Returns:
            Dictionary with API information
        """
        response = self._session.get(f'{self.base_url}/api/v1/chat')
        return response.json()
    
    def __repr__(self) -> str:
        """String representation of the client."""
        masked_key = self.api_key[:8] + '...' + self.api_key[-4:]
        return f'LibraAI(api_key="{masked_key}", base_url="{self.base_url}")'

# libra-ai-sdk

Official Libra AI SDK for Python.

## Installation

```bash
pip install libra-ai-sdk
```

## Quick Start

```python
from libra_ai import LibraAI

libra = LibraAI('lak_your_api_key')

# Simple usage
answer = libra.ask('What is Python?')
print(answer)

# With options
response = libra.chat(
    'Explain machine learning',
    temperature=0.5,
    max_tokens=1000
)
print(response['data']['message'])
```

## API Reference

### Constructor

```python
LibraAI(api_key: str, base_url: str = 'https://libra-ai.com')
```

- `api_key` - Your Libra API key (starts with `lak_`)
- `base_url` - Optional custom base URL

### Methods

#### `chat(message, **options)`

Send a message and get the full response object.

```python
response = libra.chat(
    'Hello!',
    model='default',
    max_tokens=2048,
    temperature=0.7,
    system_prompt='You are a helpful assistant'
)
```

#### `ask(message, **options)`

Simple method that returns just the AI response as a string.

```python
answer = libra.ask('What is AI?')
```

#### `get_info()`

Get API info and rate limits.

```python
info = libra.get_info()
```

## Rate Limits

| Tier | Requests/min | Requests/day | Max Tokens |
|------|-------------|--------------|------------|
| Basic | 10 | 100 | 2048 |
| Pro | 60 | 1000 | 8192 |

## Requirements

- Python >= 3.8
- requests >= 2.25.0

## License

MIT © IndoNusaCorp

# hiinsta

A Python package for interacting with Instagram's messaging API.

## Installation

```bash
pip install hiinsta
```

## Usage

```python
from hiinsta import InstagramMessenger

messenger = InstagramMessenger(access_token="YOUR_ACCESS_TOKEN")

# Example usage
message_id = await messenger.send_text("Hello, World!", recipient_id="RECIPIENT_ID")

print(message_id)
```

## Development

To install in development mode:

```bash
git clone https://github.com/cervant-ai/hiinsta.git
cd hiinsta
pip install -e .
```

To install development dependencies:

```bash
pip install -e ".[dev]"
```

## Testing

```bash
pytest
```

```bash
pip install -e ".[dev]"
```

## Testing

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

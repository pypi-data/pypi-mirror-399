# Changelog

All notable changes to the EnkaliPrime Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2] - 2024-12-29

### Added

- **Connection Animation** - Show engaging animation during API key resolution
  - New `show_connection` parameter in `send_message()` method (default: True)
  - Displays "🌐 Connecting to EnkaliPrime" with rotating earth animation (🌍🌎🌏)
  - Only shows on first message per session when connection resolution is needed
  - Automatically cached for subsequent messages in the same session
  - Makes the initial connection delay more engaging and informative

### Improved

- **Enhanced User Experience** - Connection resolution now provides visual feedback
  - Users see exactly what's happening during the initial API key resolution
  - Professional loading experience with thematic animations
  - Smart caching prevents repeated connection animations

## [1.2.1] - 2024-12-29

### Improved

- **Simplified Loading API** - `loading=True` now shows beautiful Unicode brain animation
  - `loading=True` displays "🧠 Thinking" with animated brain emoji sequence
  - Much cleaner API - no need for complex dictionary configurations
  - Default brain animation uses cyan color and cycles through 🧠💭💡✨
  - Backward compatible - all existing loading options still work

### Technical

- Enhanced `send_message()` method to handle `loading=True` with smart defaults
- Improved user experience with more intuitive loading parameter

---

## [1.2.0] - 2024-12-29

### Added

- **Enhanced Type System** - Superior cross-editor support with advanced type annotations
  - `.pyi` stub files for all modules providing pure type information
  - `Literal` types for exact autocomplete on spinner styles, colors, and message roles
  - `Union` and `Generic` types for better type safety
  - Runtime type guard functions for additional validation
- **Type Guards** - New `type_guards.py` module with validation functions:
  - `is_conversation_context()` - Validate conversation history format
  - `is_loading_config()` - Validate loading animation configurations
  - `is_spinner_style()` - Check spinner style validity
  - `is_color_name()` - Validate color names
  - `is_valid_api_key()` - API key format validation
  - `is_valid_session_id()` - Session ID validation
  - `validate_message_content()` - Message content safety checks
- **Improved Developer Experience**
  - Enhanced IntelliSense support across all Python editors (VS Code, PyCharm, Vim, Emacs, etc.)
  - Better autocomplete with literal type constraints
  - More precise type checking with mypy and other type checkers
  - Runtime type safety with comprehensive validation

### Enhanced

- **Type Annotations** - Upgraded all type hints to use modern typing features
  - `ConversationContext` type alias for conversation history
  - `LoadingConfig` union type for flexible loading parameters
  - `SpinnerStyle` and `ColorName` literal types
- **Package Distribution** - Include `.pyi` stub files in distribution for better IDE support
- **Documentation** - Updated README with enhanced type system information

### Technical

- Added `typing_extensions` dependency for `Literal` type support
- Enhanced `__all__` exports to include new types and functions
- Improved package metadata for better type-aware installations

---

## [1.1.0] - 2024-12-17

### Added

- **Terminal Loading Animations** - Cool spinner animations while waiting for AI responses
  - `Spinner` class with 12+ animation styles (dots, pulse, moon, brain, arrows, etc.)
  - `LoadingBar` class for pulsing progress bar animation
  - Built-in `loading` parameter in `send_message()` for easy integration
  - Color support: cyan, green, yellow, blue, magenta, white
  - Elapsed time display during loading
- Convenience functions: `spinner()` and `loading_bar()` for standalone use

### Usage

```python
# Simple loading animation
response = client.send_message("Hello", session_id="123", loading=True)

# Custom message
response = client.send_message("Hello", session_id="123", loading="Thinking")

# Full customization
response = client.send_message(
    "Hello",
    session_id="123",
    loading={"message": "Processing", "style": "brain", "color": "magenta"}
)
```

---

## [1.0.0] - 2024-12-17

### Added

- Initial release of the EnkaliPrime Python SDK
- `EnkaliPrimeClient` class for interacting with the EnkaliPrime Chat API
- Support for synchronous and asynchronous operations
- Streaming response support with callbacks
- Session management (create, end, get)
- Conversation history management
- Full type hints and PEP 561 compliance
- Data models:
  - `ChatMessage`
  - `ChatSession`
  - `ResolvedConnection`
  - `ChatApiConfig`
  - `ChatRequest`
- Custom exceptions:
  - `EnkaliPrimeError`
  - `ConnectionError`
  - `AuthenticationError`
  - `APIError`
  - `StreamingError`
  - `ValidationError`
  - `SessionError`
- Context manager support for resource cleanup
- Comprehensive test suite
- Examples for:
  - Basic usage
  - Streaming responses
  - Async operations
  - Interactive CLI chat
  - FastAPI integration
- Documentation with API reference and usage examples

### Security

- Secure API key handling
- HTTPS-only communication
- No sensitive data logging

---

## [Unreleased]

### Planned

- Retry logic with exponential backoff
- Webhook support for push notifications
- Built-in rate limiting
- Local caching for conversation history
- More framework integrations (Django, Flask blueprints)


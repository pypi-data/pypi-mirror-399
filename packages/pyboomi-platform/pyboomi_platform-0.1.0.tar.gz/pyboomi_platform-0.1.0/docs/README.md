# PyBoomi Platform Documentation

Welcome to the PyBoomi Platform SDK documentation. This documentation provides comprehensive guides and API references for using the Python SDK to interact with the Boomi Platform API.

## Documentation Structure

### User Guides

- **[Getting Started](guides/getting-started.md)** - Installation, basic setup, and your first API call
- **[Authentication](guides/authentication.md)** - Understanding authentication methods and configuration
- **[Folder Management](guides/folder-management.md)** - Creating, querying, updating, and deleting folders
- **[Component Management](guides/component-management.md)** - Working with processes, connections, and components
- **[Execution Monitoring](guides/execution-monitoring.md)** - Querying execution records and downloading artifacts
- **[Error Handling](guides/error-handling.md)** - Understanding exceptions and error responses
- **[Retry Behavior](guides/retry-behavior.md)** - Retry logic, rate limiting, and backoff strategies

### API Reference

- **[BoomiPlatformClient](api/client.md)** - Main client class with all API methods
- **[Config](api/config.md)** - Configuration management class
- **[BoomiAuth](api/auth.md)** - Authentication handling
- **[BoomiAPIError](api/exceptions.md)** - Exception classes
- **[Utils](api/utils.md)** - Utility functions

## Quick Links

- [Installation](guides/getting-started.md#installation)
- [Quick Start Example](guides/getting-started.md#quick-start)
- [Configuration Options](guides/authentication.md#configuration-methods)
- [API Reference Index](api/client.md)

## Examples

For practical code examples, see the `examples/` directory in the repository:

- `example_01_basic_client_and_folders.py` - Client initialization and folder operations
- `example_02_component_management.py` - Component creation and management
- `example_03_execution_monitoring.py` - Execution monitoring and artifact downloads

## Additional Resources

- [GitHub Repository](https://github.com/iesoftwaredeveloper/pyboomi-platform)
- [Boomi Platform API Documentation](https://developer.boomi.com/docs/api/platformapi/)
- [CHANGELOG](../CHANGELOG.md)

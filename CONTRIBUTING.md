# Development Guidelines

## Code Style

- Follow PEP 8 guidelines
- Use 4-space indentation
- Maximum line length: 100 characters
- Use type hints where possible

## Testing

Before submitting changes:

1. Run the test suite:
   ```bash
   python test_api.py
   # or
   bash test_api.sh
   ```

2. Check for errors:
   ```bash
   python -m py_compile app.py
   ```

## Adding New Features

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Update documentation
5. Submit a pull request

## Logging

Use the existing logging setup for debug information:

```python
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

## Error Handling

- Always handle specific exceptions before generic ones
- Log errors appropriately
- Return meaningful error messages to users
- Use appropriate HTTP status codes

## API Changes

- Maintain backward compatibility when possible
- Update README.md with new endpoints/parameters
- Include examples in documentation

## Docker Updates

When modifying Dockerfile:

1. Test the build: `docker-compose build`
2. Test the container: `docker-compose up`
3. Verify health checks pass
4. Run full test suite

## Dependency Management

- Update requirements.txt when adding new packages
- Pin specific versions for stability
- Regularly check for security updates

## Documentation

- Add docstrings to new functions
- Update README.md for user-facing changes
- Include examples for new features
- Keep inline comments clear and concise

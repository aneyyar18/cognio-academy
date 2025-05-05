# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands
- Run application: `python app.py`
- Debug mode is enabled in development

## Testing
- No test framework implemented yet
- When implemented, use `pytest` as the standard Python testing framework

## Linting & Code Style
- Follow PEP 8 conventions for Python code
- Use snake_case for functions and variables
- Use CamelCase for class names
- Group imports: standard lib first, then third-party, then local
- Docstrings for all functions and classes
- Meaningful variable names that reflect their purpose
- Maintain Flask blueprint organization with views/ directory

## Error Handling
- Use appropriate HTTP status codes for API responses
- Collect form validation errors and flash to users
- Log errors for debugging using Flask's logging features

## Database Patterns
- SQLite database stored in SqliteDb/ directory
- Use SQLAlchemy ORM for database operations
- Follow model definitions in models/ directory
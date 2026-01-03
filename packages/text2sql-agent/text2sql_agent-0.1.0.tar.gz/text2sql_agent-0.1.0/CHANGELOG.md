# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-30

### Added
- Initial release of text2sql-agent
- LLM-agnostic SQL agent supporting any LangChain BaseChatModel
- Database-agnostic design supporting PostgreSQL, MySQL, SQLite, SQL Server, BigQuery
- Domain-specific context support for specialized behavior
- Intelligent result handling with automatic truncation for large result sets
- JSON-serializable results with support for UUIDs, dates, decimals
- Support for multiple LLM providers:
  - AWS Bedrock (Claude, Titan, etc.)
  - OpenAI (GPT-3.5, GPT-4, etc.)
  - Anthropic (Claude via API)
  - Ollama (local models)
  - Google Gemini
  - Groq
- Comprehensive test suite with 100+ tests
- Spider benchmark evaluation support
- Conversation history for follow-up questions
- ReAct agent pattern for reliable SQL generation
- Schema-first approach with automatic table discovery
- Error recovery and query correction

### Features
- `SQLAgent`: Main agent class for natural language to SQL conversion
- `JSONSerializableSQLDatabase`: Enhanced database wrapper with JSON support
- `JSONSQLDatabaseToolkit`: LangChain toolkit integration
- Configurable result truncation thresholds
- Verbose mode for debugging
- Full result retrieval for truncated queries
- Schema inspection utilities
- Table name discovery
- Dialect detection

### Documentation
- Comprehensive README with examples
- Quick start guide
- LLM provider comparison analysis
- Missing features roadmap
- Example scripts for all major LLM providers
- Spider benchmark setup and evaluation guides

### Testing
- Unit tests for core functionality
- Integration tests with real databases
- Evaluation tests for domain-specific scenarios
- Spider benchmark integration
- Support for multiple test databases (SQLite, PostgreSQL, MySQL)
- HTML test reports and comparison reports

### Examples
- AWS Bedrock integration examples
- OpenAI integration examples
- Anthropic API examples
- Ollama local model examples
- Google Gemini examples
- Groq examples with Spider benchmark
- Domain-specific examples (medical, e-commerce, employees)

## [Unreleased]

### Planned
- Support for database write operations (with safety controls)
- Enhanced caching mechanisms
- Async query execution
- Query optimization hints
- Multi-database query support
- Enhanced error messages with suggestions
- SQL query explanation feature
- Performance monitoring and metrics
- Support for more LLM providers
- Additional database dialects
- Query result visualization
- Integration with popular BI tools

### Under Consideration
- GraphQL interface
- REST API wrapper
- CLI tool for interactive queries
- Web-based query interface
- Query history and favorites
- Automated schema documentation
- Query performance profiling
- Cost optimization for cloud databases
- Multi-tenant support
- Role-based access control

---

## Version History

- **0.1.0** (2025-12-30) - Initial release

---

## Release Process

For maintainers releasing new versions:

1. Update version in `text_to_sql/__init__.py`
2. Update this CHANGELOG.md with new features, changes, and fixes
3. Commit changes: `git commit -m "Bump version to X.Y.Z"`
4. Create git tag: `git tag -a vX.Y.Z -m "Release version X.Y.Z"`
5. Push changes: `git push && git push --tags`
6. Build package: `python -m build`
7. Upload to PyPI: `python -m twine upload dist/*`
8. Create GitHub release with tag

---

## Links

- [PyPI Package](https://pypi.org/project/text2sql-agent/)
- [GitHub Repository](https://github.com/jasminpsourcefuse/text-to-sql)
- [Documentation](https://github.com/jasminpsourcefuse/text-to-sql#readme)
- [Issue Tracker](https://github.com/jasminpsourcefuse/text-to-sql/issues)

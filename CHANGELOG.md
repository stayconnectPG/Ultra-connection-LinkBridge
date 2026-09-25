# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure based on the README architecture
- Python packages: `debian` (assistant, connection, api, device) and `relay` (gateway, authentication, routing, sessions)
- Kotlin Android app module with Compose UI, connection, and device sub-modules
- pytest test suite with fixtures
- DevOps scripts: `setup_relay.sh`, `generate_certs.sh`, `setup_android.sh`, `run_tests.sh`
- Kilo configuration: `kilo.json`, `AGENTS.md`, command workflows, coding agent definition
- Documentation: `docs/` with architecture, protocol, communication, security, authentication, deployment, troubleshooting

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

#### HELP
Added, Changed, Deprecated, Removed, Fixed, Security

## [Unreleased]
- Introducing State management with strands_agents instead of langgraph
- RAG

### Changed
- Moved fast api back into container, and only keeping inference on the OS level.
- Uninstalled ollama package from dependency
- Minor performance and package updates

## [2.2.0]


### Changed
- Moved backend container to OS level for better communication between api and LLM.
- Minor improvements and bug fixes in code.
## [2.1.0] - 2025-08-01

### Changed
- Replaced Ollama with llama_cpp for more precise controls.
## [2.0.0] - 2025-07-01

### Added
- Ollama and langchain integrated AI inference system
- Based on docker container
## [1.0.0] - 2025-07-01

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

#### HELP
Added, Changed, Deprecated, Removed, Fixed, Security

## [Unreleased]
- Introducing State management with strands_agents instead of langgraph
- RAG

## [2.3.0] - 2026-01-08
### Added
- **Sovereign AI Documentation**: Added `SOVEREIGN_AI_ANALYSIS.md` detailing the project's data privacy and architecture advantages.
- **Infrastructure Roadmap**: Added `INFRASTRUCTURE_ROADMAP.md` for scaling from R&D to enterprise.
- **Search Integration**: Replaced DuckDuckGo with **Tavily** for more robust, cited web search results.
- **Event Listeners**: Added event listeners and search helpers for better frontend-backend interactivity.
- **UI Improvements**: Added favicon, new font, and improved message styling.

### Changed
- **System Prompt**: refined "Yeti" persona to be first-person, creative with lore, and smarter about when to use tools (vs. casual chat).
- **Tool Logic**: Rebranded exchange rate tool to "Smiles Wallet" and optimized search summary generation.
- **Optimization**: Tuned `llama-server` parameters for better performance on local hardware (MacBook Pro M2).

### Fixed
- **History Persistence**: Fixed issue where chat history would vanish on page refresh.
- **Docker Runner**: Rewrote `run_ai_server.sh` for better stability and slot management.


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

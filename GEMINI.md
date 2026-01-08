# Yeti – AI Agent Framework

Yeti is an agentic AI framework powered by Mistral-Nemo (OpenAI API-compatible). It is designed to perform various tasks through tool-calling and provides a robust architecture for AI-driven applications.

## Core Technologies
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React), Tailwind CSS-like styles
- **Inference**: llama_cpp (local serving)
- **Database**: PostgreSQL
- **Orchestration**: Docker & Docker Compose
- **Agent Logic**: LangChain / LangGraph

## Key Features
- **Tool Calling**: Custom functions for weather, exchange rates, web search, etc.
- **Privacy Core**: Local inference ensures data privacy.
- **Websocket Integration**: Real-time streaming between backend and frontend.
- **OpenAI Compatibility**: Easy migration and integration with existing OpenAI-based workflows.

## Project Structure
- `/app`: Backend logic, utilities, and main FastAPI entry point.
- `/frontend`: Next.js web application.
- `/scripts`: Development scripts for testing and prototyping.
- `/assets`: Brand assets and logos.

## Getting Started
1. Serve the GGUF model using `llama-server`.
2. Configure the database and environment in `.env`.
3. Run `docker compose up -d` to start the ecosystem.

For detailed instructions, refer to the [README.md](file:///Users/deepesh/Desktop/github-projects/ai-agent/README.md).

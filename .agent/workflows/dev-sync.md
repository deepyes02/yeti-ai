---
description: Sync development environment (Docker & LLM Server)
---

This workflow ensures the Yeti backend and inference server are running the latest code.

1.  **Sync Backend**: Restart the backend container to apply Python changes.
// turbo
    ```bash
    docker compose up -d backend
    ```

2.  **Verify**: Check system status.
    ```bash
    docker compose ps
    ```
"""Console entry point: starts the API server.

Exposed as the `pii-detector` command via [project.scripts] in pyproject.toml.
This is what Docker's CMD and production deploys invoke.
"""

import uvicorn

from pii_detector.core.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "pii_detector.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )


if __name__ == "__main__":
    main()

"""Parity FastAPI application."""

from fastapi import FastAPI

from parity.api.errors import install_error_handlers
from parity.api.privacy import install_privacy_middleware
from parity.api.routes.analyses import router as analyses_router
from parity.api.routes.health import router as health_router

app = FastAPI(
    title="Parity Price Waterfall API",
    version="0.1.0",
    description=(
        "Stateless decision-support API. Outputs are model estimates, not objectively correct "
        "probabilities, executable quotes, trading recommendations, or guaranteed returns."
    ),
)
install_privacy_middleware(app)
install_error_handlers(app)
app.include_router(analyses_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")

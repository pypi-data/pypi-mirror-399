from fastapi import FastAPI
import uvicorn
from fastapi import APIRouter
from loguru import logger
from urllib.parse import urlparse
from fastapi import HTTPException, Request, WebSocket, WebSocketException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from service_forge.api.routers.websocket.websocket_router import websocket_router
from service_forge.api.routers.service.service_router import service_router
from service_forge.api.routers.feedback.feedback_router import router as feedback_router
from service_forge.sft.config.sf_metadata import load_metadata
from service_forge.sft.util.name_util import get_service_url_name

def is_trusted_origin(origin_host: str, host: str, trusted_root: str = "ring.shiweinan.com") -> bool:
    """
    Check if the origin host is trusted based on domain matching.
    
    Args:
        origin_host: The hostname from the origin header
        host: The hostname from the host header
        trusted_root: The trusted root domain (can be customized)
        
    Returns:
        bool: True if the origin is trusted, False otherwise
    """
    # Convert to lowercase to avoid case sensitivity issues
    origin_host = origin_host.lower()
    host = host.lower()

    # Allow same domain, or subdomains under the same trusted root
    return (
        origin_host == host or
        origin_host.endswith("." + trusted_root) or
        host.endswith("." + trusted_root)
    )


def validate_auth_from_headers(
    headers: dict,
    origin: str | None,
    scheme: str,
    host: str,
    trusted_domain: str = "ring.shiweinan.com",
) -> tuple[str | None, str | None]:
    """
    Validate authentication from headers and return user_id and token.
    
    Args:
        headers: Dictionary of headers (can be from Request or WebSocket)
        origin: Origin header value
        scheme: URL scheme (http/https/ws/wss)
        host: Host header value
        trusted_domain: Trusted domain for origin validation
        
    Returns:
        tuple: (user_id, auth_token) - user_id can be None if not authenticated and not same origin
    """
    is_same_origin = False
    
    logger.debug(f"origin {origin}, host:{host}")
    
    if origin and host:
        try:
            parsed_origin = urlparse(origin)
            parsed_host = urlparse(f"{scheme}://{host}")
            is_same_origin = (
                parsed_origin.hostname == parsed_host.hostname
                and parsed_origin.port == parsed_host.port
                and is_trusted_origin(parsed_origin.hostname, parsed_host.hostname, trusted_domain)
            )
        except Exception:
            pass
    
    user_id = headers.get("X-User-ID")
    token = headers.get("X-User-Token")
    
    if not is_same_origin:
        # For cross-origin requests, user_id is required
        if not user_id:
            return None, None
        return user_id, token
    else:
        # For same-origin requests, user_id defaults to "0" if not provided
        return user_id if user_id else "0", token


async def authenticate_websocket(
    websocket: WebSocket,
    trusted_domain: str = "ring.shiweinan.com",
) -> None:
    """
    Authenticate WebSocket connection and set user_id and auth_token in websocket.state.
    
    Args:
        websocket: WebSocket instance
        trusted_domain: Trusted domain for origin validation
        
    Raises:
        WebSocketException: If authentication fails
    """
    origin = websocket.headers.get("origin") or websocket.headers.get("referer")
    scheme = websocket.url.scheme
    host = websocket.headers.get("host", "")
    
    user_id, token = validate_auth_from_headers(
        websocket.headers,
        origin,
        scheme,
        host,
        trusted_domain,
    )
    
    if user_id is None:
        raise WebSocketException(code=1008, reason="Unauthorized")
    
    websocket.state.user_id = user_id
    websocket.state.auth_token = token


def create_app(
    app: FastAPI | None = None,
    routers: list[APIRouter] | None = None,
    cors_origins: list[str] | None = None,
    enable_auth_middleware: bool = True,
    trusted_domain: str = "ring.shiweinan.com",
    root_path: str | None = None,
) -> FastAPI:
    """
    Create or configure a FastAPI app with common middleware and configuration.
    
    Args:
        app: Optional existing FastAPI instance. If None, creates a new one.
        routers: List of APIRouter instances to include
        cors_origins: List of allowed CORS origins. Defaults to ["*"]
        enable_auth_middleware: Whether to enable authentication middleware
        trusted_domain: Trusted domain for origin validation
        
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    if app is None:
        app = FastAPI(root_path=root_path)
    
    # Configure CORS middleware
    if cors_origins is None:
        cors_origins = ["*"]
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers if provided
    if routers:
        for router in routers:
            app.include_router(router)
    
    # Store auth configuration in app.state for WebSocket endpoints to access
    app.state.enable_auth_middleware = enable_auth_middleware
    app.state.trusted_domain = trusted_domain

    # Always include WebSocket router
    app.include_router(websocket_router)

    # Include Feedback router
    app.include_router(feedback_router)
    
    # Always include Service router
    app.include_router(service_router)
    
    # Add authentication middleware if enabled
    if enable_auth_middleware:
        @app.middleware("http")
        async def auth_middleware(request: Request, call_next):
            """
            Authentication middleware for API routes.
            
            Validates user authentication for /api routes with origin-based
            trust verification and X-User-ID header validation.
            """
            if request.url.path.startswith("/api"):
                origin = request.headers.get("origin") or request.headers.get("referer")
                scheme = request.url.scheme
                host = request.headers.get("host", "")
                
                user_id, token = validate_auth_from_headers(
                    request.headers,
                    origin,
                    scheme,
                    host,
                    trusted_domain,
                )
                
                if user_id is None:
                    raise HTTPException(status_code=401, detail="Unauthorized")
                
                request.state.user_id = user_id
                request.state.auth_token = token

            return await call_next(request)
    
    return app

async def start_fastapi_server(host: str, port: int):
    try:
        config = uvicorn.Config(
            fastapi_app,
            host=host,
            port=int(port),
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

try:
    metadata = load_metadata("sf-meta.yaml")
    fastapi_app = create_app(enable_auth_middleware=metadata.enable_auth_middleware, root_path=f"/api/v1/{get_service_url_name(metadata.name, metadata.version)}")
except Exception as e:
    logger.warning(f"Failed to load metadata, using default configuration: {e}")
    fastapi_app = create_app(enable_auth_middleware=True, root_path=None)

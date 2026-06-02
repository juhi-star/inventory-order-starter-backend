from fastapi import APIRouter, HTTPException, Request, status

from app.api.v1.deps import CurrentUser, DbSession
from app.core.limiter import limiter
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    TokenPair,
    UserResponse,
)
from app.services.auth_service import AuthenticationError, AuthService, RequestContext

router = APIRouter()


def _context_from(request: Request) -> RequestContext:
    return RequestContext(
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, payload: LoginRequest, session: DbSession) -> LoginResponse:
    service = AuthService(session)
    try:
        user, tokens = await service.login(
            email=payload.email,
            password=payload.password,
            context=_context_from(request),
        )
    except AuthenticationError as exc:
        raise _auth_http_exception(status.HTTP_401_UNAUTHORIZED, exc) from exc
    return LoginResponse(user=UserResponse.model_validate(user), tokens=tokens)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
    request: Request, payload: RefreshRequest, session: DbSession
) -> TokenPair:
    service = AuthService(session)
    try:
        _, tokens = await service.refresh(
            refresh_token=payload.refresh_token,
            context=_context_from(request),
        )
    except AuthenticationError as exc:
        raise _auth_http_exception(status.HTTP_401_UNAUTHORIZED, exc) from exc
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def logout(request: Request, current_user: CurrentUser, session: DbSession) -> None:
    service = AuthService(session)
    await service.logout(user=current_user, context=_context_from(request))


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)


def _auth_http_exception(http_status: int, exc: AuthenticationError) -> HTTPException:
    return HTTPException(
        status_code=http_status,
        detail={"code": exc.code, "message": exc.message},
    )

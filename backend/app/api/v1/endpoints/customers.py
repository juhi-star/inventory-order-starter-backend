from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.v1.deps import CurrentUser, DbSession
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter()


@router.get("", response_model=list[CustomerResponse])
async def list_customers(
    session: DbSession,
    current_user: CurrentUser,
    search: str = Query("", max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[CustomerResponse]:
    repo = CustomerRepository(session)
    customers = await repo.list_all(search=search, skip=skip, limit=limit)
    return [CustomerResponse.model_validate(c) for c in customers]


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> CustomerResponse:
    repo = CustomerRepository(session)
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"code": "duplicate_email", "message": "Email already exists"},
        )
    customer = await repo.create(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
    )
    await session.commit()
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    session: DbSession,
    current_user: CurrentUser,
) -> CustomerResponse:
    repo = CustomerRepository(session)
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerResponse.model_validate(customer)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> CustomerResponse:
    repo = CustomerRepository(session)
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    if payload.email is not None:
        existing = await repo.get_by_email(payload.email)
        if existing and existing.id != customer_id:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail={"code": "duplicate_email", "message": "Email already exists"},
            )
    updated = await repo.update(
        customer,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
    )
    await session.commit()
    return CustomerResponse.model_validate(updated)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_customer(
    customer_id: str,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    repo = CustomerRepository(session)
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
    await repo.delete(customer)
    await session.commit()

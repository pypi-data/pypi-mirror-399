"""FastAPI routes using DI to inject services."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from fastapi_di_kit import Inject
from ..domain.services import UserService


router = APIRouter()


class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    name: str
    email: str


class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    name: str
    email: str


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(Inject[UserService])
):
    """Create a new user."""
    user = user_service.create_user(name=request.name, email=request.email)
    return UserResponse(id=user.id, name=user.name, email=user.email)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    user_service: UserService = Depends(Inject[UserService])
):
    """Get a user by ID."""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, name=user.name, email=user.email)


@router.get("/users", response_model=list[UserResponse])
def list_users(user_service: UserService = Depends(Inject[UserService])):
    """List all users."""
    users = user_service.list_users()
    return [UserResponse(id=u.id, name=u.name, email=u.email) for u in users]

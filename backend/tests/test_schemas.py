from schemas import UserCreate, LoginRequest


def test_user_create_valid():
    user = UserCreate(nom="Ali", email="ali@test.com", password="secret", role="student")
    assert user.nom == "Ali"
    assert user.email == "ali@test.com"
    assert user.role == "student"


def test_login_request_valid():
    login = LoginRequest(email="ali@test.com", password="secret")
    assert login.email == "ali@test.com"


def test_user_create_requires_email():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        UserCreate(nom="Ali", password="secret", role="student")

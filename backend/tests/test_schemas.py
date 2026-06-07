from schemas import UserCreate, LoginRequest, TokenResponse


def test_user_create_valid():
    user = UserCreate(nom="Ali", email="ali@test.com", password="secret", role="student")
    assert user.nom == "Ali"
    assert user.email == "ali@test.com"
    assert user.role == "student"


def test_login_request_valid():
    login = LoginRequest(email="ali@test.com", password="secret")
    assert login.email == "ali@test.com"


def test_token_response_valid():
    token = TokenResponse(access_token="abc123", token_type="bearer")
    assert token.access_token == "abc123"
    assert token.token_type == "bearer"

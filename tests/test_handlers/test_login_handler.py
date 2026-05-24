from uuid import uuid4

from db.models import PortalRole
from hashing import Hasher
from tests.conftest import create_test_auth_headers_for_user


async def test_inactive_user_cannot_login(client, create_user_in_database):
    password = "password"
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": False,
        "hashed_password": Hasher.get_password_hash(password),
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)

    resp = client.post(
        "/login/token",
        data={"username": user_data["email"], "password": password},
    )

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Incorrect email or password"}


async def test_inactive_user_token_is_rejected(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": False,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)

    resp = client.get(
        f"/user/?user_id={user_data['user_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}

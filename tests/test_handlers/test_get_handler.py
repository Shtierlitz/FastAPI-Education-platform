from uuid import uuid4

from db.models import PortalRole
from tests.conftest import create_test_auth_headers_for_user


async def test_get_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)
    resp = client.get(
        f"/user/?user_id={user_data['user_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    user_from_response = resp.json()
    assert user_from_response["user_id"] == str(user_data["user_id"])
    assert user_from_response["name"] == str(user_data["name"])
    assert user_from_response["surname"] == str(user_data["surname"])
    assert user_from_response["email"] == str(user_data["email"])
    assert user_from_response["is_active"] == user_data["is_active"]


async def test_get_another_user_forbidden(
    client, create_user_in_database, get_user_from_database
):
    target_user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    current_user_data = {
        "user_id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**target_user_data)
    await create_user_in_database(**current_user_data)

    resp = client.get(
        f"/user/?user_id={target_user_data['user_id']}",
        headers=create_test_auth_headers_for_user(current_user_data["email"]),
    )

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Forbidden."}


async def test_get_another_user_by_admin(
    client, create_user_in_database, get_user_from_database
):
    target_user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    admin_user_data = {
        "user_id": uuid4(),
        "name": "Admin",
        "surname": "Adminov",
        "email": "admin@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_ADMIN],
    }
    await create_user_in_database(**target_user_data)
    await create_user_in_database(**admin_user_data)

    resp = client.get(
        f"/user/?user_id={target_user_data['user_id']}",
        headers=create_test_auth_headers_for_user(admin_user_data["email"]),
    )

    assert resp.status_code == 200
    user_from_response = resp.json()
    assert user_from_response["user_id"] == str(target_user_data["user_id"])
    assert user_from_response["name"] == str(target_user_data["name"])
    assert user_from_response["surname"] == str(target_user_data["surname"])
    assert user_from_response["email"] == str(target_user_data["email"])
    assert user_from_response["is_active"] == target_user_data["is_active"]


async def test_get_user_id_validation_error(
    client,
    create_user_in_database,
    get_user_from_database,
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**user_data)
    resp = client.get(
        "/user/?user_id=123",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 422
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": [
            {
                "type": "uuid_parsing",
                "loc": ["query", "user_id"],
                "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 3",
                "input": "123",
                "ctx": {
                    "error": "invalid length: expected length 32 for simple format, found 3"
                },
            }
        ]
    }


async def test_get_user_not_found(
    client,
    create_user_in_database,
    get_user_from_database,
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_id_for_finding = uuid4()
    await create_user_in_database(**user_data)
    resp = client.get(
        f"/user/?user_id={user_id_for_finding}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 404
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": f"User with id {user_id_for_finding} not found."
    }


async def test_get_user_not_auth(
    client,
    create_user_in_database,
    get_user_from_database,
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    bad_auth_headers = create_test_auth_headers_for_user(user_data["email"])
    bad_auth_headers["Authorization"] += "a"
    user_id_for_finding = uuid4()
    await create_user_in_database(**user_data)
    resp = client.get(f"/user/?user_id={user_id_for_finding}", headers=bad_auth_headers)
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}


async def test_get_user_no_jwt(
    client,
    create_user_in_database,
    get_user_from_database,
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_id_for_finding = uuid4()
    await create_user_in_database(**user_data)
    resp = client.get(
        f"/user/?user_id={user_id_for_finding}",
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}

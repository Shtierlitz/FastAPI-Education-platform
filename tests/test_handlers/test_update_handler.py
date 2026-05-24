from uuid import uuid4

import pytest

from db.models import PortalRole
from tests.conftest import create_test_auth_headers_for_user


async def test_update_user_updates_only_requested_user(
    client, create_user_in_database, get_user_from_database
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "nikolai@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    other_user_data = {
        "user_id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    update_data = {
        "name": "Petr",
        "surname": "Petrov",
        "email": "petr@example.com",
    }
    await create_user_in_database(**user_data)
    await create_user_in_database(**other_user_data)

    resp = client.patch(
        f"/user/?user_id={user_data['user_id']}",
        json=update_data,
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )

    assert resp.status_code == 200
    assert resp.json() == {"updated_user_id": str(user_data["user_id"])}
    updated_users_from_db = await get_user_from_database(user_data["user_id"])
    updated_user_from_db = dict(updated_users_from_db[0])
    assert updated_user_from_db["name"] == update_data["name"]
    assert updated_user_from_db["surname"] == update_data["surname"]
    assert updated_user_from_db["email"] == update_data["email"]
    other_users_from_db = await get_user_from_database(other_user_data["user_id"])
    other_user_from_db = dict(other_users_from_db[0])
    assert other_user_from_db["name"] == other_user_data["name"]
    assert other_user_from_db["surname"] == other_user_data["surname"]
    assert other_user_from_db["email"] == other_user_data["email"]


async def test_update_user_check_one_is_updated(
    client, create_user_in_database, get_user_from_database
):
    user_data_1 = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "nikolai@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_data_2 = {
        "user_id": uuid4(),
        "name": "John",
        "surname": "Smith",
        "email": "johns@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_data_3 = {
        "user_id": uuid4(),
        "name": "Jane",
        "surname": "Smith",
        "email": "janes@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_data_updated = {
        "name": "James",
        "surname": "Logan",
        "email": "cheburek@kek.com",
    }
    for user_data in [user_data_1, user_data_2, user_data_3]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data_1['user_id']}",
        json=user_data_updated,
        headers=create_test_auth_headers_for_user(user_data_1["email"]),
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["updated_user_id"] == str(user_data_1["user_id"])
    users_from_db = await get_user_from_database(user_data_1["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] == user_data_1["is_active"]
    assert user_from_db["user_id"] == user_data_1["user_id"]

    # check other users that data has not been changed
    users_from_db = await get_user_from_database(user_data_2["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_2["name"]
    assert user_from_db["surname"] == user_data_2["surname"]
    assert user_from_db["email"] == user_data_2["email"]
    assert user_from_db["is_active"] == user_data_2["is_active"]
    assert user_from_db["user_id"] == user_data_2["user_id"]

    users_from_db = await get_user_from_database(user_data_3["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_3["name"]
    assert user_from_db["surname"] == user_data_3["surname"]
    assert user_from_db["email"] == user_data_3["email"]
    assert user_from_db["is_active"] == user_data_3["is_active"]
    assert user_from_db["user_id"] == user_data_3["user_id"]


async def test_update_another_user_forbidden(
    client, create_user_in_database, get_user_from_database
):
    target_user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "nikolai@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    current_user_data = {
        "user_id": uuid4(),
        "name": "Jane",
        "surname": "Smith",
        "email": "janes@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    update_data = {
        "name": "James",
        "surname": "Logan",
        "email": "cheburek@kek.com",
    }
    await create_user_in_database(**target_user_data)
    await create_user_in_database(**current_user_data)

    resp = client.patch(
        f"/user/?user_id={target_user_data['user_id']}",
        json=update_data,
        headers=create_test_auth_headers_for_user(current_user_data["email"]),
    )

    assert resp.status_code == 403
    assert resp.json() == {"detail": "Forbidden."}
    users_from_db = await get_user_from_database(target_user_data["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == target_user_data["name"]
    assert user_from_db["surname"] == target_user_data["surname"]
    assert user_from_db["email"] == target_user_data["email"]


async def test_update_another_user_by_admin(
    client, create_user_in_database, get_user_from_database
):
    target_user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "nikolai@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    admin_user_data = {
        "user_id": uuid4(),
        "name": "Admin",
        "surname": "Adminov",
        "email": "admin@example.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_ADMIN],
    }
    update_data = {
        "name": "James",
        "surname": "Logan",
        "email": "cheburek@kek.com",
    }
    await create_user_in_database(**target_user_data)
    await create_user_in_database(**admin_user_data)

    resp = client.patch(
        f"/user/?user_id={target_user_data['user_id']}",
        json=update_data,
        headers=create_test_auth_headers_for_user(admin_user_data["email"]),
    )

    assert resp.status_code == 200
    assert resp.json() == {"updated_user_id": str(target_user_data["user_id"])}
    users_from_db = await get_user_from_database(target_user_data["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == update_data["name"]
    assert user_from_db["surname"] == update_data["surname"]
    assert user_from_db["email"] == update_data["email"]


async def test_update_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_data_updated = {
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "cheburek@kek.com",
    }
    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data['user_id']}",
        json=user_data_updated,
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data == {"updated_user_id": str(user_data["user_id"])}
    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] == user_data["is_active"]
    assert user_from_db["user_id"] == user_data["user_id"]


@pytest.mark.parametrize(
    "user_data_updated, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": "At least one parameter for user update info should be provided"
            },
        ),
        ({"name": "Nikolai123"}, 422, {"detail": "Name should contains only letters"}),
        (
            {"email": "not_an_email"},
            422,
            {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: An email address must have an @-sign.",
                        "input": "not_an_email",
                        "ctx": {"reason": "An email address must have an @-sign."},
                    }
                ]
            },
        ),
        (
            {"surname": ""},
            422,
            {
                "detail": [
                    {
                        "type": "string_too_short",
                        "loc": ["body", "surname"],
                        "msg": "String should have at least 1 character",
                        "input": "",
                        "ctx": {"min_length": 1},
                    }
                ]
            },
        ),
        (
            {"name": ""},
            422,
            {
                "detail": [
                    {
                        "type": "string_too_short",
                        "loc": ["body", "name"],
                        "msg": "String should have at least 1 character",
                        "input": "",
                        "ctx": {"min_length": 1},
                    }
                ]
            },
        ),
        (
            {"surname": "Sviridov123"},
            422,
            {"detail": "Surname should contains only letters"},
        ),
        (
            {"email": "123"},
            422,
            {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: An email address must have an @-sign.",
                        "input": "123",
                        "ctx": {"reason": "An email address must have an @-sign."},
                    }
                ]
            },
        ),
    ],
)
async def test_update_user_validation_error(
    client,
    create_user_in_database,
    get_user_from_database,
    user_data_updated,
    expected_status_code,
    expected_detail,
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
    resp = client.patch(
        f"/user/?user_id={user_data['user_id']}",
        json=user_data_updated,
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == expected_status_code
    resp_data = resp.json()
    assert resp_data == expected_detail


async def test_update_user_id_validation_error(
    client,
    create_user_in_database,
    get_user_from_database,
):
    auth_user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**auth_user_data)

    update_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
    }
    resp = client.patch(
        "/user/?user_id=123",
        json=update_data,
        headers=create_test_auth_headers_for_user(update_data["email"]),
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


async def test_update_user_not_found_error(
    client,
    create_user_in_database,
    get_user_from_database,
):
    auth_user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**auth_user_data)

    update_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
    }
    user_id = uuid4()
    resp = client.patch(
        f"/user/?user_id={user_id}",
        json=update_data,
        headers=create_test_auth_headers_for_user(update_data["email"]),
    )
    assert resp.status_code == 404
    data_from_response = resp.json()
    assert data_from_response == {"detail": f"User with id {user_id} not found."}


async def test_update_user_duplication_email_error(
    client, create_user_in_database, get_user_from_database
):
    user_data_1 = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_data_2 = {
        "user_id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_data_updated = {"email": user_data_2["email"]}
    for user_data in [user_data_1, user_data_2]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data_1['user_id']}",
        json=user_data_updated,
        headers=create_test_auth_headers_for_user(user_data_1["email"]),
    )
    assert resp.status_code == 409
    assert resp.json() == {"detail": "Email already exists."}


async def test_update_user_not_auth(
    client,
    create_user_in_database,
    get_user_from_database,
):
    auth_user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**auth_user_data)

    update_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
    }
    bad_auth_headers = create_test_auth_headers_for_user(update_data["email"])
    bad_auth_headers["Authorization"] += "a"
    user_id = uuid4()
    resp = client.patch(
        f"/user/?user_id={user_id}", json=update_data, headers=bad_auth_headers
    )
    assert resp.status_code == 401
    data_from_response = resp.json()
    assert data_from_response == {"detail": "Could not validate credentials"}


async def test_update_user_no_jwt(
    client,
    create_user_in_database,
    get_user_from_database,
):
    auth_user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "hashed_password",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    await create_user_in_database(**auth_user_data)

    update_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
    }
    user_id = uuid4()
    resp = client.patch(
        f"/user/?user_id={user_id}",
        json=update_data,
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}

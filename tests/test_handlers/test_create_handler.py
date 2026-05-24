import pytest


async def test_create_user(client, get_user_from_database):
    user_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "password": "strong_password",
    }
    resp = client.post("/user/", json=user_data)
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]


async def test_create_user_duplicate_email_error(client, get_user_from_database):
    user_data = {
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "password": "strong_password",
    }
    user_data_same_email = {
        "name": "James",
        "surname": "Logan",
        "email": "lol@kek.com",
        "password": "strong_password",
    }
    resp = client.post("/user/", json=user_data)
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    user_from_db = await get_user_from_database((data_from_resp["user_id"]))
    assert len(user_from_db) == 1
    user_from_db = dict(user_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]
    resp = client.post("/user/", json=user_data_same_email)
    assert resp.status_code == 409
    assert resp.json() == {"detail": "Email already exists."}


@pytest.mark.parametrize(
    "user_data_for_creation, " "expected_status_code," "expected_detail",
    [
        (
            {},
            422,
            {
                "detail": [
                    {
                        "type": "missing",
                        "loc": ["body", "name"],
                        "msg": "Field required",
                        "input": {},
                    },
                    {
                        "type": "missing",
                        "loc": ["body", "surname"],
                        "msg": "Field required",
                        "input": {},
                    },
                    {
                        "type": "missing",
                        "loc": ["body", "email"],
                        "msg": "Field required",
                        "input": {},
                    },
                    {
                        "type": "missing",
                        "loc": ["body", "password"],
                        "msg": "Field required",
                        "input": {},
                    },
                ]
            },
        ),
        (
            {
                "name": "Nikolai123",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "password": "strong_password",
            },
            422,
            {"detail": "Name should contains only letters"},
        ),
        (
            {
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol",
                "password": "strong_password",
            },
            422,
            {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address: An email address must have an @-sign.",
                        "input": "lol",
                        "ctx": {"reason": "An email address must have an @-sign."},
                    }
                ]
            },
        ),
        (
            {
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "password": "short",
            },
            422,
            {
                "detail": [
                    {
                        "type": "string_too_short",
                        "loc": ["body", "password"],
                        "msg": "String should have at least 8 characters",
                        "input": "short",
                        "ctx": {"min_length": 8},
                    }
                ]
            },
        ),
    ],
)
async def test_create_user_validation_error(
    client, user_data_for_creation, expected_status_code, expected_detail
):
    resp = client.post("/user/", json=user_data_for_creation)
    data_from_resp = resp.json()
    assert resp.status_code == expected_status_code
    assert data_from_resp == expected_detail

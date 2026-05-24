import conftest
import pytest


@pytest.mark.asyncio
async def test_get_test_db_closes_session_and_disposes_engine(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.closed = False

        async def close(self):
            self.closed = True

    class FakeEngine:
        def __init__(self):
            self.disposed = False

        async def dispose(self):
            self.disposed = True

    fake_session = FakeSession()
    fake_engine = FakeEngine()

    monkeypatch.setattr(
        conftest, "create_async_engine", lambda *args, **kwargs: fake_engine
    )
    monkeypatch.setattr(
        conftest,
        "sessionmaker",
        lambda *args, **kwargs: lambda: fake_session,
    )

    db_generator = conftest._get_test_db()
    yielded_session = await anext(db_generator)
    await db_generator.aclose()

    assert yielded_session is fake_session
    assert fake_session.closed is True
    assert fake_engine.disposed is True

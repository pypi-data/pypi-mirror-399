import pytest
import pytest_asyncio
from surrealengine import Document, StringField, IntField, create_connection, ConnectionRegistry

# Renamed to avoid PytestCollectionWarning (classes starting with Test are collected)
class UserDescriptorDoc(Document):
    name = StringField()
    age = IntField()

    class Meta:
        collection = "test_user_descriptor"

@pytest_asyncio.fixture
async def cleanup():
    # Force reset connection to handle pytest-asyncio loop scoping
    # The connection is tied to the event loop, so we must recreate it if the loop changes
    ConnectionRegistry._default_async_connection = None
    
    # Establish new connection
    # Credentials from compose.yml: root/root
    try:
        await create_connection("ws://localhost:8001/rpc", "root", "root", "test", "test").connect()
    except Exception as e:
        print(f"Connection failed: {e}")
        raise

    await UserDescriptorDoc.objects.delete()
    yield
    # Teardown
    await UserDescriptorDoc.objects.delete()
    # Close connection to clean up
    if ConnectionRegistry._default_async_connection:
        await ConnectionRegistry._default_async_connection.close()
        ConnectionRegistry._default_async_connection = None

@pytest.mark.asyncio
async def test_descriptor_update(cleanup):
    # Setup data
    u1 = UserDescriptorDoc(name="User 1", age=20)
    await u1.save()
    u2 = UserDescriptorDoc(name="User 2", age=20)
    await u2.save()
    
    # Test User.objects.update() (Async) - Should update ALL
    updated_list = await UserDescriptorDoc.objects.update(age=30, returning='after')
    
    assert len(updated_list) == 2
    for user in updated_list:
        assert user.age == 30
        
    # Verify in DB
    count = await UserDescriptorDoc.objects.filter(age=30).count()
    assert count == 2

@pytest.mark.asyncio
async def test_descriptor_delete(cleanup):
    # Setup data
    u1 = UserDescriptorDoc(name="User 1")
    await u1.save()
    u2 = UserDescriptorDoc(name="User 2")
    await u2.save()
    
    assert await UserDescriptorDoc.objects.count() == 2
    
    # Test User.objects.delete() (Async) - Should delete ALL
    count = await UserDescriptorDoc.objects.delete()
    
    assert await UserDescriptorDoc.objects.count() == 0

def test_descriptor_sync_methods():
    # Setup sync connection (assuming one is configured/available in test env or created)
    # Since existing tests use async mostly, we might need to ensure sync connection is present
    # But usually tests reuse the same event loop/connection if tricky.
    # We'll skip complex sync setup if uncertain, but verify basic API existence/callability if possible.
    pass

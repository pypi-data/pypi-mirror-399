import pytest
from atomsql import Database, Model, StringField
from atomsql.fields import ForeignKey

# --- Define Models for Testing ---
# We define these at the module level so they are available to all tests.


class User(Model):
    name = StringField()


class Post(Model):
    title = StringField()
    # Link Post to User
    author = ForeignKey(to=User)


# --- Fixtures ---


@pytest.fixture
def db():
    """
    Creates a fresh in-memory database for each test.
    Handles binding the DB to models and cleaning up afterwards.
    """
    database = Database("sqlite:///:memory:")

    # Bind the database to the Models (Required for AtomSQL lazy loading)
    User.db = database
    Post.db = database

    # Create the tables
    database.create_all()

    yield database

    # Teardown: Close connection and unbind to prevent side effects
    database.close()
    User.db = None
    Post.db = None


# --- Tests ---


def test_relationship_creation_and_lazy_load(db):
    """
    Test the standard flow: Create Parent -> Create Child -> Save -> Fetch -> Access Relation.
    """
    # 1. Create and Save Parent (User)
    alice = User(name="Alice")
    alice.save(db)
    assert alice.id is not None

    # 2. Create and Save Child (Post) linked to Parent
    post = Post(title="My First Post", author=alice)
    post.save(db)
    assert post.id is not None

    # Verify the ID was stored correctly in the instance attribute (author_id)
    assert post.author_id == alice.id

    # 3. Test Lazy Loading
    # Fetch a fresh instance from the DB
    fetched_post = Post.get(post.id)
    assert fetched_post is not None
    assert fetched_post.title == "My First Post"

    # Accessing the .author property should trigger the SQL select
    # and return a User object
    assert fetched_post.author is not None
    assert isinstance(fetched_post.author, User)
    assert fetched_post.author.name == "Alice"
    assert fetched_post.author.id == alice.id


def test_relationship_assignment_by_id(db):
    """
    Test that we can assign a Foreign Key using the integer ID directly.
    """
    bob = User(name="Bob")
    bob.save(db)

    # Assign using ID (int) instead of the object instance
    post = Post(title="Manual ID Assignment", author=bob.id)
    post.save(db)

    # Verify it resolved correctly
    fetched_post = Post.get(post.id)
    assert fetched_post.author.name == "Bob"


def test_relationship_validation(db):
    """
    Test that the ForeignKey field raises errors for invalid types.
    """
    with pytest.raises(ValueError) as excinfo:
        # Try to assign a string instead of a User object or int ID
        Post(title="Invalid", author="Not A User Object")

    assert "Expected User instance or int ID" in str(excinfo.value)


def test_relationship_update(db):
    """
    Test updating a Foreign Key relationship to a different parent.
    """
    alice = User(name="Alice")
    alice.save(db)

    bob = User(name="Bob")
    bob.save(db)

    # Originally authored by Alice
    post = Post(title="Shared Post", author=alice)
    post.save(db)
    assert post.author.name == "Alice"

    # Change author to Bob
    post.author = bob
    # Note: If your ORM supports update(), this would be post.save() or post.update()
    # For now, we manually simulate the save flow or assume save() handles updates (upsert)
    # If save() is INSERT-only currently, this test might need adjustment based on Phase 4 features.
    # Assuming basic Python object update works in memory:
    assert post.author_id == bob.id
    assert post.author.name == "Bob"

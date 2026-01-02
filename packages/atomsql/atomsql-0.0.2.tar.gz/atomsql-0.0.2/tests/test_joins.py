import pytest
from atomsql import Database, Model, StringField
from atomsql.fields import ForeignKey


class User(Model):
    name = StringField()


class Post(Model):
    title = StringField()
    author = ForeignKey(to=User, nullable=True)


@pytest.fixture
def db():
    database = Database("sqlite:///:memory:")
    User.db = database
    Post.db = database
    database.create_all()
    yield database
    database.close()


def test_select_related_eager_load(db):
    """Test that select_related fetches data in a single query."""
    # 1. Setup Data
    u = User(name="Speedy")
    u.save()

    Post(title="Fast Query", author=u).save()

    # 2. Fetch using JOIN
    # This should trigger ONE SELECT with a JOIN
    qs = Post.filter(title="Fast Query").select_related("author")
    posts = list(qs)

    assert len(posts) == 1
    post = posts[0]

    # 3. Verify Data
    assert post.title == "Fast Query"

    # 4. Verify Eager Loading via public API
    assert post.author is not None
    assert post.author.name == "Speedy"
    assert post.author.id == u.id
def test_select_related_null_relation(db):
    """Test behavior when the foreign key is NULL (LEFT JOIN)."""
    # Create post with NO author (assuming FK is nullable for this test)
    # Note: You might need required=False on ForeignKey definition
    Post(title="Orphan Post", author=None).save()

    qs = Post.filter(title="Orphan Post").select_related("author")
    post = list(qs)[0]

    assert post.title == "Orphan Post"
    # Accessing author should be None (and safely cached as None)
    assert post.author is None

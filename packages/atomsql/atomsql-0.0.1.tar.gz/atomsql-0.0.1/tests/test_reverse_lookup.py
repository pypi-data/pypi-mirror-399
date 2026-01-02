import pytest
from atomsql import Database, Model, StringField
from atomsql.fields import ForeignKey


class User(Model):
    name = StringField()


class Post(Model):
    title = StringField()
    # related_name="posts" will allow us to access user.posts
    author = ForeignKey(to=User, related_name="posts")


class Comment(Model):
    content = StringField()
    # Default behavior: will create user.comment_set
    user = ForeignKey(to=User)


@pytest.fixture
def db():
    database = Database("sqlite:///:memory:")
    User.db = database
    Post.db = database
    Comment.db = database
    database.create_all()
    yield database
    database.close()


def test_reverse_lookup_custom_name(db):
    """Test reverse lookup using 'related_name'"""
    alice = User(name="Alice")
    alice.save()

    p1 = Post(title="Post 1", author=alice)
    p1.save()
    p2 = Post(title="Post 2", author=alice)
    p2.save()

    # Access via related_name
    user_posts = alice.posts
    assert len(user_posts) == 2
    assert user_posts[0].title == "Post 1"
    assert user_posts[1].title == "Post 2"


def test_reverse_lookup_default_name(db):
    """Test reverse lookup using default '{table}_set' naming"""
    bob = User(name="Bob")
    bob.save()

    c1 = Comment(content="Nice!", user=bob)
    c1.save()

    # Access via default name
    assert hasattr(bob, "comment_set")
    user_comments = bob.comment_set
    assert len(user_comments) == 1
    assert user_comments[0].content == "Nice!"


def test_reverse_lookup_empty(db):
    """Test reverse lookup returns empty list if no children exist"""
    charlie = User(name="Charlie")
    charlie.save()
    assert charlie.posts == []

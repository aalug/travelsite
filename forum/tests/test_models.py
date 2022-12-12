"""Tests for models of the forum app."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from mptt.exceptions import InvalidMove

from forum.models import Author, PostCategory, Post, Reply, Comment


class SetUpTestCase(TestCase):
    """Class for creating a user, an author and a post for further testing."""

    def setUp(self):
        # Create a user
        self.user = get_user_model().objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpassword',
            is_active=True
        )

        # Create an author
        self.author = Author.objects.create(
            user=self.user,
            slug='test-author',
            points=5
        )

        # Create a post
        self.post = Post.objects.create(
            title='Test title',
            slug='test-title',
            author=self.author,
            content='Test content.',
            is_approved=True
        )


class AuthorTest(SetUpTestCase):
    """Test Author model. It extends SetUpTestCase class
        that creates a user, an author and a post."""

    def setUp(self):
        super(AuthorTest, self).setUp()

    def test_user_field(self):
        """Test that the user field is set correctly."""
        self.assertEqual(self.author.user, self.user)

    def test_deleting_user(self):
        """Test on_delete property of the user field."""
        pk = self.author.pk
        self.user.delete()
        self.assertFalse(Author.objects.filter(pk=pk).exists())

    def test_slug_field(self):
        """Test that the slug field is set correctly."""
        self.assertEqual(self.author.slug, 'test-author')

    def test_creating_slug(self):
        """Test that the slug will be created after save()
           if it was not passed while creating."""
        second_user = get_user_model().objects.create_user(
            username='second_user',
            email='second_user@example.com',
            password='testpassword',
        )
        second_author = Author.objects.create(
            user=second_user,
        )
        second_author.save()
        self.assertEqual(slugify(second_author), second_author.slug)

    def test_points_field(self):
        """Test that the points field is set correctly."""
        self.assertEqual(self.author.points, 5)

    def test_num_posts_method(self):
        """Test that num_posts method works correctly."""
        self.assertEqual(self.author.num_posts, 1)


class PostCategoryTest(SetUpTestCase):
    """Test PostCategory model. It extends SetUpTestCase class
       that creates a user, an author and a post."""

    def setUp(self):
        super(PostCategoryTest, self).setUp()
        # Create a parent category
        self.parent_category = PostCategory.objects.create(
            name='Parent Category',
            slug='parent-category',
            is_active=True
        )

        # Create a child category
        self.child_category = PostCategory.objects.create(
            name='Child Category',
            slug='child-category',
            is_active=True,
            parent=self.parent_category
        )
        self.post.categories.add(self.parent_category)
        self.post.categories.add(self.child_category)

    def test_name_field(self):
        """Test that the name field is set correctly."""
        self.assertEqual(self.parent_category.name, 'Parent Category')
        self.assertEqual(self.child_category.name, 'Child Category')

    def test_slug_field(self):
        """Test that the slug field is set correctly."""
        self.assertEqual(self.parent_category.slug, 'parent-category')
        self.assertEqual(self.child_category.slug, 'child-category')

    def test_creating_slug(self):
        """Test that the slug will be created after save()
           if it was not passed while creating."""
        category = PostCategory.objects.create(
            name='Test Category',
        )
        category.save()
        self.assertEqual(slugify(category), category.slug)

    def test_is_active_field(self):
        """Test that the is_active field is set correctly."""
        self.assertTrue(self.parent_category.is_active)
        self.assertTrue(self.child_category.is_active)

    def test_parent_field(self):
        """Test that the parent field is set correctly."""
        self.assertEqual(self.parent_category.parent, None)
        self.assertEqual(self.child_category.parent, self.parent_category)

    def test_move_category(self):
        """Test moving a category to a new parent."""
        self.child_category.move_to(self.parent_category)
        self.assertEqual(self.child_category.parent, self.parent_category)

    def test_invalid_move(self):
        """Test that trying to move a category to itself or one of its own descendants
           raises an InvalidMove exception"""
        with self.assertRaises(InvalidMove):
            self.child_category.move_to(self.child_category)

        with self.assertRaises(InvalidMove):
            self.parent_category.move_to(self.child_category)

    def test_num_posts_method(self):
        """Test that the num_posts method works correctly."""
        self.assertEqual(self.parent_category.num_posts, 1)
        self.assertEqual(self.child_category.num_posts, 1)

    def test_last_post_method(self):
        """Test that last_posts method works correctly."""
        self.assertEqual(self.parent_category.last_post, self.post)
        self.assertEqual(self.child_category.last_post, self.post)


class ReplyTest(SetUpTestCase):
    """Test Reply model. It extends SetUpTestCase class
       that creates a user, an author and a post."""

    def setUp(self):
        super(ReplyTest, self).setUp()
        # Create a reply
        self.reply = Reply.objects.create(
            author=self.author,
            content='Test reply content.'
        )

    def test_author_field(self):
        """Test that the author field is set correctly."""
        self.assertEqual(self.author, self.author)

    def test_content_field(self):
        """Test that the content field is set correctly."""
        self.assertEqual(self.reply.content, 'Test reply content.')


class CommentTest(SetUpTestCase):
    """Test Comment model. It extends SetUpTestCase class
       that creates a user, an author and a post."""

    def setUp(self):
        super(CommentTest, self).setUp()
        # Create a comment
        self.comment = Comment.objects.create(
            author=self.author,
            content='Test comment content.'
        )

        # Create a reply to self.comment
        self.reply = Reply.objects.create(
            author=self.author,
            content='Reply to a comment.'
        )
        self.comment.replies.add(self.reply)

    def test_author_field(self):
        """Test that the author field is set correctly."""
        self.assertEqual(self.author, self.author)

    def test_content_field(self):
        """Test that the content field is set correctly."""
        self.assertEqual(self.comment.content, 'Test comment content.')

    def test_replies_field(self):
        """Test that the replies field is set correctly."""
        self.assertIn(self.reply, self.comment.replies.all())


class PostTest(SetUpTestCase):
    """Test Post model. It extends SetUpTestCase class
       that creates a user, an author and a post."""

    def setUp(self):
        super(PostTest, self).setUp()
        # Create a PostCategory
        self.post_category = PostCategory.objects.create(
            name='Post Category',
            slug='post-category',
            is_active=True
        )
        self.post.categories.add(self.post_category)

        # Create a comment
        self.comment = Comment.objects.create(
            author=self.author,
            content='Test comment.'
        )
        self.post.comments.add(self.comment)

    def test_title_field(self):
        """Test that the title field is set correctly."""
        self.assertEqual(self.post.title, 'Test title')

    def test_slug_field(self):
        """Test that the slug field is set correctly."""
        self.assertEqual(self.post.slug, 'test-title')

    def test_creating_slug(self):
        """Test that the slug will be created after save()
           if it was not passed while creating."""
        test_post = Post.objects.create(
            title='Test Slug',
            author=self.author,
            content='Test content.',
        )
        test_post.save()
        self.assertEqual(slugify(test_post), test_post.slug)

    def test_author_field(self):
        """Test that the author field is set correctly."""
        self.assertEqual(self.post.author, self.author)

    def test_content_field(self):
        """Test that the content field is set correctly."""
        self.assertEqual(self.post.content, 'Test content.')
        self.assertHTMLEqual(self.post.content, 'Test content.')

    def test_categories_field(self):
        """Test that the categories field is set correctly."""
        self.assertIn(self.post_category, self.post.categories.all())

    def test_is_approved_field(self):
        """Test that the is_approved field is set correctly."""
        self.assertTrue(self.post.is_approved)

    def test_comments_field(self):
        """Test that the is_approved field is set correctly."""
        self.assertIn(self.comment, self.post.comments.all())

    def test_closed_field(self):
        """Test that the is_approved field is set correctly."""
        self.assertFalse(self.post.closed)

    def test_num_comments_method(self):
        """Test that the num_comments method works correctly."""
        self.assertEqual(self.post.num_comments, 1)
        comment = Comment.objects.create(
            author=self.author,
            content='Second comment.'
        )
        self.post.comments.add(comment)
        self.assertEqual(self.post.num_comments, 2)

"""
Tests for orb.tags.managers.
"""

from django.contrib.auth.models import User
from django.test import TestCase

from orb.models import Tag, Resource, ResourceTag
from orb.resources.tests.factory import resource_factory
from orb.tags.tests.factory import tag_factory


class ActiveManagerTests(TestCase):
    """
    Tests for the active manager class.

    The active manager only returns tags with associated resources
    """

    @classmethod
    def setUpClass(cls):
        user = User.objects.create(username="McTester")
        resource = resource_factory(user=user)
        second_resource= resource_factory(user=user)
        used_tag = tag_factory(user=user)
        unused_tag = tag_factory(user=user)  # noqa
        ResourceTag.objects.create(create_user=user, tag=used_tag, resource=resource)
        ResourceTag.objects.create(create_user=user, tag=used_tag, resource=second_resource)

    @classmethod
    def tearDownClass(cls):
        ResourceTag.objects.all().delete()
        Resource.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.all().delete()

    def test_default_manager(self):
        self.assertEqual(Tag.objects.all().count(), 2)

    def test_active_manager(self):
        self.assertEqual(Tag.active.all().count(), 1)


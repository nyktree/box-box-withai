from django.contrib.auth.models import Group, User
from django.test import TestCase

from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC, user_has_role


class RolePermissionTests(TestCase):
    def test_user_has_exact_operational_role(self):
        user = User.objects.create_user("ana", password="test123")
        group, _ = Group.objects.get_or_create(name=ROLE_ATTENDANT)
        user.groups.add(group)
        self.assertTrue(user_has_role(user, ROLE_ATTENDANT))
        self.assertFalse(user_has_role(user, ROLE_MECHANIC))

    def test_anonymous_user_has_no_role(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertFalse(user_has_role(AnonymousUser(), ROLE_ADMIN))

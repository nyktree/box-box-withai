from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT


class UserManagementTests(TestCase):
    def setUp(self):
        for name in (ROLE_ADMIN, ROLE_ATTENDANT):
            Group.objects.get_or_create(name=name)
        self.admin = User.objects.create_user("admin", password="test123")
        self.admin.groups.add(Group.objects.get(name=ROLE_ADMIN))
        self.attendant = User.objects.create_user("atendente", password="test123")
        self.attendant.groups.add(Group.objects.get(name=ROLE_ATTENDANT))

    def test_admin_can_open_user_list(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("user_list")).status_code, 200)

    def test_attendant_cannot_open_user_list(self):
        self.client.force_login(self.attendant)
        self.assertEqual(self.client.get(reverse("user_list")).status_code, 403)

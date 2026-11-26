from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from PIL import Image
from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC
from services.models import Part

class RoleActionVisibilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role in (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC):
            Group.objects.get_or_create(name=role)

    def user(self, name, role=None, superuser=False):
        user = User.objects.create_user(name, password="x", is_superuser=superuser, is_staff=superuser)
        if role: user.groups.add(Group.objects.get(name=role))
        return user

    def test_mechanic_does_not_see_creation_actions(self):
        self.client.force_login(self.user("mechanic-ui", ROLE_MECHANIC))
        checks = [("dashboard", "Abrir ordem"), ("order_list", "Nova ordem"), ("customer_list", "Novo cliente"), ("vehicle_list", "Novo veículo"), ("part_list", "Nova peça")]
        for route, label in checks:
            with self.subTest(route=route):
                self.assertNotContains(self.client.get(reverse(route)), label)

    def test_attendant_sees_operational_and_part_actions(self):
        self.client.force_login(self.user("attendant-ui", ROLE_ATTENDANT))
        for route, label in [("dashboard", "Abrir ordem"), ("order_list", "Nova ordem"), ("customer_list", "Novo cliente"), ("vehicle_list", "Novo veículo"), ("part_list", "Nova peça")]:
            with self.subTest(route=route): self.assertContains(self.client.get(reverse(route)), label)

    def test_superuser_receives_all_capabilities(self):
        self.client.force_login(self.user("root-ui", superuser=True))
        response = self.client.get(reverse("dashboard"))
        self.assertTrue(response.context["is_admin_role"])
        self.assertTrue(response.context["can_create_orders"])
        self.assertTrue(response.context["can_manage_part_catalog"])

    def test_admin_capabilities_win_when_user_has_multiple_groups(self):
        user = self.user("admin-mechanic", ROLE_MECHANIC)
        user.groups.add(Group.objects.get(name=ROLE_ADMIN))
        self.client.force_login(user)
        part = Part.objects.create(name="Filtro", code="MULTI", stock_quantity=1, unit_price="10.00")
        dashboard = self.client.get(reverse("dashboard"))
        self.assertTrue(dashboard.context["is_admin_role"])
        self.assertContains(dashboard, reverse("user_list"))
        self.assertContains(self.client.get(reverse("part_list")), reverse("part_deactivate", args=[part.pk]))

    def test_direct_forbidden_url_has_friendly_403_page(self):
        self.client.force_login(self.user("mechanic-forbidden", ROLE_MECHANIC))
        response = self.client.get(reverse("order_create"))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Você não tem permissão", status_code=403)
        self.assertContains(response, reverse("dashboard"), status_code=403)

    def test_base_uses_supplied_brand_assets(self):
        self.client.force_login(self.user("brand-user", ROLE_ATTENDANT))
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "img/boxbox-mark.png")
        self.assertContains(response, "img/favicon.png")
        self.assertNotContains(response, "WORKSHOP OS")
        for name, size in (("boxbox-mark.png", (256, 256)), ("favicon.png", (64, 64))):
            image = Image.open(settings.BASE_DIR / "static" / "img" / name)
            self.assertEqual(image.size, size)
            self.assertEqual(image.mode, "RGBA")

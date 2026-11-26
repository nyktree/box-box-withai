from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

class UIContractTests(TestCase):
    def test_authenticated_layout_has_navigation_and_accessible_mobile_button(self):
        user = User.objects.create_user("admin", password="test123", is_superuser=True)
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, 'aria-label="Abrir menu"')
        self.assertContains(response, "Clientes")
        self.assertContains(response, "Relatórios")
        self.assertContains(response, "app.css")

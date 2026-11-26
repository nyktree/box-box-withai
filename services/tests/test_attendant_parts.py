from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from accounts.permissions import ROLE_ATTENDANT
from services.models import Part

class AttendantPartCatalogTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name=ROLE_ATTENDANT)
        self.user = User.objects.create_user("marina-parts", password="x")
        self.user.groups.add(Group.objects.get(name=ROLE_ATTENDANT))
        self.client.force_login(self.user)

    def test_attendant_can_create_part(self):
        response = self.client.post(reverse("part_create"), {"name": "Filtro", "code": "FLT-1", "description": "", "stock_quantity": 3, "unit_price": "29.90", "is_active": "on"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Part.objects.filter(code="FLT-1").exists())

    def test_attendant_can_edit_but_not_archive_part(self):
        part = Part.objects.create(name="Óleo", code="OL-1", stock_quantity=1, unit_price="20.00")
        response = self.client.post(reverse("part_update", args=[part.pk]), {"name": "Óleo Premium", "code": "OL-1", "description": "", "stock_quantity": 2, "unit_price": "25.00", "is_active": "on"})
        self.assertEqual(response.status_code, 302)
        part.refresh_from_db()
        self.assertEqual(part.name, "Óleo Premium")
        self.assertEqual(self.client.post(reverse("part_deactivate", args=[part.pk])).status_code, 403)

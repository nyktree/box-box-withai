from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from accounts.permissions import ROLE_ADMIN, ROLE_MECHANIC
from customers.models import Customer
from trash.models import TrashRecord
from trash.services import archive_object, permanently_delete, restore_record

class TrashServiceTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name=ROLE_ADMIN)
        self.admin = User.objects.create_user("trash-admin"); self.admin.groups.add(Group.objects.get(name=ROLE_ADMIN))

    def test_archive_records_actor_and_restore_reactivates_same_object(self):
        customer = Customer.objects.create(name="Arquivado", phone="1")
        record = archive_object(customer, self.admin)
        customer.refresh_from_db()
        self.assertFalse(customer.is_active)
        self.assertEqual(record.archived_by, self.admin)
        restore_record(record, self.admin)
        customer.refresh_from_db()
        self.assertTrue(customer.is_active)
        record.refresh_from_db()
        self.assertIsNotNone(record.restored_at)

    def test_admin_can_permanently_delete_unprotected_record(self):
        customer = Customer.objects.create(name="Apagar", phone="1", is_active=False)
        record = TrashRecord.objects.create_for_object(customer, self.admin)
        permanently_delete(record, self.admin)
        self.assertFalse(Customer.objects.filter(pk=customer.pk).exists())

    def test_restored_record_cannot_be_permanently_deleted(self):
        customer = Customer.objects.create(name="Restaurado", phone="1")
        record = archive_object(customer, self.admin)
        restore_record(record, self.admin)
        record.refresh_from_db()
        with self.assertRaises(ValidationError): permanently_delete(record, self.admin)
        self.assertTrue(Customer.objects.filter(pk=customer.pk).exists())

    def test_mechanic_cannot_restore_customer(self):
        Group.objects.get_or_create(name=ROLE_MECHANIC)
        mechanic = User.objects.create_user("mechanic-trash", password="x")
        mechanic.groups.add(Group.objects.get(name=ROLE_MECHANIC))
        record = archive_object(Customer.objects.create(name="Restrito", phone="1"), self.admin)
        self.client.force_login(mechanic)
        self.assertEqual(self.client.post(reverse("trash_restore", args=[record.pk])).status_code, 403)

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

class TrashRecordManager(models.Manager):
    def create_for_object(self, obj, actor):
        return self.create(content_type=ContentType.objects.get_for_model(obj), object_id=obj.pk, label=str(obj), archived_by=actor)

class TrashRecord(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    label = models.CharField(max_length=255)
    archived_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="trash_actions")
    archived_at = models.DateTimeField(auto_now_add=True)
    restored_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="trash_restores")
    restored_at = models.DateTimeField(null=True, blank=True)
    permanently_deleted_at = models.DateTimeField(null=True, blank=True)
    objects = TrashRecordManager()
    class Meta:
        ordering = ("-archived_at",)
        constraints = [models.UniqueConstraint(fields=("content_type", "object_id"), condition=Q(restored_at__isnull=True, permanently_deleted_at__isnull=True), name="unique_active_trash_object")]

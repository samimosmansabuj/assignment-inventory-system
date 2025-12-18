from django.db import models


class AuditLog(models.Model):
    actor = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    old_value = models.JSONField(null=True)
    new_value = models.JSONField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.timestamp} - {self.actor} - {self.action}"


def audit_log(actor, action, obj, old_value=None, new_value=None):
    AuditLog.objects.create(
        actor=actor,
        action=action,
        object_type=obj.__class__.__name__,
        object_id=obj.id,
        old_value=old_value,
        new_value=new_value
    )

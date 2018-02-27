from django.db import models, DatabaseError, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from celery_model_result.exceptions import LockedTaskException
from celery_model_result.fields import TaskResultField, TaskStatusField
from celery_model_result.querysets import TaskStatusQuerySet


class TaskResultModelBase(models.Model):
    status = TaskStatusField()
    result = TaskResultField()

    objects = TaskStatusQuerySet.as_manager()

    class Meta:
        abstract = True


class TaskLockModel(models.Model):
    current_operation = models.CharField(max_length=100, blank=True, null=True)
    current_operation_start = models.DateTimeField(blank=True, null=True)
    is_locked = models.BooleanField(default=False)

    class Meta:
        abstract = True

    @transaction.atomic
    def _acquire_lock(self, operation):
        try:
            locked_self = self._meta.model.objects.select_for_update(nowait=True).get(pk=self.pk)
            if locked_self.is_locked:
                self.__raise_lock_error(locked_self.current_operation)
            locked_self.is_locked = True
            locked_self.current_operation = operation
            locked_self.current_operation_start = timezone.now()
            locked_self.save()
        except DatabaseError:
            self.refresh_from_db()
            if not self.is_locked:
                self._acquire_lock(operation)  # if lock was already released try to acquire it again
            self.__raise_lock_error(self.current_operation)

    def __raise_lock_error(self, current_operation):
            raise LockedTaskException(
                _('Another operation is already in progress in '
                  '{model_name} {name}. '
                  'Currently running operation: {current_operation}').format(
                    model_name=self._meta.model_name,
                    name=self.name,
                    current_operation=current_operation
                ))

    def change_operation_label(self, operation):
        """
        Allows to change operation description with already acquired lock, useful when tasks are running in chain.
        """
        self.current_operation = operation
        self.current_operation_start = timezone.now()
        self.save()

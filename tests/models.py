from django.db import models

from celery_model_result import fields
from celery_model_result.models import TaskResultModelBase, TaskLockModel


class CeleryModelResultModel(models.Model):
    class Meta:
        app_label = 'tests'
        abstract = True


class BaseSampleModel(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        abstract = True


class SampleModel(TaskResultModelBase, BaseSampleModel):
    pass


class SampleCustomStatusModel(BaseSampleModel):
    status_custom = fields.TaskStatusField()
    result = fields.TaskResultField()


class SampleCustomResultModel(BaseSampleModel):
    status = fields.TaskStatusField()
    result_custom = fields.TaskResultField()


class SampleLockModel(SampleModel, TaskLockModel):
    pass

from django.contrib.postgres.fields import JSONField
from django.db import models

from celery_model_result.statuses import STATUS_CHOICES, STATUS_NEW


class DefaultInitKwargsMixin:
    DEFAULT_INIT_KWARGS = {}

    def __init__(self, *args, **kwargs):
        for k, v in self.DEFAULT_INIT_KWARGS.items():
            kwargs.setdefault(k, v)
        super().__init__(*args, **kwargs)


class TaskStatusField(DefaultInitKwargsMixin, models.PositiveSmallIntegerField):
    DEFAULT_INIT_KWARGS = {
        'choices': STATUS_CHOICES,
        'default': STATUS_NEW[0],
        'editable': False
    }


class TaskResultField(DefaultInitKwargsMixin, JSONField):
    DEFAULT_INIT_KWARGS = {
        'null': True,
        'blank': True,
        'editable': False
    }

from celery import Task
from django.core.exceptions import FieldDoesNotExist

from celery_model_result import statuses


class ModelResultTaskBase(Task):
    DEFAULT_STATUS_FIELD = 'status'
    DEFAULT_RESULT_FIELD = 'result'

    def __init__(self):
        self.instance = None
        self._initialize_task_fields()

    def _update_instance_status(self, new_status, result=None):
        setattr(self.instance, self.status_field, new_status[0])
        update_fields = (self.status_field,)
        if result is not None:
            setattr(self.instance, self.result_field, result)
            update_fields += (self.result_field,)
        self.instance.save(update_fields=update_fields)

    def _check_if_model_has_field(self, field):
        try:
            opts = self.instance_class._meta
            opts.get_field(field)
            return True
        except FieldDoesNotExist:
            return False

    def _initialize_task_fields(self):
        # TODO (m.lach) Fill docs, status_field and result_field passed in task declaration
        task_default_fields = self._get_default_fields()
        for attr_name, field_name in task_default_fields:
            if not hasattr(self, attr_name):
                setattr(self, attr_name, field_name)

            assert self._check_if_model_has_field(getattr(self, attr_name)), \
                'Class "{instance_class}" does not have field "{field}"'.format(
                    instance_class=self.instance_class,
                    field=getattr(self, attr_name)
                )

    def _get_default_fields(self):
        task_default_fields = (
            ('status_field', self.DEFAULT_STATUS_FIELD),
            ('result_field', self.DEFAULT_RESULT_FIELD),
        )
        return task_default_fields

    def __call__(self, instance_pk, *args, **kwargs):
        self.instance = self.instance_class.objects.get(pk=instance_pk)
        # self._initialize_task_fields()
        self._update_instance_status(statuses.STATUS_PENDING)
        return self.run(instance_pk=instance_pk, *args, **kwargs)

    def run(self, *args, **kwargs):
        """The body of the task executed by workers."""
        raise NotImplementedError('Tasks must define the run method.')

    def on_success(self, retval, task_id, args, kwargs):
        super(ModelResultTaskBase, self).on_success(retval, task_id, args, kwargs)
        self._update_instance_status(statuses.STATUS_COMPLETED)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(ModelResultTaskBase, self).on_failure(exc, task_id, args, kwargs, einfo)
        # Refreshing instance from db is crucial here, because we want to discard all changes
        # made by different methods. For an example if on_success method would assign string value
        # to instance attribute which corresponds to some Integer database field, then
        # self.instance.save() would throw IntegrityError, handling would be passed to on_failure method,
        # it would try to set proper status and save instance, but again IntegrityError would be thrown because
        # instance in memory still would have wrong value assigned to one of its field causing errors during commit.
        # As a result db model would be still marked as PENDING despite this that it failed.
        self.instance.refresh_from_db()
        task_result = {
            'error_type': type(exc).__name__,
            'error_msg': str(exc)
        }
        self._update_instance_status(statuses.STATUS_ERROR, task_result)


class ChordTaskMixin:
    def __call__(self, chord_result, instance_pk, *args, **kwargs):
        # celery chord require first parameter to be list of results
        kwargs.update({
            'chord_result': chord_result
        })
        return super().__call__(instance_pk, *args, **kwargs)


class ModelResultChordTaskBase(ChordTaskMixin, ModelResultTaskBase):
    pass


class ModelResultTaskWithLock(ModelResultTaskBase):
    DEFAULT_IS_LOCKED_FIELD = 'is_locked'
    DEFAULT_CURRENT_OPERATION_FIELD = 'current_operation'
    DEFAULT_CURRENT_OPERATION_START_FIELD = 'current_operation_start'

    def _get_default_fields(self):
        default_fields = super()._get_default_fields()
        default_fields += (
            ('operation_field', self.DEFAULT_CURRENT_OPERATION_FIELD),
            ('operation_start_field', self.DEFAULT_CURRENT_OPERATION_START_FIELD),
            ('lock_field', self.DEFAULT_IS_LOCKED_FIELD),
        )
        return default_fields

    def __release_lock(self):
        setattr(self.instance, self.operation_field, None)
        setattr(self.instance, self.operation_start_field, None)
        setattr(self.instance, self.lock_field, False)
        self.instance.save(update_fields=(self.operation_field, self.operation_start_field, self.lock_field))

    def on_success(self, retval, task_id, args, kwargs):
        super().on_success(retval, task_id, args, kwargs)
        self.__release_lock()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)
        self.__release_lock()


class ModelResultChordTaskWithLock(ChordTaskMixin, ModelResultTaskWithLock):
    pass


class ReleaseLockTaskBase(ModelResultTaskWithLock):
    def _get_default_fields(self):
        default_fields = (
            ('operation_field', self.DEFAULT_CURRENT_OPERATION_FIELD),
            ('operation_start_field', self.DEFAULT_CURRENT_OPERATION_START_FIELD),
            ('lock_field', self.DEFAULT_IS_LOCKED_FIELD),
        )
        return default_fields

    def _update_instance_status(self, new_status, result=None):
        pass


class ReleaseLockChordTask(ChordTaskMixin, ReleaseLockTaskBase):
    pass

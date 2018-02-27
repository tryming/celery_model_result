import pytest
from django.db import DatabaseError
from django.utils import timezone

from celery_model_result.exceptions import LockedTaskException
from tests.factories import SampleLockModelFactory


@pytest.mark.django_db
class TestLockAcquirement:
    @pytest.fixture(autouse=True)
    def initialize_db(self):
        self.instance = SampleLockModelFactory()
        self.operation_name = 'some operation name'

    def test_acquire_lock(self):
        timezone_before = timezone.now()
        self.instance._acquire_lock(self.operation_name)
        timezone_after = timezone.now()
        self.instance.refresh_from_db()
        assert self.instance.is_locked is True
        assert self.instance.current_operation == self.operation_name
        assert timezone_before < self.instance.current_operation_start < timezone_after

    def test_acquire_lock_on_locked_instance(self):
        new_operation_name = 'new operation name'
        self.instance._acquire_lock(self.operation_name)
        self.instance.refresh_from_db()
        with pytest.raises(LockedTaskException) as excinfo:
            self.instance._acquire_lock(new_operation_name)
        assert self.operation_name in str(excinfo.value)

    def test_acquire_lock_row_selected_for_update(self, mocker):
        self.instance._acquire_lock(self.operation_name)
        with mocker.patch('tests.models.SampleLockModel._perform_acquire_lock', side_effect=DatabaseError):
            with pytest.raises(LockedTaskException) as excinfo:
                self.instance._acquire_lock('some operation name')
        assert self.operation_name in str(excinfo.value)

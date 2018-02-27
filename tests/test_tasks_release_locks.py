import celery
import pytest

from celery_model_result.tasks import ModelResultTaskWithLock
from tests.factories import SampleLockModelFactory
from tests.models import SampleLockModel

app = celery.Celery('tests')


@app.task(base=ModelResultTaskWithLock, bind=True, instance_class=SampleLockModel)
def sample_success_task(self, instance_pk):
    pass


exception_msg = 'some exception msg'


@app.task(base=ModelResultTaskWithLock, bind=True, instance_class=SampleLockModel)
def sample_failure_task(self, instance_pk):
    raise Exception(exception_msg)


@pytest.mark.django_db
class TestReleaseLock:
    @pytest.fixture(autouse=True)
    def initialize_db(self):
        self.locked_instance = SampleLockModelFactory()
        self.locked_instance._acquire_lock('some operation')
        self.locked_instance.refresh_from_db()
        assert self.locked_instance.is_locked is True
        self.unlocked_instance = SampleLockModelFactory()

    def test_release_lock_on_success(self):
        sample_success_task.apply(args=(self.locked_instance.pk,))
        self.locked_instance.refresh_from_db()
        assert self.locked_instance.is_locked is False

    def test_release_lock_on_failure(self):
        sample_failure_task.apply(args=(self.locked_instance.pk,))
        self.locked_instance.refresh_from_db()
        assert self.locked_instance.is_locked is False

    def test_release_released_lock(self):
        sample_success_task.apply(args=(self.unlocked_instance.pk,))
        self.unlocked_instance.refresh_from_db()
        assert self.unlocked_instance.is_locked is False

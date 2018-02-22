import pytest
import celery

from celery_model_result import statuses
from celery_model_result.tasks import ModelResultTaskBase
from tests.factories import SampleModelFactory, SampleCustomStatusModelFactory, SampleCustomResultModelFactory
from tests.models import SampleModel, SampleCustomStatusModel, SampleCustomResultModel

app = celery.Celery('tests')


@app.task(base=ModelResultTaskBase, bind=True, instance_class=SampleModel)
def sample_success_task(self, instance_pk):
    pass


exception_msg = 'some exception msg'


@app.task(base=ModelResultTaskBase, bind=True, instance_class=SampleModel)
def sample_failure_task(self, instance_pk):
    raise Exception(exception_msg)


@app.task(base=ModelResultTaskBase, bind=True, instance_class=SampleCustomStatusModel, status_field='status_custom')
def custom_status_field_task(self, instance_pk):
    pass


@app.task(base=ModelResultTaskBase, bind=True, instance_class=SampleCustomResultModel, result_field='result_custom')
def custom_result_field_task(self, instance_pk):
    raise Exception(exception_msg)


@pytest.mark.django_db
class TestTaskStatusAndMessage:
    @pytest.fixture(autouse=True)
    def initialize_db(self):
        self.instance = SampleModelFactory()

    def test_success(self):
        sample_success_task.apply(args=(self.instance.pk,))
        self.instance.refresh_from_db()
        assert self.instance.status == statuses.STATUS_COMPLETED[0]
        assert self.instance.result is None

    def test_failure(self):
        sample_failure_task.apply(args=(self.instance.pk,))
        self.instance.refresh_from_db()
        assert self.instance.status == statuses.STATUS_ERROR[0]
        assert self.instance.result['error_msg'] == exception_msg


@pytest.mark.django_db
class TestTaskCustomStatusField:
    @pytest.fixture(autouse=True)
    def initialize_db(self):
        self.instance = SampleCustomStatusModelFactory()

    def test_field_exists(self):
        custom_status_field_task.apply(args=(self.instance.pk,))
        self.instance.refresh_from_db()
        assert self.instance.status_custom == statuses.STATUS_COMPLETED[0]

    def test_field_does_not_exist(self):
        @app.task(base=ModelResultTaskBase, bind=True, instance_class=SampleCustomStatusModel)
        def custom_status_field_wrong_field_task(self, instance_pk):
            pass
        with pytest.raises(AssertionError) as excinfo:
            custom_status_field_wrong_field_task.apply(args=(self.instance.pk,))
        assert ModelResultTaskBase.DEFAULT_STATUS_FIELD in str(excinfo.value)


@pytest.mark.django_db
class TestTaskCustomResultField:
    @pytest.fixture(autouse=True)
    def initialize_db(self):
        self.instance = SampleCustomResultModelFactory()

    def test_field_exists(self):
        custom_result_field_task.apply(args=(self.instance.pk,))
        self.instance.refresh_from_db()
        assert self.instance.result_custom['error_msg'] == exception_msg

    def test_field_does_not_exist(self):
        @app.task(base=ModelResultTaskBase, bind=True, instance_class=SampleCustomResultModel)
        def custom_result_field_wrong_field_task(self, instance_pk):
            pass

        with pytest.raises(AssertionError) as excinfo:
            custom_result_field_wrong_field_task.apply(args=(self.instance.pk,))
        assert ModelResultTaskBase.DEFAULT_RESULT_FIELD in str(excinfo.value)

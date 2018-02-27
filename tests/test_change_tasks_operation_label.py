import pytest
from django.utils import timezone

from tests.factories import SampleLockModelFactory


@pytest.mark.django_db
class TestChangeTasksOperationLabel:
    @pytest.fixture(autouse=True)
    def initialize_db(self):
        self.instance = SampleLockModelFactory()

    def test_change_label(self):
        new_operation_label = 'new operation label'
        timezone_before = timezone.now()
        self.instance.change_operation_label(new_operation_label)
        timezone_after = timezone.now()
        self.instance.refresh_from_db()
        assert self.instance.current_operation == new_operation_label
        assert timezone_before < self.instance.current_operation_start < timezone_after

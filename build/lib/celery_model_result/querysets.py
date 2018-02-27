from django.db import models


class TaskStatusQuerySet(models.QuerySet):
    def __filter_by_status(self, status_code):
        return self.filter(status=status_code)

    def new(self):
        return self.__filter_by_status(self.model.STATUS_NEW[0])

    def pending(self):
        return self.__filter_by_status(self.model.STATUS_PENDING[0])

    def completed(self):
        return self.__filter_by_status(self.model.STATUS_COMPLETED[0])

    def error(self):
        return self.__filter_by_status(self.model.STATUS_ERROR[0])


class TaskLockQuerySet(models.QuerySet):
    def __filter_by_lock(self, is_locked):
        return self.filter(is_locked=is_locked)

    def locked(self):
        return self.__filter_by_lock(True)

    def unlocked(self):
        return self.__filter_by_lock(False)

Celery Model Result
=======================

Package making working with celery tasks and synchronizing them much easier.

This project offers following functionalities:

- Automatically fetching db objects based on its primary key passed to task call
  and django model class specified in task declaration,
- Automatically setting proper tasks status based on its progress (new, pending, completed, error),
- Automatically setting thrown exceptions traceback in instance field,
- Automatically checking if another asynchronous operation (might be single task or tasks executed using *chord*)
  is in progress and returning proper errors.

Library provides base classes for tasks and models enabling mentioned above functions.

Information about contributing can be found in CONTRIBUTING.md file


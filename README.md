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

For more details see docs or example tasks.

`The source for this project is available here
<https://bitbucket.org/bitcraftteam/celery_model_result>`


TODO (m.lach) Add information about running tests just like it is done in DRF


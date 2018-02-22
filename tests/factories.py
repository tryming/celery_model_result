import factory

from tests.models import SampleModel, SampleCustomStatusModel, SampleCustomResultModel


class NameFakerMixin:
    name = factory.Faker('name')


class SampleModelFactory(NameFakerMixin, factory.DjangoModelFactory):
    class Meta:
        model = SampleModel


class SampleCustomStatusModelFactory(NameFakerMixin, factory.DjangoModelFactory):
    class Meta:
        model = SampleCustomStatusModel


class SampleCustomResultModelFactory(NameFakerMixin, factory.DjangoModelFactory):
    class Meta:
        model = SampleCustomResultModel

from typing import Type, TypeVar, Generic, Optional, List
from django.db import models

T = TypeVar('T', bound=models.Model)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
        
    def get_by_field(self, **kwargs) -> Optional[T]:
        try:
            return self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            return None
        
    def get_all(self) -> List[T]:
        return list(self.model.objects.all())
    
    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)

    def update(self, instance: T, **kwargs) -> T:
        valid_fields = [f.name for f in instance._meta.get_fields()]
        
        for key, value in kwargs.items():
            if key in valid_fields:
                setattr(instance, key, value)
        
        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        instance.delete()

    def exists(self, **kwargs) -> bool:
        return self.model.objects.filter(**kwargs).exists()
        
    def count(self, **kwargs) -> int:
        return self.model.objects.filter(**kwargs).count()
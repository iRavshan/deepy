from ..models import Section, Lesson
from .base_repository import BaseRepository

class SectionRepository(BaseRepository):
    def __init__(self):
        super().__init__(Section)
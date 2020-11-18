import difflib

from collections.abc import Sequence
from typing import Union, List

from .chapter import Chapter
from .partialchapter import PartialChapter
from .language import Language

class ChapterList(Sequence):
    """ A class used for managing and filtering a Manga Instance's chapters.
    """

    def __init__(self, chapters: Union[List[Chapter], List[PartialChapter]]):
        self._chapters = chapters

    def __getitem__(self, i):
        return self._chapters[i]

    def __len__(self):
        return len(self._chapters)

    def _append(self, element: Chapter):
        self._chapters.append(element)
        return self._chapters

    def filter_language(self, *lang: Union[Language, str]) -> 'ChapterList':
        """Filter by languages, connected by logical OR.
        Returns a ChapterList of the chapters with corresponding languages.

        Returns:
            ChapterList
        """
        if not isinstance(lang, Language):
            lang = Language(lang)
        return ChapterList([chapter for chapter in self._chapters if chapter.lang_code == lang])

    def filter_title(self, *titles, difference_cutoff: float = 0.8) -> 'ChapterList':
        """Filter by titles, connected by logical OR.
        Returns a ChapterList of the chapters with corresponding titles.

        Returns:
            ChapterList
        """

        tit = [chapter.title for chapter in self._chapters]

        results = [difflib.get_close_matches(t, tit, cutoff=difference_cutoff) for t in titles]

        chapters = [chapter for chapter in self._chapters if chapter.title in results]

        return ChapterList(chapters)

    def filter_chapter_number(self, *numbers: List[int]) -> 'ChapterList':
        """Filter by chapter number, connected by logical OR.
        Returns a ChapterList of the chapters with according chapter numbers.

        Returns:
            ChapterList
        """
        return ChapterList([chapter for chapter in self._chapters if float(chapter.chapter) in numbers])

    def filter_id(self, *ids: List[int]) -> 'ChapterList':
        """
        Filter by id, connected by logical OR.
        Returns ChapterList of chapters with corresponding ids.

        Returns:
            ChapterList
        """
        return ChapterList([chapter for chapter in self._chapters if float(chapter.id) in ids])

    @classmethod
    def from_partial_chapters(cls, chapters):
        chapters = [PartialChapter(**chapter) for chapter in chapters]
        return cls(chapters)
import os
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class CustomUrlObject:
    """This is the class to build Url string."""
    locale: str = field(init=False)
    search_type: str = field(init=False)
    search_term: str = field(init=False)

    def make_url(self) -> str:
        """This is the data class method to prepare URL string
        :return str: Url string to make a search in API"""
        self.search_term = self.search_term.strip()
        self.search_term = self.search_term.replace(" ", "%20")
        return f"https://api.themoviedb.org/3/search/{self.search_type}?api_key={os.environ.get('API_KEY')}&language=ru-RU&query={self.search_term}&page=1&include_adult=true"

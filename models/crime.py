"""The definition of the crime model."""
from datetime import date


class Crime:
    """The definition of the crime class."""
    def __init__(self, category: str, date: date):
        """Instantiates a crime model."""
        self.category = category
        self.date = date
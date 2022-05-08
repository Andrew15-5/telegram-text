from abc import ABC, abstractmethod
from typing import Union

NEW_LINE = '\n'
SPACE = ' '


class AbstractElement(ABC):
    """The interface every component implements."""

    @abstractmethod
    def to_plain_text(self) -> str:
        """Format the element to plain text without escaping, tags or special
        characters.
        """
        raise NotImplementedError

    @abstractmethod
    def to_markdown(self) -> str:
        """Format the element to Markdown/MarkdownV2 format according to
        Telegram specification with escaping if necessary.
        """
        raise NotImplementedError

    @abstractmethod
    def to_html(self) -> str:
        """Format the element to html according to Telegram specification."""
        raise NotImplementedError


class Element(AbstractElement, ABC):
    def __add__(self, other: Union[str, "Element"]):
        if isinstance(other, str):
            other = PlainText(other)
        return Chain(self, other)

    def __eq__(self, other: "Element"):
        return type(self) is type(other) and self.to_plain_text() == other.to_plain_text()

    def __str__(self) -> str:
        return self.to_markdown()


class Text(Element):
    def __init__(self, text: Union[str, Element]):
        if isinstance(text, Element):
            text = text.to_plain_text()
        self.text: str = text

    def to_plain_text(self) -> str:
        return self.text

    def to_markdown(self) -> str:
        return self.text

    def to_html(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.text}>"


class PlainText(Text):
    escaping_chars = ('_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!')

    def _escape(self, text: str) -> str:
        escaping_prefix = '\\'
        mapping = str.maketrans({char: escaping_prefix + char for char in self.escaping_chars})
        return "".join(char.translate(mapping) for char in text)

    def to_markdown(self) -> str:
        return self._escape(self.text)


class Chain(Element):
    def __init__(self, *elements: Element, sep: str = SPACE):
        self.elements = elements
        self.sep = sep

    def __add__(self, other: Union[str, "Element"]):
        if isinstance(other, str):
            other = PlainText(other)

        if self.sep == SPACE:  # Optimization for default separator
            return Chain(*self.elements, other)
        return Chain(self, other)

    def __contains__(self, item):
        return item in self.elements

    def to_plain_text(self) -> str:
        return self.sep.join(element.to_plain_text() for element in self.elements)

    def to_markdown(self) -> str:
        return self.sep.join(element.to_markdown() for element in self.elements)

    def to_html(self) -> str:
        return self.sep.join(element.to_html() for element in self.elements)

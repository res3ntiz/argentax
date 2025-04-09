"""
Модуль для работы с консолью в ArgentaX.

Этот модуль содержит класс Console для вывода стилизованного текста в терминал.
"""

from typing import Optional
import sys
import re

try:
    from rich.console import Console as RichConsole
    from rich.theme import Theme as RichTheme
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .theme import Theme


class Console:
    """Обертка для работы с консолью."""
    
    def __init__(self, theme: Optional[Theme] = None):
        """Инициализация консоли.
        
        Args:
            theme: Тема оформления
        """
        self.theme = theme or Theme()
        
        # Инициализация Rich, если доступен
        if RICH_AVAILABLE:
            rich_theme = RichTheme({
                "prompt": self.theme.get_style("prompt"),
                "command": self.theme.get_style("command"),
                "error": self.theme.get_style("error"),
                "help": self.theme.get_style("help"),
                "divider": self.theme.get_style("divider"),
            })
            self.rich_console = RichConsole(theme=rich_theme)
        else:
            self.rich_console = None
    
    def print(self, text: str, style: str = None) -> None:
        """Выводит текст в консоль.
        
        Args:
            text: Текст для вывода
            style: Стиль текста (если None, используется обычный текст)
        """
        if self.rich_console:
            self.rich_console.print(text, style=style)
        else:
            print(text)
    
    def input(self, prompt: str = "", style: str = None) -> str:
        """Запрашивает ввод от пользователя.
        
        Args:
            prompt: Строка приглашения
            style: Стиль приглашения (если None, используется стиль "prompt" из темы)
            
        Returns:
            Введенная пользователем строка
        """
        if style is None:
            style = self.theme.get_style("prompt")
        
        if self.rich_console and RICH_AVAILABLE:
            return Prompt.ask(prompt, console=self.rich_console)
        else:
            return input(prompt)
    
    def error(self, text: str) -> None:
        """Выводит сообщение об ошибке.
        
        Args:
            text: Текст сообщения
        """
        self.print(text, style=self.theme.get_style("error"))
    
    def success(self, text: str) -> None:
        """Выводит сообщение об успехе.
        
        Args:
            text: Текст сообщения
        """
        self.print(text, style=self.theme.get_style("command"))
    
    def help(self, text: str) -> None:
        """Выводит справочное сообщение.
        
        Args:
            text: Текст сообщения
        """
        self.print(text, style=self.theme.get_style("help"))
    
    def divider(self, char: str = "-", width: int = 80) -> None:
        """Выводит разделительную линию.
        
        Args:
            char: Символ для разделительной линии
            width: Ширина разделительной линии
        """
        self.print(char * width, style=self.theme.get_style("divider"))

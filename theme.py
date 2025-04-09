"""
Модуль для работы с UI компонентами в ArgentaX.

Этот модуль содержит классы для стилизации и отображения текста в консоли.
"""

from typing import Dict, Optional
import sys


class Theme:
    """Тема оформления интерфейса."""
    
    def __init__(
        self,
        prompt: str = "bold",
        command: str = "green",
        error: str = "red bold",
        help: str = "cyan",
        divider: str = "dim",
    ):
        """Инициализация темы.
        
        Args:
            prompt: Стиль строки приглашения
            command: Стиль команды
            error: Стиль сообщения об ошибке
            help: Стиль справки
            divider: Стиль разделителя
        """
        self.styles = {
            "prompt": prompt,
            "command": command,
            "error": error,
            "help": help,
            "divider": divider,
        }
    
    def get_style(self, name: str) -> str:
        """Возвращает стиль по имени.
        
        Args:
            name: Имя стиля
            
        Returns:
            Строка стиля или пустая строка, если стиль не найден
        """
        return self.styles.get(name, "")
    
    def set_style(self, name: str, style: str) -> None:
        """Устанавливает стиль.
        
        Args:
            name: Имя стиля
            style: Строка стиля
        """
        self.styles[name] = style

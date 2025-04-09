"""
Модуль для работы с флагами команд в ArgentaX.

Этот модуль содержит классы для создания и управления флагами команд.
"""

from typing import Any, Dict, List, Optional, Pattern, Type, Union
import re


class Flag:
    """Флаг команды."""
    
    def __init__(
        self,
        name: str = None,
        type: Type = str,
        default: Any = None,
        required: bool = False,
        description: str = None,
        choices: List[Any] = None,
        pattern: Optional[Pattern] = None,
    ):
        """Инициализация флага.
        
        Args:
            name: Имя флага
            type: Тип значения флага
            default: Значение по умолчанию
            required: Является ли флаг обязательным
            description: Описание флага
            choices: Список допустимых значений
            pattern: Регулярное выражение для проверки значения
        """
        self.name = name
        self.type = type
        self.default = default
        self.required = required
        self.description = description
        self.choices = choices
        self.pattern = pattern
    
    def __repr__(self) -> str:
        """Строковое представление флага."""
        return f"Flag(name={self.name}, type={self.type.__name__}, default={self.default}, required={self.required})"


class Flags:
    """Коллекция флагов команды."""
    
    def __init__(self, *flags: Flag):
        """Инициализация коллекции флагов.
        
        Args:
            *flags: Флаги для добавления в коллекцию
        """
        self._flags: Dict[str, Flag] = {}
        
        for flag in flags:
            if flag.name:
                self._flags[flag.name] = flag
    
    def add(self, flag: Flag) -> None:
        """Добавляет флаг в коллекцию.
        
        Args:
            flag: Флаг для добавления
        """
        if flag.name:
            self._flags[flag.name] = flag
    
    def get(self, name: str) -> Optional[Flag]:
        """Возвращает флаг по имени.
        
        Args:
            name: Имя флага
            
        Returns:
            Объект Flag или None, если флаг не найден
        """
        return self._flags.get(name)
    
    def get_all(self) -> Dict[str, Flag]:
        """Возвращает словарь всех флагов.
        
        Returns:
            Словарь флагов, где ключ - имя флага, значение - объект Flag
        """
        return self._flags.copy()
    
    def __iter__(self):
        """Итератор по флагам."""
        return iter(self._flags.values())
    
    def __len__(self) -> int:
        """Количество флагов в коллекции."""
        return len(self._flags)


class InputFlag:
    """Флаг, введенный пользователем."""
    
    def __init__(self, name: str, value: Any):
        """Инициализация введенного флага.
        
        Args:
            name: Имя флага
            value: Значение флага
        """
        self.name = name
        self.value = value
    
    def get_name(self) -> str:
        """Возвращает имя флага."""
        return self.name
    
    def get_value(self) -> Any:
        """Возвращает значение флага."""
        return self.value
    
    def __repr__(self) -> str:
        """Строковое представление флага."""
        return f"InputFlag(name={self.name}, value={self.value})"


class InputFlags:
    """Коллекция флагов, введенных пользователем."""
    
    def __init__(self, flags: Dict[str, Any] = None):
        """Инициализация коллекции введенных флагов.
        
        Args:
            flags: Словарь флагов, где ключ - имя флага, значение - значение флага
        """
        self._flags: Dict[str, InputFlag] = {}
        
        if flags:
            for name, value in flags.items():
                self._flags[name] = InputFlag(name, value)
    
    def add(self, name: str, value: Any) -> None:
        """Добавляет флаг в коллекцию.
        
        Args:
            name: Имя флага
            value: Значение флага
        """
        self._flags[name] = InputFlag(name, value)
    
    def get(self, name: str) -> Optional[InputFlag]:
        """Возвращает флаг по имени.
        
        Args:
            name: Имя флага
            
        Returns:
            Объект InputFlag или None, если флаг не найден
        """
        return self._flags.get(name)
    
    def get_value(self, name: str, default: Any = None) -> Any:
        """Возвращает значение флага по имени.
        
        Args:
            name: Имя флага
            default: Значение по умолчанию, если флаг не найден
            
        Returns:
            Значение флага или default, если флаг не найден
        """
        flag = self._flags.get(name)
        return flag.value if flag else default
    
    def __iter__(self):
        """Итератор по флагам."""
        return iter(self._flags.values())
    
    def __len__(self) -> int:
        """Количество флагов в коллекции."""
        return len(self._flags)
    
    def __contains__(self, name: str) -> bool:
        """Проверяет, содержится ли флаг в коллекции."""
        return name in self._flags

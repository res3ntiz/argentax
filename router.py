"""
Модуль маршрутизации команд в ArgentaX.

Этот модуль содержит класс Router, который отвечает за маршрутизацию
команд и разбор командной строки.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import shlex
import difflib

from .command.base import Command
from .utils.exceptions import CommandNotFoundError


class Router:
    """Маршрутизатор команд.
    
    Обычно не используется напрямую, а через App.
    """
    
    def __init__(self, case_sensitive: bool = False):
        """Инициализация маршрутизатора.
        
        Args:
            case_sensitive: Учитывать регистр команд
        """
        self._commands: Dict[str, Command] = {}
        self._aliases: Dict[str, str] = {}  # Отображение псевдонимов на имена команд
        self.case_sensitive = case_sensitive
    
    def add_command(self, command: Command) -> None:
        """Добавляет команду в маршрутизатор.
        
        Args:
            command: Команда для добавления
        """
        name = command.name
        
        # Если не учитываем регистр, приводим имя к нижнему регистру
        if not self.case_sensitive:
            name = name.lower()
        
        self._commands[name] = command
        
        # Добавляем псевдонимы
        for alias in command.aliases:
            alias_key = alias if self.case_sensitive else alias.lower()
            self._aliases[alias_key] = name
    
    def get_command(self, name: str) -> Optional[Command]:
        """Возвращает команду по имени.
        
        Args:
            name: Имя команды или псевдоним
            
        Returns:
            Объект Command или None, если команда не найдена
        """
        # Если не учитываем регистр, приводим имя к нижнему регистру
        if not self.case_sensitive:
            name = name.lower()
        
        # Проверяем, является ли имя псевдонимом
        if name in self._aliases:
            name = self._aliases[name]
        
        return self._commands.get(name)
    
    def get_all_commands(self) -> List[Command]:
        """Возвращает список всех зарегистрированных команд.
        
        Returns:
            Список объектов Command
        """
        return list(self._commands.values())
    
    def parse_command_line(self, command_line: str) -> Tuple[Command, List[Any], Dict[str, Any]]:
        """Разбирает строку команды на команду и аргументы.
        
        Args:
            command_line: Строка команды
            
        Returns:
            Кортеж (команда, позиционные аргументы, именованные аргументы)
            
        Raises:
            CommandNotFoundError: Если команда не найдена
        """
        # Разбиваем строку на токены, учитывая кавычки
        try:
            tokens = shlex.split(command_line)
        except ValueError as e:
            # Ошибка разбора строки (например, незакрытые кавычки)
            raise ValueError(f"Ошибка разбора командной строки: {str(e)}")
        
        if not tokens:
            raise ValueError("Пустая командная строка")
        
        # Первый токен - имя команды
        cmd_name = tokens[0]
        
        # Получаем команду
        command = self.get_command(cmd_name)
        if not command:
            raise CommandNotFoundError(f"Команда '{cmd_name}' не найдена")
        
        # Разбираем аргументы
        args, kwargs = command.parse_args(tokens[1:])
        
        return command, args, kwargs
    
    def find_similar_commands(self, name: str, threshold: float = 0.6) -> List[str]:
        """Находит команды, похожие на указанное имя.
        
        Args:
            name: Имя для поиска похожих команд
            threshold: Порог схожести (от 0 до 1)
            
        Returns:
            Список имен похожих команд
        """
        if not self.case_sensitive:
            name = name.lower()
        
        # Получаем все имена команд и псевдонимы
        all_names = list(self._commands.keys()) + list(self._aliases.keys())
        
        # Находим похожие имена
        similar = difflib.get_close_matches(name, all_names, n=3, cutoff=threshold)
        
        return similar

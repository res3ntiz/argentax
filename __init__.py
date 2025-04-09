"""
Модуль для асинхронной поддержки в ArgentaX.

Этот модуль содержит классы и функции для работы с асинхронными командами.
"""

from typing import Any, Callable, Dict, List, Optional, Union
import asyncio
import inspect
import functools

from ..app import App
from ..command.base import Command
from ..utils.exceptions import CommandExecutionError


def async_command(
    name: str = None, 
    description: str = None, 
    aliases: List[str] = None
) -> Callable:
    """Декоратор для регистрации асинхронной команды.
    
    Args:
        name: Имя команды (если None, используется имя функции)
        description: Описание команды
        aliases: Альтернативные имена команды
        
    Returns:
        Декорированная функция
        
    Примеры:
        >>> @app.async_command("fetch", "Загружает данные с сервера")
        ... async def fetch(url: str):
        ...     # Имитация асинхронного запроса
        ...     await asyncio.sleep(1)
        ...     return f"Data fetched from {url}"
    """
    def decorator(func: Callable) -> Callable:
        # Проверяем, что функция асинхронная
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Функция должна быть асинхронной (async def)")
        
        # Устанавливаем атрибут, чтобы AsyncApp мог определить асинхронную команду
        func._is_async_command = True
        func._async_command_name = name
        func._async_command_description = description
        func._async_command_aliases = aliases
        
        return func
    
    return decorator


class AsyncApp(App):
    """Асинхронная версия приложения ArgentaX.
    
    Примеры:
        >>> app = AsyncApp(name="Async CLI")
        >>> @app.command("fetch", "Загружает данные с сервера")
        ... async def fetch(url: str):
        ...     # Имитация асинхронного запроса
        ...     await asyncio.sleep(1)
        ...     return f"Data fetched from {url}"
        >>> asyncio.run(app.run())
    """
    
    def command(
        self, 
        name: str = None, 
        description: str = None, 
        aliases: List[str] = None
    ) -> Callable:
        """Декоратор для регистрации команды.
        
        Поддерживает как синхронные, так и асинхронные функции.
        
        Args:
            name: Имя команды (если None, используется имя функции)
            description: Описание команды
            aliases: Альтернативные имена команды
            
        Returns:
            Декорированная функция
        """
        def decorator(func: Callable) -> Callable:
            cmd_name = name or func.__name__
            cmd_description = description or func.__doc__
            
            # Проверяем, асинхронная ли функция
            is_async = inspect.iscoroutinefunction(func)
            
            if is_async:
                # Для асинхронных функций создаем обертку
                @functools.wraps(func)
                def async_wrapper(*args, **kwargs):
                    # Запускаем асинхронную функцию в текущем цикле событий
                    # или создаем новый, если его нет
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    return loop.run_until_complete(func(*args, **kwargs))
                
                # Регистрируем обертку как обычную команду
                return super().command(cmd_name, cmd_description, aliases)(async_wrapper)
            else:
                # Для синхронных функций используем обычную регистрацию
                return super().command(cmd_name, cmd_description, aliases)(func)
        
        return decorator
    
    async def run(self) -> None:
        """Запускает асинхронный интерактивный режим."""
        self.console.print(f"Добро пожаловать в {self.name}!")
        self.console.print(f"Введите 'help' для получения справки или '{self.exit_command}' для выхода.")
        
        while True:
            try:
                command_line = self.console.input(self.prompt)
                if not command_line.strip():
                    continue
                
                result = await self.execute(command_line)
                if result is not None:
                    self.console.print(str(result))
            
            except KeyboardInterrupt:
                self.console.print("\nПрервано пользователем.")
                break
            
            except Exception as e:
                self.console.error(f"Ошибка: {str(e)}")
    
    async def execute(self, command_line: str) -> Any:
        """Асинхронно выполняет команду.
        
        Args:
            command_line: Строка с командой и аргументами
            
        Returns:
            Результат выполнения команды
            
        Raises:
            CommandNotFoundError: Если команда не найдена
            CommandError: При ошибке выполнения команды
        """
        try:
            # Разбор командной строки
            command, args, kwargs = self.router.parse_command_line(command_line)
            
            # Получаем оригинальный обработчик
            handler = command.handler
            
            # Проверяем, асинхронный ли обработчик
            if inspect.iscoroutinefunction(handler):
                # Выполняем асинхронно
                return await handler(*args, **kwargs)
            else:
                # Выполняем синхронно
                return command.execute(*args, **kwargs)
        
        except Exception as e:
            # Оборачиваем все исключения
            if not isinstance(e, CommandExecutionError):
                raise CommandExecutionError(f"Ошибка при выполнении команды: {str(e)}") from e
            raise

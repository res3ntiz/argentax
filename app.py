"""
Основной модуль приложения ArgentaX.

Этот модуль содержит класс App, который является основной точкой входа
для создания интерактивных командных оболочек с помощью ArgentaX.
"""

from typing import Any, Callable, Dict, List, Optional, Union, Type
import sys
import shlex
from inspect import signature, Parameter

from .command.base import Command
from .command.flags import Flag
from .router import Router
from .ui.console import Console
from .ui.theme import Theme
from .utils.exceptions import CommandNotFoundError, CommandExecutionError
from .plugins.base import Plugin


class App:
    """Основной класс приложения ArgentaX.
    
    Примеры:
        Простое приложение:
        
        >>> app = App(name="My CLI")
        >>> @app.command("hello")
        ... def hello(name: str = "World"):
        ...     return f"Hello, {name}!"
        >>> app.run()
        
        С настройкой стилей:
        
        >>> app = App(
        ...     name="Styled CLI",
        ...     theme=Theme(
        ...         prompt="cyan bold",
        ...         command="green",
        ...         error="red bold"
        ...     )
        ... )
    """
    
    def __init__(
        self,
        name: str = "ArgentaX",
        description: str = None,
        prompt: str = "> ",
        exit_command: str = "exit",
        theme: Optional[Theme] = None,
        case_sensitive: bool = False,
        plugins: List[Plugin] = None,
    ):
        """Инициализация приложения.
        
        Args:
            name: Название приложения
            description: Описание приложения
            prompt: Строка приглашения ввода
            exit_command: Команда для выхода
            theme: Тема оформления
            case_sensitive: Учитывать регистр команд
            plugins: Список плагинов
        """
        self.name = name
        self.description = description or f"{name} - CLI приложение на базе ArgentaX"
        self.prompt = prompt
        self.exit_command = exit_command
        self.theme = theme or Theme()
        self.router = Router(case_sensitive=case_sensitive)
        self.console = Console(theme=self.theme)
        self.plugins = plugins or []
        
        # Регистрация встроенных команд
        self._register_builtin_commands()
        
        # Инициализация плагинов
        for plugin in self.plugins:
            plugin.initialize(self)
    
    def _register_builtin_commands(self) -> None:
        """Регистрирует встроенные команды."""
        
        @self.command(self.exit_command, "Выход из приложения")
        def exit_app():
            """Выход из приложения."""
            sys.exit(0)
        
        @self.command("help", "Показать справку по командам")
        def help_command(command: str = None):
            """Показывает справку по командам.
            
            Args:
                command: Имя команды для получения подробной справки
            """
            if command:
                cmd = self.router.get_command(command)
                if cmd:
                    return self._format_command_help(cmd)
                else:
                    return f"Команда '{command}' не найдена."
            else:
                return self._format_help()
    
    def _format_help(self) -> str:
        """Форматирует общую справку по командам."""
        result = [f"{self.name}", "-" * len(self.name), ""]
        
        if self.description:
            result.extend([self.description, ""])
        
        result.append("Доступные команды:")
        
        # Группировка команд по категориям
        commands = self.router.get_all_commands()
        
        for cmd in sorted(commands, key=lambda c: c.name):
            result.append(f"  {cmd.name:<15} - {cmd.description or 'Нет описания'}")
        
        result.extend([
            "",
            f"Введите '{self.exit_command}' для выхода или 'help <команда>' для получения справки по конкретной команде."
        ])
        
        return "\n".join(result)
    
    def _format_command_help(self, command: Command) -> str:
        """Форматирует справку по конкретной команде."""
        result = [f"Команда: {command.name}", ""]
        
        if command.description:
            result.extend([command.description, ""])
        
        # Получение информации о параметрах
        params = []
        for name, param in command.get_parameters().items():
            if isinstance(param, Flag):
                flag_info = f"--{name}"
                if param.description:
                    flag_info += f": {param.description}"
                if param.default is not None:
                    flag_info += f" (по умолчанию: {param.default})"
                if param.required:
                    flag_info += " [обязательный]"
                params.append(flag_info)
        
        if params:
            result.append("Параметры:")
            for param in params:
                result.append(f"  {param}")
        
        if command.aliases:
            result.extend([
                "",
                "Альтернативные имена:",
                "  " + ", ".join(command.aliases)
            ])
        
        return "\n".join(result)
    
    def command(
        self, 
        name: str = None, 
        description: str = None, 
        aliases: List[str] = None
    ) -> Callable:
        """Декоратор для регистрации команды.
        
        Args:
            name: Имя команды (если None, используется имя функции)
            description: Описание команды
            aliases: Альтернативные имена команды
            
        Returns:
            Декорированная функция
            
        Примеры:
            >>> @app.command("greet", "Приветствует пользователя")
            ... def hello(name: str = "World"):
            ...     return f"Hello, {name}!"
        """
        def decorator(func: Callable) -> Callable:
            cmd_name = name or func.__name__
            cmd_description = description or func.__doc__
            
            # Анализ сигнатуры функции для создания флагов
            flags = {}
            sig = signature(func)
            
            for param_name, param in sig.parameters.items():
                # Если параметр уже является флагом, используем его
                if param.default is not Parameter.empty and isinstance(param.default, Flag):
                    flag = param.default
                    flag.name = param_name  # Убедимся, что имя флага соответствует параметру
                    flags[param_name] = flag
                # Иначе создаем флаг на основе аннотации типа и значения по умолчанию
                elif param_name != 'self':  # Пропускаем self для методов
                    default = None if param.default is Parameter.empty else param.default
                    param_type = param.annotation if param.annotation is not Parameter.empty else type(default) if default is not None else str
                    required = param.default is Parameter.empty
                    flags[param_name] = Flag(
                        name=param_name,
                        type=param_type,
                        default=default,
                        required=required
                    )
            
            # Создание и регистрация команды
            command = Command(
                name=cmd_name,
                handler=func,
                description=cmd_description,
                aliases=aliases,
                flags=flags
            )
            
            self.router.add_command(command)
            return func
        
        return decorator
    
    def run(self) -> None:
        """Запускает интерактивный режим приложения."""
        self.console.print(f"Добро пожаловать в {self.name}!")
        self.console.print(f"Введите 'help' для получения справки или '{self.exit_command}' для выхода.")
        
        while True:
            try:
                command_line = self.console.input(self.prompt)
                if not command_line.strip():
                    continue
                
                result = self.execute(command_line)
                if result is not None:
                    self.console.print(str(result))
            
            except KeyboardInterrupt:
                self.console.print("\nПрервано пользователем.")
                break
            
            except Exception as e:
                self.console.error(f"Ошибка: {str(e)}")
    
    def execute(self, command_line: str) -> Any:
        """Выполняет команду без запуска интерактивного режима.
        
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
            
            # Выполнение команды
            return command.execute(*args, **kwargs)
        
        except CommandNotFoundError:
            # Если команда не найдена, пробуем найти похожие
            tokens = shlex.split(command_line)
            if not tokens:
                return None
            
            cmd_name = tokens[0]
            similar_commands = self.router.find_similar_commands(cmd_name)
            
            if similar_commands:
                suggestions = ", ".join(similar_commands)
                raise CommandNotFoundError(
                    f"Команда '{cmd_name}' не найдена. Возможно, вы имели в виду: {suggestions}"
                )
            else:
                raise CommandNotFoundError(f"Команда '{cmd_name}' не найдена.")
        
        except Exception as e:
            # Оборачиваем все остальные исключения
            if not isinstance(e, CommandExecutionError):
                raise CommandExecutionError(f"Ошибка при выполнении команды: {str(e)}") from e
            raise

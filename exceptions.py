"""
Модуль исключений ArgentaX.

Этот модуль содержит иерархию исключений, используемых в библиотеке ArgentaX.
"""

class ArgentaError(Exception):
    """Базовый класс для всех исключений ArgentaX."""
    pass


class CommandError(ArgentaError):
    """Базовый класс для ошибок, связанных с командами."""
    pass


class CommandNotFoundError(CommandError):
    """Команда не найдена."""
    pass


class CommandExecutionError(CommandError):
    """Ошибка выполнения команды."""
    pass


class FlagError(CommandError):
    """Базовый класс для ошибок, связанных с флагами."""
    pass


class FlagValueError(FlagError):
    """Некорректное значение флага."""
    pass


class RouterError(ArgentaError):
    """Базовый класс для ошибок, связанных с маршрутизацией."""
    pass


class RepeatedFlagNameException(FlagError):
    """Повторяющееся имя флага."""
    pass


class TooManyTransferredArgsException(CommandError):
    """Слишком много переданных аргументов."""
    pass


class RequiredArgumentNotPassedException(CommandError):
    """Не передан обязательный аргумент."""
    pass


class IncorrectNumberOfHandlerArgsException(CommandError):
    """Некорректное количество аргументов обработчика."""
    pass


class TriggerCannotContainSpacesException(CommandError):
    """Триггер не может содержать пробелы."""
    pass


class InvalidRouterInstanceException(RouterError):
    """Некорректный экземпляр маршрутизатора."""
    pass


class InvalidDescriptionMessagePatternException(ArgentaError):
    """Некорректный шаблон сообщения описания."""
    pass


class NoRegisteredRoutersException(RouterError):
    """Нет зарегистрированных маршрутизаторов."""
    pass


class NoRegisteredHandlersException(RouterError):
    """Нет зарегистрированных обработчиков."""
    pass

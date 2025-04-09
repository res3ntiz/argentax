"""
Модуль для работы с плагинами в ArgentaX.

Этот модуль содержит базовые классы для создания и управления плагинами.
"""

from typing import Any, Dict, List, Optional, Type


class Plugin:
    """Базовый класс для плагинов."""
    
    def __init__(self, name: str, description: str = None):
        """Инициализация плагина.
        
        Args:
            name: Название плагина
            description: Описание плагина
        """
        self.name = name
        self.description = description
        self.app = None
    
    def initialize(self, app: Any) -> None:
        """Инициализирует плагин.
        
        Args:
            app: Экземпляр приложения
        """
        self.app = app
    
    def cleanup(self) -> None:
        """Освобождает ресурсы плагина."""
        pass


class HistoryPlugin(Plugin):
    """Плагин для сохранения истории команд."""
    
    def __init__(self, max_history: int = 100):
        """Инициализация плагина истории.
        
        Args:
            max_history: Максимальное количество сохраняемых команд
        """
        super().__init__(name="History", description="Сохраняет историю команд")
        self.max_history = max_history
        self.history = []
    
    def initialize(self, app: Any) -> None:
        """Инициализирует плагин.
        
        Args:
            app: Экземпляр приложения
        """
        super().initialize(app)
        
        # Оборачиваем метод execute приложения для сохранения истории
        original_execute = app.execute
        
        def execute_with_history(command_line: str) -> Any:
            # Добавляем команду в историю
            self.add_to_history(command_line)
            # Вызываем оригинальный метод
            return original_execute(command_line)
        
        # Заменяем метод execute
        app.execute = execute_with_history
    
    def add_to_history(self, command_line: str) -> None:
        """Добавляет команду в историю.
        
        Args:
            command_line: Строка команды
        """
        # Не добавляем пустые строки и дубликаты
        if command_line.strip() and (not self.history or self.history[-1] != command_line):
            self.history.append(command_line)
            # Ограничиваем размер истории
            if len(self.history) > self.max_history:
                self.history.pop(0)
    
    def get_history(self) -> List[str]:
        """Возвращает историю команд.
        
        Returns:
            Список строк команд
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Очищает историю команд."""
        self.history.clear()


class AutocompletePlugin(Plugin):
    """Плагин для автодополнения команд."""
    
    def __init__(self):
        """Инициализация плагина автодополнения."""
        super().__init__(name="Autocomplete", description="Обеспечивает автодополнение команд")
    
    def initialize(self, app: Any) -> None:
        """Инициализирует плагин.
        
        Args:
            app: Экземпляр приложения
        """
        super().initialize(app)
        
        # Здесь можно добавить логику для настройки автодополнения
        # Например, с использованием библиотеки readline
        try:
            import readline
            
            def completer(text, state):
                # Получаем все команды
                commands = [cmd.name for cmd in app.router.get_all_commands()]
                
                # Фильтруем команды, начинающиеся с введенного текста
                matches = [cmd for cmd in commands if cmd.startswith(text)]
                
                # Возвращаем соответствующую команду или None, если нет совпадений
                return matches[state] if state < len(matches) else None
            
            # Устанавливаем функцию автодополнения
            readline.set_completer(completer)
            readline.parse_and_bind("tab: complete")
        
        except ImportError:
            # readline не доступен, пропускаем настройку автодополнения
            pass

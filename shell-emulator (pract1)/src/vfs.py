"""Виртуальная файловая система, целиком хранящаяся в памяти."""

from src.errors import VFSError

ROOT_NAME = ""
NO_SUCH_FILE = "No such file or directory"
NOT_A_DIRECTORY = "Not a directory"


class Node:
    """Узел VFS: файл (с содержимым в байтах) или папка."""

    def __init__(self, name, is_dir, data=b""):
        """Создаёт узел; у папки есть словарь потомков children."""
        self.name = name
        self.is_dir = is_dir
        self.data = data
        self.children = {}

    @property
    def size(self):
        """Размер в байтах: для папки — сумма размеров содержимого."""
        if not self.is_dir:
            return len(self.data)
        return sum(child.size for child in self.children.values())

    def descendants(self):
        """Возвращает число узлов внутри поддерева без самого узла."""
        return sum(1 + c.descendants() for c in self.children.values())

    def clone(self, name):
        """Возвращает глубокую копию узла под новым именем."""
        copy = Node(name, self.is_dir, self.data)
        for key, child in self.children.items():
            copy.children[key] = child.clone(child.name)
        return copy


class VFS:
    """Дерево узлов с текущей папкой (cwd)."""

    def __init__(self):
        """Создаёт пустую VFS: только корневая папка."""
        self.root = Node(ROOT_NAME, True)
        self.cwd = []

    def normalize(self, path):
        """Превращает путь в список имён от корня.

        Относительные пути считаются от текущей папки, элементы «.» и
        «..» обрабатываются, выше корня подняться нельзя.
        """
        parts = [] if path.startswith("/") else list(self.cwd)
        for part in path.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part not in ("", "."):
                parts.append(part)
        return parts

    def lookup(self, parts):
        """Находит узел по списку имён. Бросает VFSError, если его нет."""
        node = self.root
        for part in parts:
            if not node.is_dir:
                raise VFSError(NOT_A_DIRECTORY)
            child = node.children.get(part)
            if child is None:
                raise VFSError(NO_SUCH_FILE)
            node = child
        return node

    def get(self, path):
        """Возвращает узел по пути; сообщение об ошибке содержит путь."""
        try:
            return self.lookup(self.normalize(path))
        except VFSError as error:
            raise VFSError(f"{path}: {error}") from error

    def get_dir(self, path):
        """Возвращает папку по пути или бросает VFSError."""
        node = self.get(path)
        if not node.is_dir:
            raise VFSError(f"{path}: {NOT_A_DIRECTORY}")
        return node

    def pwd(self):
        """Возвращает путь текущей папки."""
        return "/" + "/".join(self.cwd)

    def change_dir(self, path):
        """Делает папку по пути текущей."""
        self.get_dir(path)
        self.cwd = self.normalize(path)

    def add(self, parts, node):
        """Добавляет узел по пути parts; родитель должен существовать."""
        parent = self.lookup(parts[:-1])
        if not parent.is_dir:
            raise VFSError(NOT_A_DIRECTORY)
        if node.name in parent.children:
            raise VFSError("File exists")
        parent.children[node.name] = node

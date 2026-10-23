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


def place(parent, name, node):
    """Помещает копию node в parent под именем name, как это делает cp.

    Файл перезаписывает файл, папка сливается с существующей папкой.
    Бросает VFSError, если папку нужно заменить файлом или наоборот.
    """
    existing = parent.children.get(name)
    if existing is None:
        parent.children[name] = node.clone(name)
    elif existing.is_dir and node.is_dir:
        for child in node.children.values():
            place(existing, child.name, child)
    elif existing.is_dir:
        raise VFSError(f"cannot overwrite directory '{name}' with file")
    elif node.is_dir:
        raise VFSError(f"cannot overwrite file '{name}' with directory")
    else:
        parent.children[name] = node.clone(name)


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

    def exists(self, parts):
        """Проверяет, существует ли узел по списку имён."""
        try:
            self.lookup(parts)
        except VFSError:
            return False
        return True

    def is_dir(self, path):
        """Проверяет, что по пути находится существующая папка."""
        parts = self.normalize(path)
        return self.exists(parts) and self.lookup(parts).is_dir

    def dir_at(self, parts, path):
        """Возвращает существующую папку; сообщения об ошибках с путём."""
        try:
            node = self.lookup(parts)
        except VFSError as error:
            raise VFSError(f"{path}: {error}") from error
        if not node.is_dir:
            raise VFSError(f"{path}: {NOT_A_DIRECTORY}")
        return node

    def make_chain(self, parts, path):
        """Создаёт папку со всеми недостающими родителями (mkdir -p)."""
        node = self.root
        for part in parts:
            child = node.children.get(part)
            if child is None:
                child = Node(part, True)
                node.children[part] = child
            elif not child.is_dir:
                raise VFSError(f"{path}: {NOT_A_DIRECTORY}")
            node = child

    def make_dir(self, path, parents=False):
        """Создаёт папку; с parents=True создаёт и недостающих родителей."""
        parts = self.normalize(path)
        if parents:
            self.make_chain(parts, path)
            return
        if self.exists(parts):
            raise VFSError(f"{path}: File exists")
        parent = self.dir_at(parts[:-1], path)
        parent.children[parts[-1]] = Node(parts[-1], True)

    def copy_target(self, src_parts, dest):
        """Возвращает путь копии: внутрь папки dest или под именем dest."""
        dest_parts = self.normalize(dest)
        if self.is_dir(dest):
            return dest_parts + [src_parts[-1]]
        return dest_parts

    def copy(self, source, dest, recursive=False):
        """Копирует файл или (с recursive=True) папку, как команда cp.

        Если dest — существующая папка, копия кладётся внутрь неё.
        """
        node = self.get(source)
        if node.is_dir and not recursive:
            raise VFSError(f"{source}: -r not specified; omitting directory")
        src_parts = self.normalize(source)
        if not src_parts:
            raise VFSError(f"{source}: cannot copy a directory into itself")
        target = self.copy_target(src_parts, dest)
        if target == src_parts:
            raise VFSError(f"'{source}' and '{dest}' are the same file")
        if node.is_dir and target[: len(src_parts)] == src_parts:
            raise VFSError(f"{dest}: cannot copy a directory into itself")
        parent = self.dir_at(target[:-1], dest)
        try:
            place(parent, target[-1], node)
        except VFSError as error:
            raise VFSError(f"{dest}: {error}") from error

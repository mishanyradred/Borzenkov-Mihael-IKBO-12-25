"""Тесты виртуальной файловой системы."""

import unittest

from src.errors import VFSError
from src.vfs import VFS, Node


def make_vfs():
    """Создаёт VFS: /dir/file.txt (5 байт) и /top.txt (3 байта)."""
    vfs = VFS()
    vfs.add(["dir"], Node("dir", True))
    vfs.add(["dir", "file.txt"], Node("file.txt", False, b"hello"))
    vfs.add(["top.txt"], Node("top.txt", False, b"abc"))
    return vfs


class NodeTests(unittest.TestCase):
    """Проверки класса Node."""

    def test_file_size(self):
        """Размер файла равен длине содержимого."""
        self.assertEqual(Node("a", False, b"1234").size, 4)

    def test_dir_size_is_sum(self):
        """Размер папки — сумма размеров вложенных узлов."""
        self.assertEqual(make_vfs().root.size, 8)

    def test_descendants(self):
        """descendants считает узлы без корня."""
        self.assertEqual(make_vfs().root.descendants(), 3)

    def test_clone_is_deep(self):
        """Копия не зависит от оригинала."""
        root = make_vfs().root
        copy = root.clone("copy")
        copy.children["dir"].children.clear()
        self.assertEqual(root.size, 8)
        self.assertEqual(copy.name, "copy")


class PathTests(unittest.TestCase):
    """Проверки разбора путей."""

    def test_absolute_path(self):
        """Абсолютный путь не зависит от текущей папки."""
        vfs = make_vfs()
        vfs.cwd = ["dir"]
        self.assertEqual(vfs.normalize("/top.txt"), ["top.txt"])

    def test_relative_path(self):
        """Относительный путь считается от текущей папки."""
        vfs = make_vfs()
        vfs.cwd = ["dir"]
        self.assertEqual(vfs.normalize("file.txt"), ["dir", "file.txt"])

    def test_dots(self):
        """Элементы «.» и «..» обрабатываются."""
        vfs = make_vfs()
        self.assertEqual(vfs.normalize("/dir/./../top.txt"), ["top.txt"])

    def test_cannot_go_above_root(self):
        """Выше корня подняться нельзя."""
        self.assertEqual(make_vfs().normalize("../../.."), [])


class LookupTests(unittest.TestCase):
    """Проверки поиска узлов и смены папки."""

    def test_get_file(self):
        """get находит файл по пути."""
        self.assertEqual(make_vfs().get("/dir/file.txt").data, b"hello")

    def test_get_missing(self):
        """Отсутствующий узел вызывает VFSError с путём."""
        with self.assertRaises(VFSError) as context:
            make_vfs().get("/nope")
        self.assertIn("/nope", str(context.exception))

    def test_through_file(self):
        """Путь через файл вызывает VFSError."""
        with self.assertRaises(VFSError):
            make_vfs().get("/top.txt/x")

    def test_get_dir_on_file(self):
        """get_dir на файле вызывает VFSError."""
        with self.assertRaises(VFSError):
            make_vfs().get_dir("/top.txt")

    def test_change_dir(self):
        """change_dir меняет текущую папку и pwd."""
        vfs = make_vfs()
        vfs.change_dir("dir")
        self.assertEqual(vfs.pwd(), "/dir")
        vfs.change_dir("..")
        self.assertEqual(vfs.pwd(), "/")

    def test_change_dir_failure_keeps_cwd(self):
        """Неудачный cd не меняет текущую папку."""
        vfs = make_vfs()
        with self.assertRaises(VFSError):
            vfs.change_dir("/top.txt")
        self.assertEqual(vfs.pwd(), "/")


class AddTests(unittest.TestCase):
    """Проверки добавления узлов."""

    def test_add_duplicate(self):
        """Повторное добавление вызывает VFSError."""
        with self.assertRaises(VFSError):
            make_vfs().add(["top.txt"], Node("top.txt", False))

    def test_add_without_parent(self):
        """Добавление без родителя вызывает VFSError."""
        with self.assertRaises(VFSError):
            make_vfs().add(["no", "x"], Node("x", False))

    def test_add_into_file(self):
        """Добавление внутрь файла вызывает VFSError."""
        with self.assertRaises(VFSError):
            make_vfs().add(["top.txt", "x"], Node("x", False))


if __name__ == "__main__":
    unittest.main()

"""Тесты загрузки VFS из CSV."""

import os
import tempfile
import unittest

from src.errors import VFSError
from src.vfs_loader import load_vfs
from tests.helpers import VFS_DIR


def sample(name):
    """Возвращает путь к файлу VFS из папки vfs."""
    return os.path.join(VFS_DIR, name)


class LoadSampleTests(unittest.TestCase):
    """Проверки загрузки готовых образцов."""

    def test_minimal(self):
        """Минимальная VFS содержит только корень."""
        self.assertEqual(load_vfs(sample("minimal.csv")).root.descendants(), 0)

    def test_several_files(self):
        """В VFS с несколькими файлами читается содержимое."""
        vfs = load_vfs(sample("files.csv"))
        self.assertEqual(vfs.get("/a.txt").data, b"first file\n")
        self.assertEqual(vfs.get("/docs/c.txt").data, b"third\n")

    def test_deep_levels(self):
        """В глубокой VFS не менее трёх уровней вложенности."""
        vfs = load_vfs(sample("deep.csv"))
        node = vfs.get("/home/user/docs/work/report.txt")
        self.assertFalse(node.is_dir)

    def test_binary_content(self):
        """Двоичные данные восстанавливаются из base64."""
        vfs = load_vfs(sample("deep.csv"))
        node = vfs.get("/bin/tool.bin")
        self.assertEqual(node.data, b"\xff\xfe\x00\x01\x80")


class LoadErrorTests(unittest.TestCase):
    """Проверки сообщений об ошибках загрузки."""

    def assert_error(self, path, text):
        """Проверяет, что загрузка падает с VFSError, содержащей text."""
        with self.assertRaises(VFSError) as context:
            load_vfs(path)
        self.assertIn(text, str(context.exception))

    def test_missing_file(self):
        """Отсутствующий файл."""
        self.assert_error(sample("no_such.csv"), "No such file")

    def test_bad_header(self):
        """Неверный заголовок."""
        self.assert_error(sample("invalid/bad_header.csv"), "header")

    def test_bad_type(self):
        """Неизвестный тип узла."""
        self.assert_error(sample("invalid/bad_type.csv"), "unknown type")

    def test_no_parent(self):
        """Нет родительской папки."""
        self.assert_error(sample("invalid/no_parent.csv"), "line 3")

    def test_bad_base64(self):
        """Неверный base64."""
        self.assert_error(sample("invalid/bad_base64.csv"), "base64")

    def test_bad_columns(self):
        """Неверное число колонок."""
        self.assert_error(sample("invalid/bad_columns.csv"), "columns")

    def test_not_utf8(self):
        """Файл не в кодировке UTF-8."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "x.csv")
            with open(path, "wb") as file:
                file.write(b"\xff\xfe\x00\x80")
            self.assert_error(path, "UTF-8")

    def test_any_order(self):
        """Порядок строк в файле не важен."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "x.csv")
            with open(path, "w", encoding="utf-8") as file:
                file.write("path,type,content\n/a/b,dir,\n/a,dir,\n")
            self.assertEqual(load_vfs(path).get("/a/b").is_dir, True)


if __name__ == "__main__":
    unittest.main()

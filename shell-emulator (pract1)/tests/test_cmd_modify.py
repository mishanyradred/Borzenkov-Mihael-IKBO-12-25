"""Тесты команд mkdir и cp, изменяющих VFS в памяти."""

import unittest

from src.errors import CommandError
from tests.helpers import deep_vfs, run

HOSTS = b"127.0.0.1 localhost\n"


class MkdirTests(unittest.TestCase):
    """Проверки команды mkdir."""

    def setUp(self):
        """Загружает образец VFS."""
        self.vfs = deep_vfs()

    def test_create(self):
        """mkdir создаёт папку, видимую в ls."""
        run(self.vfs, "mkdir /tmp/new")
        self.assertEqual(run(self.vfs, "ls /tmp"), "new")
        self.assertTrue(self.vfs.get("/tmp/new").is_dir)

    def test_relative(self):
        """Относительный путь считается от текущей папки."""
        run(self.vfs, "cd /tmp")
        run(self.vfs, "mkdir sub")
        self.assertTrue(self.vfs.is_dir("/tmp/sub"))

    def test_several(self):
        """Можно создать несколько папок сразу."""
        run(self.vfs, "mkdir /tmp/a /tmp/b")
        self.assertEqual(run(self.vfs, "ls /tmp"), "a\nb")

    def test_parents(self):
        """-p создаёт цепочку папок."""
        run(self.vfs, "mkdir -p /tmp/a/b/c")
        self.assertTrue(self.vfs.is_dir("/tmp/a/b/c"))

    def test_parents_existing(self):
        """-p не считает ошибкой существующую папку."""
        run(self.vfs, "mkdir -p /home/user")
        self.assertTrue(self.vfs.is_dir("/home/user"))

    def test_exists(self):
        """Существующая папка без -p вызывает ошибку."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "mkdir /home")
        self.assertIn("File exists", str(context.exception))

    def test_missing_parent(self):
        """Без -p нет папки-родителя вызывает ошибку."""
        with self.assertRaises(CommandError):
            run(self.vfs, "mkdir /nope/x")

    def test_parent_is_file(self):
        """Файл в качестве родителя вызывает ошибку."""
        with self.assertRaises(CommandError):
            run(self.vfs, "mkdir /etc/hosts/x")
        with self.assertRaises(CommandError):
            run(self.vfs, "mkdir -p /etc/hosts/x")

    def test_missing_operand(self):
        """Без аргументов команда завершается ошибкой."""
        with self.assertRaises(CommandError):
            run(self.vfs, "mkdir")


class CpFileTests(unittest.TestCase):
    """Проверки cp для файлов."""

    def setUp(self):
        """Загружает образец VFS."""
        self.vfs = deep_vfs()

    def test_new_name(self):
        """Файл копируется под новым именем."""
        run(self.vfs, "cp /etc/hosts /etc/hosts2")
        self.assertEqual(self.vfs.get("/etc/hosts2").data, HOSTS)
        self.assertEqual(self.vfs.get("/etc/hosts").data, HOSTS)

    def test_into_directory(self):
        """Файл копируется внутрь существующей папки."""
        run(self.vfs, "cp /etc/hosts /tmp")
        self.assertEqual(self.vfs.get("/tmp/hosts").data, HOSTS)

    def test_overwrite(self):
        """Существующий файл перезаписывается."""
        run(self.vfs, "cp /etc/hosts /home/user/notes.txt")
        self.assertEqual(self.vfs.get("/home/user/notes.txt").data, HOSTS)

    def test_copy_is_independent(self):
        """Копия не связана с оригиналом."""
        run(self.vfs, "cp /etc/hosts /tmp/h")
        self.vfs.get("/tmp/h").data = b"changed"
        self.assertEqual(self.vfs.get("/etc/hosts").data, HOSTS)

    def test_several_sources(self):
        """Несколько файлов копируются в папку."""
        run(self.vfs, "cp /etc/hosts /home/user/notes.txt /tmp")
        self.assertEqual(run(self.vfs, "ls /tmp"), "hosts\nnotes.txt")

    def test_several_sources_to_file(self):
        """Несколько источников и назначение-файл вызывают ошибку."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "cp /etc/hosts /bin/tool.bin /etc/hosts")
        self.assertIn("not a directory", str(context.exception))

    def test_same_file(self):
        """Копирование файла на себя вызывает ошибку."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "cp /etc/hosts /etc/hosts")
        self.assertIn("same file", str(context.exception))
        with self.assertRaises(CommandError):
            run(self.vfs, "cp /etc/hosts /etc")

    def test_errors(self):
        """Ошибки аргументов и путей."""
        for line in ("cp", "cp /etc/hosts", "cp /nope /tmp",
                     "cp /etc/hosts /nope/x", "cp -z a b"):
            with self.assertRaises(CommandError, msg=line):
                run(self.vfs, line)


class CpDirectoryTests(unittest.TestCase):
    """Проверки cp -r для папок."""

    def setUp(self):
        """Загружает образец VFS."""
        self.vfs = deep_vfs()

    def test_needs_recursive(self):
        """Папка без -r вызывает ошибку."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "cp /home/user/docs /tmp/docs")
        self.assertIn("-r", str(context.exception))

    def test_recursive_new_name(self):
        """cp -r копирует всё дерево под новым именем."""
        run(self.vfs, "cp -r /home/user/docs /tmp/docs2")
        self.assertEqual(
            self.vfs.get("/tmp/docs2/work/report.txt").size,
            self.vfs.get("/home/user/docs/work/report.txt").size,
        )

    def test_recursive_into_directory(self):
        """Папка копируется внутрь существующей папки."""
        run(self.vfs, "cp -r /home/user/docs /tmp")
        self.assertTrue(self.vfs.is_dir("/tmp/docs/work"))

    def test_merge(self):
        """Повторное копирование сливает папки без ошибки."""
        run(self.vfs, "cp -r /home/user/docs /tmp")
        run(self.vfs, "cp -r /home/user/docs /tmp")
        self.assertEqual(
            run(self.vfs, "ls /tmp/docs"), "empty.txt\nreadme.txt\nwork"
        )

    def test_into_itself(self):
        """Копирование папки внутрь себя вызывает ошибку."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "cp -r /home/user /home/user/docs")
        self.assertIn("into itself", str(context.exception))

    def test_root(self):
        """Корень скопировать нельзя."""
        with self.assertRaises(CommandError):
            run(self.vfs, "cp -r / /tmp")

    def test_dir_over_file(self):
        """Папку нельзя записать поверх файла."""
        with self.assertRaises(CommandError) as context:
            run(self.vfs, "cp -r /home/user/docs /etc/hosts")
        self.assertIn("overwrite", str(context.exception))

    def test_file_over_dir(self):
        """Файл нельзя записать поверх папки с тем же именем."""
        run(self.vfs, "mkdir /tmp/hosts")
        with self.assertRaises(CommandError):
            run(self.vfs, "cp /etc/hosts /tmp")


if __name__ == "__main__":
    unittest.main()

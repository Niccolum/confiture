from dature.source_locators.toml_ import TomlPathFinder


class TestTomlMultiline:
    def test_key_after_multiline_double_quotes(self):
        content = 'str1 = """\nx=1\nViolets are blue"""\nx = 1\n'
        finder = TomlPathFinder(content)

        assert finder.find_line(["x"]) == 4

    def test_key_inside_multiline_not_matched_as_real_key(self):
        content = 'str1 = """\nhost = localhost\n"""\nhost = production\n'
        finder = TomlPathFinder(content)

        assert finder.find_line(["host"]) == 4

    def test_key_after_multiline_single_quotes(self):
        content = "str1 = '''\nport = 8080\n'''\nport = 3000\n"
        finder = TomlPathFinder(content)

        assert finder.find_line(["port"]) == 4

    def test_key_only_inside_multiline_returns_not_found(self):
        content = 'str1 = """\nx = 1\n"""\n'
        finder = TomlPathFinder(content)

        assert finder.find_line(["x"]) == -1

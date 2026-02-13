from dature.source_locators.ini_ import TablePathFinder


class TestIniMultiline:
    def test_key_not_confused_by_continuation_line(self):
        content = "[section]\nstr1 = line1\n  x = 1\nx = real\n"
        finder = TablePathFinder(content)

        assert finder.find_line(["section", "x"]) == 4

    def test_key_with_colon_separator(self):
        content = "[app]\nstr1: line1\n  host: fake\nhost: production\n"
        finder = TablePathFinder(content)

        assert finder.find_line(["app", "host"]) == 4

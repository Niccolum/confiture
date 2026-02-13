from dature.source_locators.yaml_ import YamlPathFinder


class TestYamlMultiline:
    def test_key_after_literal_block(self):
        content = "str1: |\n  x: 1\n  Violets are blue\nx: 1\n"
        finder = YamlPathFinder(content)

        assert finder.find_line(["x"]) == 4

    def test_key_after_folded_block(self):
        content = "str1: >\n  host: localhost\n  more text\nhost: production\n"
        finder = YamlPathFinder(content)

        assert finder.find_line(["host"]) == 4

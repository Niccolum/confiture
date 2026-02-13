from dature.source_locators.json5_ import Json5PathFinder


class TestJson5Multiline:
    def test_key_not_confused_by_newline_in_value(self):
        content = "{\n  str1: 'line1\\nkey=1',\n  key: 'real'\n}"
        finder = Json5PathFinder(content)

        assert finder.find_line(["key"]) == 3

    def test_key_not_confused_by_escaped_quotes(self):
        content = '{\n  str1: "he said \\"key\\": value",\n  key: 42\n}'
        finder = Json5PathFinder(content)

        assert finder.find_line(["key"]) == 3

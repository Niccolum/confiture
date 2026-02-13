from dature.source_locators.json_ import JsonPathFinder


class TestJsonMultiline:
    def test_key_not_confused_by_newline_in_value(self):
        content = '{\n  "str1": "line1\\nkey=1",\n  "key": "real"\n}'
        finder = JsonPathFinder(content)

        assert finder.find_line(["key"]) == 3

    def test_key_not_confused_by_escaped_quotes(self):
        content = '{\n  "str1": "he said \\"key\\": value",\n  "key": 42\n}'
        finder = JsonPathFinder(content)

        assert finder.find_line(["key"]) == 3

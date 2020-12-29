#!/usr/bin/env python3
import json
import textwrap
import unittest
import re
import io
import jsongrep


class SingleDictTest(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO(textwrap.dedent("""\
            {
                "foo": 123,
                "bar": 456
            }
            """))

    def testSearchKey(self):
        self.assertDictEqual(
            {"foo": 123}, jsongrep.search_stream(re.compile("foo"), self.stream))

    def testSearchValue(self):
        self.assertDictEqual(
            {"foo": 123}, jsongrep.search_stream(re.compile("123"), self.stream))

    def testMatchNothing(self):
        self.assertIsNone(
            jsongrep.search_stream(re.compile("abc"), self.stream))


class SingleArrayTest(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO(textwrap.dedent("""\
            ["abc", 123, "abc123"]
            """))

    def testSearchString(self):
        self.assertListEqual(
            ["abc", "abc123"], jsongrep.search_stream(re.compile("abc"), self.stream))

    def testSearchInteger(self):
        self.assertListEqual(
            [123, "abc123"], jsongrep.search_stream(re.compile("123"), self.stream))


class AtomicTest(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO("1234")

    def testSearchMatch(self):
        self.assertEqual(1234, jsongrep.search_stream(
            re.compile("123"), self.stream))

    def testSearchNoMatch(self):
        self.assertIsNone(jsongrep.search_stream(
            re.compile("abc"), self.stream))


class DropExtraFieldsTest(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO(textwrap.dedent("""\
            {
                "key1": "blah",
                "key2": {
                    "a": [1, 2, 3],
                    "b": [456, 123]
                },
                "key3": [1, 2, 3],
                "key4": {
                    "foo": "bar"
                }   
            }
            """))

    def testDropKeysAndArrays(self):
        self.assertDictEqual({"key2": {"b": [123]}}, jsongrep.search_stream(
            re.compile("123"), self.stream))


if __name__ == "__main__":
    unittest.main()

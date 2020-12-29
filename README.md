# jsongrep

Searches json for matching keys and values.

Examples:
```
$ cat abc.json
{
  "foo": 123,
  "bar": "100",
  "baz": 200
}

$ jsongrep.py foo abc.json
{
  "foo": 123
}

$ jsongrep.py 1 abc.json
{
  "foo": 123,
  "bar": "100",
}

$ cat abc.json | jsongrep.py 200
{
  "baz": 200
}
```

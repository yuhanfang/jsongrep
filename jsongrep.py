#!/usr/bin/env python3
"""Prints the subset of a json file matching the regular expression.

Prints nothing if there is no match and returns a nonzero exit code.

Example:

    # Both examples search file.json for the given regular expression.
    jsongrep.py myregex file.json
    cat file.json | jsongrep.py myregex
"""
import argparse
import json
import os
import re
import sys


def walk_json(expr, root):
    """Walks a json tree in two passes. In the first pass, prune elements from
    the tree to shrink down to matches. In the second pass, delete containers
    that hold no matches.
    """
    any_match = [False]
    nodes = [(root, [])]
    keep = set()

    def _flag_match(node, parents):
        """Flags a node and its parents as matching the target expression."""
        any_match[0] = True
        keep.add(id(node))
        for n in parents:
            keep.add(id(n))

    def _process_element(node, key, value, parents, to_delete):
        """Process an element of a dict or a list. Flags matches, lack of match
        on an atomic type, or need for further processing.
        """
        is_object = isinstance(value, (list, dict))
        if (not is_object) and expr.search(str(value)):
            _flag_match(node, parents)
        elif not is_object:
            to_delete.append(key)
        else:
            nodes.append((value, parents + [node]))

    while nodes:
        node, parents = nodes.pop()
        if isinstance(node, dict):
            to_delete = []
            for key, value in node.items():
                if expr.search(key):
                    _flag_match(node, parents)
                else:
                    _process_element(node, key, value, parents, to_delete)
            for index in to_delete:
                del node[index]
        elif isinstance(node, list):
            to_delete = []
            for key, value in enumerate(node):
                _process_element(node, key, value, parents, to_delete)
            for index in sorted(to_delete, reverse=True):
                del node[index]
        else:
            any_match[0] = expr.search(str(node))

    nodes = [root]

    def _filter_element(node, key, value, to_delete):
        """Adds nodes to the deletion list as needed."""
        if isinstance(value, (list, dict)):
            if id(value) not in keep:
                to_delete.append(key)
            else:
                nodes.append(value)

    while nodes:
        node = nodes.pop()
        if isinstance(node, dict):
            to_delete = []
            for key, value in node.items():
                _filter_element(node, key, value, to_delete)
            for key in to_delete:
                del node[key]
        elif isinstance(node, list):
            to_delete = []
            for key, value in enumerate(node):
                _filter_element(node, key, value, to_delete)
            for key in sorted(to_delete, reverse=True):
                del node[key]

    return any_match[0]


def search_stream(expression, stream):
    """Searches a stream for a regular expression and returns the matching
    subset. Returns None if there is no match.
    """
    expr = re.compile(expression)
    obj = json.load(stream)
    matched = walk_json(expr, obj)
    return obj if matched else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("expression", type=str,
                        help="Regular expression to match keys and values")
    parser.add_argument("filename", type=str, nargs="?", help="File to search")
    args = parser.parse_args()
    if not args.filename:
        match = search_stream(args.expression, sys.stdin)
    else:
        with open(args.filename, "r") as stream:
            match = search_stream(args.expression, stream)
    if match:
        print(json.dumps(match, indent=2))
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()

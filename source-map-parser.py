import json
import os
import requests

from argparse import ArgumentParser
from dataclasses import dataclass
from json import JSONDecodeError
from requests.exceptions import MissingSchema, ConnectionError


@dataclass
class SourceMap:
    version: int
    sources: str
    sources_content: str


def read_local_resource(path):
    try:
        with open(path, "r", encoding="utf-8") as input_file:
            return json.load(input_file)

    except (FileNotFoundError, JSONDecodeError) as e:
        if e.__class__.__name__ == "FileNotFoundError":
            exit(f"[{path}] Provided JSON path doesn't exist, check and try again")

        elif e.__class__.__name__ == "JSONDecodeError":
            exit(
                f"[{path}] Provided JSON has not been parsed as valid JSON, check and try again"
            )


def read_remote_resource(path):
    try:
        return requests.get(path).json()

    except (ConnectionError, JSONDecodeError, MissingSchemaError) as e:
        if e.__class__.__name__ == "ConnectionError":
            exit(f"[{path}] Error connecting to remote resource")

        elif e.__class__.__name__ == "JSONDecodeError":
            exit(
                f"[{path}] Provided JSON has not been parsed as valid JSON, check and try again"
            )

        elif e.__class__.__name__ == "MissingSchemaError":
            exit(
                f"[{path}] Provided URL is missing a schema, add a schema and try again"
            )


def verify_source_map(source_map):
    keys = ["version", "sources", "sourcesContent"]
    return all([key in source_map for key in keys])


def make_clean_path(path):
    invalid = '^*":<>|?'

    path = path.replace(" ^\.\/.*$", ".js")

    for character in invalid:
        path = path.replace(character, "")

    return path


def parse(parse_type, resource, destination_folder, write_data):
    print(f"[{resource}] Parsing {parse_type} resource")

    if parse_type == "local":
        source_map = read_local_resource(resource)

    elif parse_type == "remote":
        source_map = read_remote_resource(resource)

    else:
        exit(f"[{resource}] Must provide either a local or remote parse type")

    if verify_source_map(source_map):
        source_map = SourceMap(
            version=int(source_map["version"]),
            sources=source_map["sources"],
            sources_content=source_map["sourcesContent"],
        )
        print(
            f"[{resource}] Version {source_map.version} source map with {len(source_map.sources)} sources"
        )

        for index, path in enumerate(source_map.sources):
            if path.startswith("../") or path.startswith("..\\"):
                path = path[3:]

            path = make_clean_path(path)
            clean_path = os.path.join(destination_folder, os.path.normpath(path))
            directory = os.path.dirname(clean_path)

            if not os.path.exists(directory) and write_data:
                os.makedirs(directory)

            try:
                if write_data:
                    with open(clean_path, "wb") as source_file:
                        source_file.write(
                            source_map.sources_content[index].encode("utf-8")
                        )

                print(f"[{resource}] File found: {clean_path}")

            except Exception as e:
                print(e)
                exit(f"[{resource}] Error extracting file {path}")

    else:
        print(f"[{resource}] Error verifying source map")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-f", "--file", help="The location of a local source map to parse", type=str
    )
    parser.add_argument(
        "-u", "--url", help="The URL of a remote source map to parse", type=str
    )
    parser.add_argument(
        "-d", "--destination", help="Destination folder to output to", type=str
    )

    parser.add_argument(
        "-n",
        "--no-output",
        help="Only print found source files and write nothing to disk",
        action="store_false",
    )

    args = parser.parse_args()

    if not args.file and not args.url:
        exit("Must provide either a URL or local source map to parse")

    if args.file and args.url:
        exit("Must only provide one source map to parse")

    if not args.destination:
        exit("Must provide a destination directory for source files")

    parse(
        "local" if args.file else "remote",
        args.file if args.file else args.url,
        args.destination,
        args.no_output,
    )


if __name__ == "__main__":
    parse_args()

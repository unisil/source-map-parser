# Source Map Parser

A simple command line Python script to parse JavaScript source maps and extract original source files. Can be used to parse and retrieve from both local and remotely hosted source maps.

## **Usage**

```shell
usage: source-map-parser.py [-h] [-f FILE] [-u URL] [-d DESTINATION] [-n]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  The location of a local source map to parse
  -u URL, --url URL     The URL of a remote source map to parse
  -d DESTINATION, --destination DESTINATION
                        Destination folder to output to
  -n, --no-output       Only print found source files and write nothing to
                        disk
```

Local example

```
.\source-map-parser.py --destination example-folder --file example.js.map
```

Remote example

```
.\source-map-parser.py --destination example-folder --url https://example.localhost/js/example.js.map
```

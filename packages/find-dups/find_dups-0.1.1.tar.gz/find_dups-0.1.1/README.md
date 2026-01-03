# find-dups
> script to find potential duplicate files in a directory tree

**find-dups** scans a directory tree and outputs a simple report on the standard output with potential duplicate files grouped by:
+ files found having the same size and hash.
+ files having the same name (name + extension).
+ files having the same name and different extension.

## Basic usage

```bash
find-dups directory
```

You can find all the options with:

```bash
find-dups -h
```
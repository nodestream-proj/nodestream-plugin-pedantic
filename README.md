# Nodestream pedantic Plugin

This plugin adds a pedantic mode to nodestream. It will check for the following:

- All node types are define using `CamelCase`.
- All node types are singular (e.g. `User` not `Users`).
- All relationship types are defined using `UPPER_SNAKE_CASE`
- All property names are defined using `lower_snake_case`
- All pipeline names are defined using `lower-case-with-dashes`

## Installation

```bash
pip install nodestream-plugin-pedantic
```

## Usage

```
nodestream audit pedantic
```

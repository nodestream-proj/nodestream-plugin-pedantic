# Nodestream pedantic Plugin

This plugin adds a pedantic mode to nodestream. It will check for the following:

- All node types are defined using `CamelCase`.
- All node types are singular (e.g. `User` not `Users`).
- All relationship types are defined using `UPPER_SNAKE_CASE`
- All property names are defined using `lower_snake_case`
- All pipeline names are defined using `lower-case-with-dashes`

## Installation

```bash
pip install nodestream-plugin-pedantic
```

## Usage

```bash
nodestream audit pedantic
```

Will produce output like:

```
Pipeline load_org_chart is not lower dash case. Suggestion: load-org-chart
Node type People is not singular. Suggestion: Person
Property lastName is not snake case. Suggestion: last_name
Node type number is not camel case. Suggestion: Number
Relationship type is_friends_with is not upper camel case. Suggestion: IS_FRIENDS_WITH
```

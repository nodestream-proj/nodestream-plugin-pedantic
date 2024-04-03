import pytest
from nodestream.project.audits import AuditPrinter
from nodestream.schema.state import (
    Adjacency,
    AdjacencyCardinality,
    Cardinality,
    GraphObjectSchema,
    PropertyMetadata,
    PropertyType,
    Schema,
)

from nodestream_plugin_pedantic.audits import (
    PedanticAudit,
    check_camel_case,
    check_lower_dash_case,
    check_singularity,
    check_snake_case,
)


@pytest.fixture
def basic_schema():
    schema = Schema()
    person = GraphObjectSchema(
        name="person",
        properties={
            "nameOfPerson": PropertyMetadata(PropertyType.STRING, is_key=True),
            "age": PropertyMetadata(PropertyType.INTEGER),
        },
    )
    organization = GraphObjectSchema(
        name="Organization",
        properties={
            "name": PropertyMetadata(PropertyType.STRING),
            "industry": PropertyMetadata(PropertyType.STRING),
        },
    )
    best_friend_of = GraphObjectSchema(
        name="best_friend_of",
        properties={
            "since": PropertyMetadata(PropertyType.DATETIME),
        },
    )
    has_employee = GraphObjectSchema(
        name="HAS_EMPLOYEE",
        properties={
            "since": PropertyMetadata(PropertyType.DATETIME),
        },
    )

    schema.put_node_type(person)
    schema.put_node_type(organization)
    schema.put_relationship_type(best_friend_of)
    schema.put_relationship_type(has_employee)

    schema.add_adjacency(
        adjacency=Adjacency("Person", "Person", "BEST_FRIEND_OF"),
        cardinality=AdjacencyCardinality(Cardinality.SINGLE, Cardinality.MANY),
    )
    schema.add_adjacency(
        adjacency=Adjacency("Organization", "Person", "HAS_EMPLOYEE"),
        cardinality=AdjacencyCardinality(Cardinality.MANY, Cardinality.MANY),
    )

    return schema


@pytest.mark.parametrize(
    "input,expected_ok,expected_suggestion",
    [
        ("CamelCase", True, "CamelCase"),
        ("camelCase", False, "CamelCase"),
        ("camel_case", False, "CamelCase"),
        ("something else", False, "SomethingElse"),
        ("something-else", False, "SomethingElse"),
        ("something_else", False, "SomethingElse"),
    ],
)
def test_check_camel_case(input, expected_ok, expected_suggestion):
    is_camel_case, suggestion = check_camel_case(input)
    assert suggestion == expected_suggestion
    assert is_camel_case == expected_ok


@pytest.mark.parametrize(
    "input,expected_ok,expected_suggestion",
    [
        ("lower_snake_case", False, "lower-snake-case"),
        ("something else", False, "something-else"),
        ("something-else", True, "something-else"),
    ],
)
def test_check_lower_dash_case(input, expected_ok, expected_suggestion):
    is_lower_dash_case, suggestion = check_lower_dash_case(input)
    assert suggestion == expected_suggestion
    assert is_lower_dash_case == expected_ok


@pytest.mark.parametrize(
    "input,expected_ok,expected_suggestion",
    [
        ("CamelCase", False, "camel_case"),
        ("camelCase", False, "camel_case"),
        ("camel_case", True, "camel_case"),
        ("something else", False, "something_else"),
        ("something-else", False, "something_else"),
        ("something_else", True, "something_else"),
    ],
)
def test_check_snake_case(input, expected_ok, expected_suggestion):
    is_snake_case, suggestion = check_snake_case(input)
    assert suggestion == expected_suggestion
    assert is_snake_case == expected_ok


@pytest.mark.parametrize(
    "input,expected_ok,expected_suggestion",
    [
        ("CamelCase", False, "CAMEL_CASE"),
        ("camelCase", False, "CAMEL_CASE"),
        ("camel_case", False, "CAMEL_CASE"),
        ("something else", False, "SOMETHING_ELSE"),
        ("something-else", False, "SOMETHING_ELSE"),
        ("something_else", False, "SOMETHING_ELSE"),
        ("UPPER_SNAKE_CASE", True, "UPPER_SNAKE_CASE"),
    ],
)
def test_upper_check_snake_case(input, expected_ok, expected_suggestion):
    is_snake_case, suggestion = check_snake_case(input, upper=True)
    assert suggestion == expected_suggestion
    assert is_snake_case == expected_ok


@pytest.mark.parametrize(
    "input,expected_ok,expected_suggestion",
    [
        ("post", True, "post"),
        ("sheep", True, "sheep"),
        ("posts", False, "post"),
        ("octopi", False, "octopus"),
    ],
)
def test_check_singularity(input, expected_ok, expected_suggestion):
    is_singular, suggestion = check_singularity(input)
    assert suggestion == expected_suggestion
    assert is_singular == expected_ok


def test_pedantic_audit(basic_schema, mocker):
    subject = PedanticAudit(AuditPrinter())
    subject.check_schema(basic_schema)
    assert subject.failed_properties == {"nameOfPerson"}
    assert subject.failed_node_types == {"person"}
    assert subject.failed_relationship_types == {"best_friend_of"}

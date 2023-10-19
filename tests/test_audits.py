import pytest
from nodestream.project.audits import AuditPrinter
from nodestream.schema.schema import (
    Cardinality,
    GraphObjectShape,
    GraphObjectType,
    GraphSchema,
    KnownTypeMarker,
    PresentRelationship,
    PropertyMetadata,
    PropertyMetadataSet,
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
    return GraphSchema(
        [
            GraphObjectShape(
                GraphObjectType.NODE,
                KnownTypeMarker("person"),
                PropertyMetadataSet(
                    {
                        "nameOfPerson": PropertyMetadata("name"),
                        "age": PropertyMetadata("age"),
                    }
                ),
            ),
            GraphObjectShape(
                GraphObjectType.NODE,
                KnownTypeMarker("Organization"),
                PropertyMetadataSet(
                    {
                        "name": PropertyMetadata("name"),
                        "industry": PropertyMetadata("industry"),
                    }
                ),
            ),
            GraphObjectShape(
                GraphObjectType.RELATIONSHIP,
                KnownTypeMarker("best_friend_of"),
                PropertyMetadataSet(
                    {
                        "since": PropertyMetadata("since"),
                    }
                ),
            ),
            GraphObjectShape(
                GraphObjectType.RELATIONSHIP,
                KnownTypeMarker("HAS_EMPLOYEE"),
                PropertyMetadataSet(
                    {
                        "since": PropertyMetadata("since"),
                    }
                ),
            ),
        ],
        [
            PresentRelationship(
                KnownTypeMarker("Person"),
                KnownTypeMarker("Person"),
                KnownTypeMarker("BEST_FRIEND_OF"),
                from_side_cardinality=Cardinality.SINGLE,
                to_side_cardinality=Cardinality.MANY,
            ),
            PresentRelationship(
                KnownTypeMarker("Organization"),
                KnownTypeMarker("Person"),
                KnownTypeMarker("HAS_EMPLOYEE"),
                from_side_cardinality=Cardinality.MANY,
                to_side_cardinality=Cardinality.MANY,
            ),
        ],
    )


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

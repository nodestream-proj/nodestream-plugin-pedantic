from typing import Tuple

from inflection import camelize, dasherize, singularize, underscore
from nodestream.project import PipelineDefinition, Project
from nodestream.project.audits import Audit, AuditPrinter
from nodestream.schema.schema import GraphObjectShape, GraphSchema


def check_camel_case(name: str) -> Tuple[bool, str]:
    sections = name.replace("-", " ").split()
    suggestion = "".join(camelize(section) for section in sections)
    return name == suggestion, suggestion


def check_singularity(name: str) -> Tuple[bool, str]:
    suggestion = singularize(name)
    return name == suggestion, suggestion


def check_lower_dash_case(name: str) -> Tuple[bool, str]:
    sections = name.split()
    suggestion = "-".join(dasherize(section).lower() for section in sections)
    return name == suggestion, suggestion


def check_snake_case(name: str, upper: bool = False) -> Tuple[bool, str]:
    sections = name.split()
    suggestion = "_".join(underscore(section) for section in sections)
    if upper:
        suggestion = suggestion.upper()
    return name == suggestion, suggestion


class PedanticAudit(Audit):
    name = "pedantic"
    description = "Checks for pedantic things about a project"

    def __init__(self, printer: AuditPrinter) -> None:
        super().__init__(printer)
        self.failed_properties = set()
        self.failed_node_types = set()
        self.failed_relationship_types = set()
        self.failed_pipelines = set()

    def fail_property_name(self, name: str, expected: str):
        self.failed_properties.add(name)
        self.failure(f"Property {name} is not snake case. Suggestion: {expected}")

    def fail_node_type(self, name: str, expected: str):
        self.failed_node_types.add(name)
        self.failure(f"Node type {name} is not camel case. Suggestion: {expected}")

    def fail_node_singularity(self, name: str, expected: str):
        self.failed_node_types.add(name)
        self.failure(f"Node type {name} is not singular. Suggestion: {expected}")

    def fail_relationship_type(self, name: str, expected: str):
        self.failed_relationship_types.add(name)
        self.failure(
            f"Relationship type {name} is not upper camel case. Suggestion: {expected}"
        )

    def fail_pipeline_definition(self, name: str, expected: str):
        self.failed_pipelines.add(name)
        self.failure(f"Pipeline {name} is not lower dash case. Suggestion: {expected}")

    def check_property_names(self, shape: GraphObjectShape):
        for prop in shape.properties.properties:
            is_camel_case, suggestion = check_snake_case(prop)
            if not is_camel_case:
                self.fail_property_name(prop, suggestion)

    def check_node_type(self, shape: GraphObjectShape):
        node_type = shape.object_type.type
        is_camel_case, camel_case = check_camel_case(node_type)
        is_singular, singular = check_singularity(node_type)
        if not is_camel_case:
            self.fail_node_type(node_type, camel_case)
        if not is_singular:
            self.fail_node_singularity(node_type, singular)

    def check_relationship_type(self, shape: GraphObjectShape):
        relationship_type = shape.object_type.type
        is_camel_case, suggestion = check_snake_case(relationship_type, upper=True)
        if not is_camel_case:
            self.fail_relationship_type(relationship_type, suggestion)

    def check_pipeline_definition(self, pipeline: PipelineDefinition):
        is_lower_dash_case, suggestion = check_lower_dash_case(pipeline.name)
        if not is_lower_dash_case:
            self.fail_pipeline_definition(pipeline.name, suggestion)

    def check_nodes(self, schema: GraphSchema):
        for shape in schema.known_node_types():
            self.check_node_type(shape)
            self.check_property_names(shape)

    def check_relationships(self, schema: GraphSchema):
        for shape in schema.known_relationship_types():
            self.check_relationship_type(shape)
            self.check_property_names(shape)

    def check_schema(self, schema: GraphSchema):
        self.check_nodes(schema)
        self.check_relationships(schema)

    def check_pipelines(self, project: Project):
        for scope in project.scopes_by_name.values():
            for pipeline in scope.pipelines_by_name.values():
                self.check_pipeline_definition(pipeline)

    async def run(self, project: Project):
        self.check_pipelines(project)
        self.check_schema(project.get_schema())
        if self.failure_count == 0:
            self.success("Project has no pedantic issues")

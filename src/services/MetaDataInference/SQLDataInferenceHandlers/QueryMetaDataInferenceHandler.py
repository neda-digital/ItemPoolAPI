from ..BaseMetaDataInferenceHandler import MetaDataInferenceHandler
from ....models.TaskMaterials.QueryTaskMaterial import QueryTaskMaterial
import inspect
import logging
import json

from sqlglot import parse_one, exp, Expression

logger = logging.getLogger("uvicorn.error")


class QueryMetricsHandler(MetaDataInferenceHandler):
    """
    Currently wraps the SQLGlot-library and uses its parser to calculate basic counting metrics.
    """

    """
    Weight value for all metrics 
    The weight value is actually not used to calculate the final score for the query.
    """
    WEIGHTS = {
        "Join": 0.25,
        "Table": 0.3,
        "Subquery": 0.2,
        "Column": 0.1,
        "Alias": 0.1,
        "Star": 0.1,
        "Literal": 0.1,
        "Identifier": 0.15,
        "Placeholder": 0.15,
        "Value": 0.15
    }

    def __init__(self):
        super().__init__()
        self._analyzer = SQLAnalyzer()

    def infer_metadata(self, query_material: QueryTaskMaterial):
        query = query_material.query
        dialect = query_material.dialect

        exp_classes = {
            class_name: 0
            for class_name, cls in inspect.getmembers(exp, inspect.isclass)
            if issubclass(cls, exp.Expression)
        }

        ast = self._analyzer.parse_query(query, dialect)

        for node in self._analyzer.walk(ast):
            class_name = type(node).__name__
            exp_classes[class_name] += 1

        registered_exp_classes = {e: v for [e, v] in exp_classes.items() if v > 0}

        logger.log(
            msg=json.dumps(registered_exp_classes),
            level=logging.DEBUG,
        )

        return registered_exp_classes


class SQLAnalyzer:
    def parse_query(self, query: str, dialect: str = "postgres"):
        """Parse SQL query and store AST"""
        self._ast = parse_one(query, dialect=dialect)
        return self._ast

    def walk(self, ast: Expression):
        """Walk through all nodes in the AST"""
        if ast is None:
            return []
        return ast.walk()

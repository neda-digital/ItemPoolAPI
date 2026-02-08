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
        
        complexity = self.calculate_weights(registered_exp_classes)
        logger.info(f"Complexity Score: {complexity}")

        return registered_exp_classes
    
    def calculate_score(self, metrics: dict):
        """
        Calculate weighted score for the query based on the metrics and predefined weights
        """
        total_score = 0
        for metric, count in metrics.items():
            weight = self.WEIGHTS.get(metric, 0.05) # Default weight for unregistered metrics
            total_score += weight * count
        total_score = total_score / 10 # Normalize score
        return total_score


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

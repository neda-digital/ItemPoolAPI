from ..BaseMetaDataInferenceHandler import MetaDataInferenceHandler
from ....models.TaskMaterials.QueryTaskMaterial import QueryTaskMaterial
import inspect


from sqlglot import parse_one, Expression, exp
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.annotate_types import annotate_types
from sqlglot.optimizer.scope import (
    build_scope,
    find_all_in_scope,
    traverse_scope,
    Scope,
)
from enum import Enum, auto
from typing import List

class QueryMetricsHandler(MetaDataInferenceHandler):
    """
    Currently wraps the SQLGlot-library and uses its parser to calculate basic counting metrics.
    """

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
        
        for node in self._analyzer.walk():
            class_name = type(node).__name__
            exp_classes[class_name] += 1
        
        return exp_classes

class ScopeType(Enum):
    ROOT = auto()
    SUBQUERY = auto()
    CORRELATED_SUBQUERY = auto()
    DERIVED_TABLE = auto()
    CTE = auto()
    UNION = auto()
    UDTF = auto()
    UNKNOWN = auto()

class SQLAnalyzer:
    def __init__(self):
        self._ast = None
    
    def parse_query(self, query: str, dialect: str = "postgres"):
        """Parse SQL query and store AST"""
        self._ast = parse_one(query, dialect=dialect)
        return self._ast
    
    def walk(self):
        """Walk through all nodes in the AST"""
        if self._ast is None:
            return []
        return self._ast.walk()
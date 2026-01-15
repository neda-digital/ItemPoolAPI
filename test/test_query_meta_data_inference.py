from ..src.services.MetaDataInference.SQLDataInferenceHandlers.QueryMetaDataInferenceHandler import (
    QueryMetricsHandler,
)
from ..src.models.TaskMaterials.QueryTaskMaterial import QueryTaskMaterial

query_metrics_handler = QueryMetricsHandler()


def test_answer():
    material = QueryTaskMaterial(
        query="SELECT a, b, sum(a) FROM foo JOIN bar WHERE a > b;",
        dialect = "postgres",
        metadata = None,
    )
    metadata = query_metrics_handler.infer_metadata(query_material=material)
    assert metadata == {
        "Column": 5,
        "From": 1,
        "GT": 1,
        "Identifier": 7,
        "Join": 1,
        "Select": 1,
        "Sum": 1,
        "Table": 2,
        "Where": 1,
    }

def test_subquery():
    material = QueryTaskMaterial(
        query = "SELECT name FROM (SELECT name, id FROM users) AS sub WHERE id > 10;",
        dialect = "postgres",
        metadata = None,
    )
    metadata = query_metrics_handler.infer_metadata(query_material=material)
    assert metadata == {
        "Column": 4,
        "From": 2,
        "GT": 1,
        "Identifier": 6,
        "Select": 2,
        "Subquery": 1,
        "Table": 1,
        "Where": 1,
        "Literal": 1,
        "TableAlias": 1,
    }

def test_grouping():
    material = QueryTaskMaterial(
        query = "SELECT organisation, COUNT(*) FROM employees GROUP BY organisation HAVING COUNT(*) > 5;",
        dialect = "postgres",
        metadata = None,
    )
    metadata = query_metrics_handler.infer_metadata(query_material=material)
    assert metadata == {
        "Select": 1,
        "From": 1,
        "Table": 1,
        "Column": 2,
        "Identifier": 3, 
        "Count": 2,
        "Group": 1,
        "Having": 1,
        "GT": 1,
        "Literal": 1,
        "Star": 2,
    }

def test_joins():
    material = QueryTaskMaterial(
        query = "SELECT a.id,b-vaö FROM table_a AS a LEFT JOIN table_b AS b ON a.id = b.a_id;",
        dialect = "postgres",
        metadata = None,
    )
    metadata = query_metrics_handler.infer_metadata(query_material=material)
    assert metadata == {
        "Select": 1,
        "From": 1,
        "Table": 2,
        "Column": 5,
        "Identifier": 12, 
        "Join": 1,
        "TableAlias": 2,
        "EQ": 1,       
        "Sub": 1,
    }

def test_union():
    material = QueryTaskMaterial(
        query = "SELECT name FROM organisation UNION SELECT name FROM services,",
        dialect = "postgres",
        metadata = None,
    )
    metadata = query_metrics_handler.infer_metadata(query_material=material)
    assert metadata == {
        "Select": 2,
        "From": 2,
        "Table": 2,
        "Column": 2,
        "Identifier": 4, 
        "Union": 1,
    }    

def test_capitalization():
    material = QueryTaskMaterial(
        query="select A, B from FOO where A > 0;",
        dialect="postgres",
        metadata=None,
    )
    metadata = query_metrics_handler.infer_metadata(query_material=material)
    assert metadata == {
        "Column": 3,
        "From": 1,
        "GT": 1,
        "Identifier": 4,
        "Select": 1,
        "Table": 1,
        "Where": 1,
        "Literal": 1,
    }

# Liefert Fehler:  "self.raise_error("Invalid expression / Unexpected token")"
# def test_invalid_query():
#     material = QueryTaskMaterial(
#         query="SELECT FROM WHERE JOIN",
#         dialect="postgres",
#         metadata=None,
#     )
#     metadata = query_metrics_handler.infer_metadata(query_material=material)
#     assert isinstance(metadata, dict)
from ..src.services.MetaDataInference.SQLDataInferenceHandlers.QueryMetaDataInferenceHandler import (
    QueryMetricsHandler,
)
from ..src.models.TaskMaterials.QueryTaskMaterial import QueryTaskMaterial

query_metrics_handler = QueryMetricsHandler()


def test_answer():
    material = QueryTaskMaterial(
        query="SELECT a, b, sum(a) FROM foo JOIN bar WHERE a > b;",
        dialect="postgres",
        metadata=None,
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

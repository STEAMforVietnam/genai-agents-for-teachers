

from sentence_transformers import SentenceTransformer
from pymilvus import Collection, connections

MODEL_NAME='bkai-foundation-models/vietnamese-bi-encoder'

class VectorStore():
    def __init__(self,  uri: str, token: str):
        connections.connect(uri=uri, token= token, alias="default")
        model_name = MODEL_NAME
        self.model = SentenceTransformer(model_name)
        self.collection = Collection(name="s4v_python_oh_bkai")
        self.collection.load()

    

    def search(self, query: str, search_params={
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }, **kwargs):
        embeddings = self.model.encode(query)
        query_vector = [embeddings]
        try:
            search_results = self.collection.search(
                data=query_vector,
                anns_field="vector",
                param=search_params,
                limit=20,
                output_fields=["filename", "text", "page_number"],
                **kwargs
            )

            return search_results

        except Exception as e:
            print(e)
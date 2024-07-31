import os
from tools.retrieval import RetrievalConfig, RetrievalTools


MODEL_NAME='bkai-foundation-models/vietnamese-bi-encoder'
COLLECTION_NAME = 's4v_python_oh_bkai'
retrieval_config = RetrievalConfig(
            embedding_model=MODEL_NAME,
            milvus_collection=COLLECTION_NAME,
            milvus_connection_args={"uri": os.environ.get("DATABSE_PUBLIC_ENDPOINT"),
                            "token": os.environ.get("DATABASE_API_KEY"),
                            "secure": True
            }
        )

tool_fac= RetrievalTools(retrieval_config)
tools = tool_fac.get_tools()
tool = tools[0]
tmp = tool.retrieve_lesson_content("động học")

print(tmp)
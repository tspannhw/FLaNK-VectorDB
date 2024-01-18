# FLaNK-VectorDB
NiFi and Vector Databases


### need credits for openai

````
2024-01-18 12:20:57,634 WARNING langchain.embeddings.openai Retrying langchain.embeddings.openai.embed_with_retry.<locals>._embed_with_retry in 10.0 seconds as it raised RateLimitError: You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors..
2024-01-18 12:21:07,751 INFO openai error_code=insufficient_quota error_message='You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.' error_param=None error_type=insufficient_quota message='OpenAI API error received' stream_error=False


openai.error.RateLimitError: You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.

````


### Langchain changes?  or Pinecone?

https://api.python.langchain.com/en/stable/vectorstores/langchain_community.vectorstores.pinecone.Pinecone.html?highlight=similarity_search_with_score#langchain_community.vectorstores.pinecone.Pinecone.similarity_search_with_score


### Updated Query

````

PythonProcessor[type=QueryPinecone, id=faa3b955-018c-1000-96b9-58abe3b8ddbd] Failed to transform FlowFile[filename=6ac513e7-5ad9-481e-b383-70bb5f5e6021]: py4j.Py4JException: An exception was raised by the Python Proxy. Return Message: Traceback (most recent call last):
  File "/Users/tspann/Downloads/servers/nifi-2.0.0-M1/python/framework/py4j/java_gateway.py", line 2466, in _call_proxy
    return_value = getattr(self.pool[obj_id], method)(*params)
  File "/Users/tspann/Downloads/servers/nifi-2.0.0-M1/python/api/nifiapi/flowfiletransform.py", line 33, in transformFlowFile
    return self.transform(self.process_context, flowfile)
  File "/Users/tspann/Downloads/servers/nifi-2.0.0-M1/python/extensions/vectorstores/QueryPinecone.py", line 144, in transform
    results = vectorstore.similarity_search_with_score(query, k=num_results)
  File "/Users/tspann/Downloads/servers/nifi-2.0.0-M1/./work/python/extensions/QueryPinecone/2.0.0-SNAPSHOT/langchain/vectorstores/pinecone.py", line 171, in similarity_search_with_score
    return self.similarity_search_by_vector_with_score(
  File "/Users/tspann/Downloads/servers/nifi-2.0.0-M1/./work/python/extensions/QueryPinecone/2.0.0-SNAPSHOT/langchain/vectorstores/pinecone.py", line 188, in similarity_search_by_vector_with_score
    results = self._index.query(
  File "/Users/tspann/Downloads/servers/nifi-2.0.0-M1/./work/python/extensions/QueryPinecone/2.0.0-SNAPSHOT/pinecone/utils/error_handling.py", line 10, in inner_func
    return func(*args, **kwargs)
TypeError: Index.query() got multiple values for argument 'top_k'


`````

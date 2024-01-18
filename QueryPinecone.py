# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#from langchain.vectorstores import Pinecone
import langchain.vectorstores
from langchain.embeddings.openai import OpenAIEmbeddings
from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult
from nifiapi.properties import PropertyDescriptor, StandardValidators, ExpressionLanguageScope
import QueryUtils
#import pinecone
from pinecone import Pinecone

class QueryPinecone(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']

    class ProcessorDetails:
        version = '2.0.0-SNAPSHOT'
        description = "Queries Pinecone in order to gather a specified number of documents that are most closely related to the given query."
        tags = ["pinecone", "vector", "vectordb", "vectorstore", "embeddings", "ai", "artificial intelligence", "ml", "machine learning", "text", "LLM"]


    PINECONE_API_KEY = PropertyDescriptor(
        name="Pinecone API Key",
        description="The API Key to use in order to authentication with Pinecone",
        sensitive=True,
        required=True,
        validators=[StandardValidators.NON_EMPTY_VALIDATOR]
    )
    OPENAI_API_KEY = PropertyDescriptor(
        name="OpenAI API Key",
        description="The API Key for OpenAI in order to create embeddings",
        sensitive=True,
        required=True,
        validators=[StandardValidators.NON_EMPTY_VALIDATOR]
    )
    PINECONE_ENV = PropertyDescriptor(
        name="Pinecone Environment",
        description="The name of the Pinecone Environment. This can be found in the Pinecone console next to the API Key.",
        sensitive=False,
        required=True,
        validators=[StandardValidators.NON_EMPTY_VALIDATOR]
    )
    INDEX_NAME = PropertyDescriptor(
        name="Index Name",
        description="The name of the Pinecone index.",
        sensitive=False,
        required=True,
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        expression_language_scope=ExpressionLanguageScope.FLOWFILE_ATTRIBUTES
    )
    QUERY = PropertyDescriptor(
        name="Query",
        description="The text of the query to send to Pinecone.",
        required=True,
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        expression_language_scope=ExpressionLanguageScope.FLOWFILE_ATTRIBUTES
    )
    NUMBER_OF_RESULTS = PropertyDescriptor(
        name="Number of Results",
        description="The number of results to return from Pinecone",
        required=True,
        validators=[StandardValidators.POSITIVE_INTEGER_VALIDATOR],
        default_value="10",
        expression_language_scope=ExpressionLanguageScope.FLOWFILE_ATTRIBUTES
    )
    TEXT_KEY = PropertyDescriptor(
        name="Text Key",
        description="The key in the document that contains the text to create embeddings for.",
        required=True,
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        default_value="text",
        expression_language_scope=ExpressionLanguageScope.FLOWFILE_ATTRIBUTES
    )
    NAMESPACE = PropertyDescriptor(
        name="Namespace",
        description="The name of the Pinecone Namespace to put the documents to.",
        required=False,
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        expression_language_scope=ExpressionLanguageScope.FLOWFILE_ATTRIBUTES
    )


    properties = [PINECONE_API_KEY,
                  OPENAI_API_KEY,
                  PINECONE_ENV,
                  INDEX_NAME,
                  QUERY,
                  NUMBER_OF_RESULTS,
                  NAMESPACE,
                  TEXT_KEY,
                  QueryUtils.OUTPUT_STRATEGY,
                  QueryUtils.RESULTS_FIELD,
                  QueryUtils.INCLUDE_METADATAS,
                  QueryUtils.INCLUDE_DISTANCES]

    embeddings = None
    query_utils = None
    pc = None

    def __init__(self, **kwargs):
        pass

    def getPropertyDescriptors(self):
        return self.properties

    def onScheduled(self, context):
        api_key = context.getProperty(self.PINECONE_API_KEY).getValue()
        pinecone_env = context.getProperty(self.PINECONE_ENV).getValue()

        # initialize pinecone
        #pinecone.init(
        #    api_key=api_key,
        #    environment=pinecone_env,
        #)
        self.pc = Pinecone(api_key=api_key, environment=pinecone_env)
        openai_api_key = context.getProperty(self.OPENAI_API_KEY).getValue()
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.query_utils = QueryUtils.QueryUtils(context)


    def transform(self, context, flowfile):
        # First, check if our index already exists. If it doesn't, we create it
        index_name = context.getProperty(self.INDEX_NAME).evaluateAttributeExpressions(flowfile).getValue()
        query = context.getProperty(self.QUERY).evaluateAttributeExpressions(flowfile).getValue()
        namespace = context.getProperty(self.NAMESPACE).evaluateAttributeExpressions(flowfile).getValue()
        num_results = context.getProperty(self.NUMBER_OF_RESULTS).evaluateAttributeExpressions(flowfile).asInteger()

        index = self.pc.Index(index_name)

        text_key = context.getProperty(self.TEXT_KEY).evaluateAttributeExpressions().getValue()
        vectorstore = langchain.vectorstores.Pinecone(index, self.embeddings.embed_query, text_key, namespace=namespace)
        results = vectorstore.similarity_search_with_score(query, num_results)

        documents = []
        for result in results:
            documents.append(result[0].page_content)

        if context.getProperty(QueryUtils.INCLUDE_METADATAS):
            metadatas = []
            for result in results:
                metadatas.append(result[0].metadata)
        else:
            metadatas = None

        if context.getProperty(QueryUtils.INCLUDE_DISTANCES):
            distances = []
            for result in results:
                distances.append(result[1])
        else:
            distances = None

        (output_contents, mime_type) = self.query_utils.create_json(flowfile, documents, metadatas, None, distances, None)
        attributes = {"mime.type": mime_type}

        return FlowFileTransformResult(relationship = "success", contents=output_contents, attributes=attributes)

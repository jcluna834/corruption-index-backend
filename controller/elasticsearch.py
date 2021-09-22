import datetime

__author__ = "Julio Luna"
__email__ = "jcluna@unicauca.edu.co"

from elasticsearch import AsyncElasticsearch, NotFoundError, Elasticsearch
from elasticsearch.helpers import async_streaming_bulk
from elasticapm.contrib.starlette import ElasticAPM, make_apm_client
from controller.base import BaseController
from fastapi.encoders import jsonable_encoder
from util.injector import inject
from settings import config


class ElasticSearchFunction(BaseController):
    es = Elasticsearch()

    # Retorna todos los documentos asociados a un índice
    async def searchAll(self):
        return await self.es.search(index="documentos", body={"query": {"match_all": {}}})

    # Agrega un documento a a un índice
    def add(self, obj):
        return self.es.index(index="documentos", body=obj)

    # Detiene el cliente de ElasticSearch
    async def app_shutdown(self):
        await self.es.close()

    # Informa el estado del nodo ElasticSearch
    async def index(self):
        return await self.es.cluster.health()

    # Realiza una búsqueda por contenido y excluyendo el actualdocument retornando el primer elemento de la misma
    def searchByContentExcluyeDocID(self, query, documentID):
        frag_size = round(len(query) *config['PERCENTAGE_TEXT']) + len(query)
        return self.es.search(
            index="documentos",
            body={
                "from": 0, "size": 1,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "content": query
                                }
                            }
                        ],
                        "must_not": [
                            {
                                "match": {
                                    "id": documentID
                                }
                            }
                        ]
                    }
                },
                "_source": {
                    "includes": ["id", "title"]
                },
                "highlight": {
                    "pre_tags": [""],
                    "post_tags": [""],
                    "fields": {
                        "content": {
                            "fragment_size": frag_size,
                            "number_of_fragments": 1,
                            "order": "score"
                        }
                    }
                }
            }
        )

    # Realiza una búsqueda por contenido retornando el primer elemento de la misma
    def searchByContent(self, query):
        frag_size = round(len(query) *config['PERCENTAGE_TEXT']) + len(query)
        return self.es.search(
            index="documentos",
            body={
                "from": 0, "size": 1,
                "query": {
                    "match": {"content": query}
                },
                "_source": {
                    "includes": ["id", "title"]
                },
                "highlight": {
                    "pre_tags": [""],
                    "post_tags": [""],
                    "fields": {
                        "content": {
                            "fragment_size": frag_size,
                            "number_of_fragments": 1,
                            "order": "score"
                        }
                    }
                }
            }
        )

    # Realiza una búsqueda por contenido retornando elrimer elemento de la misma
    def searchBetweenDocs(self, query, similarDocumentID): #TODO - garantizar la búsqueda solo con 1 doc
        frag_size = round(len(query) *config['PERCENTAGE_TEXT']) + len(query)
        return self.es.search(
            index="documentos",
            body={
                "from": 0, "size": 1,
                "query": {

                    "bool": {
                        "must": [
                            {
                            "match": {
                                "content": query
                            }
                            },
                            {
                            "match": {
                                "id": similarDocumentID
                            }
                            }
                        ]
                    }
                },
                "_source": {
                    "includes": ["id", "title"]
                },
                "highlight": {
                    "pre_tags": [""],
                    "post_tags": [""],
                    "fields": {
                        "content": {
                            "fragment_size": frag_size,
                            "number_of_fragments": 1,
                            "order": "score"
                        }
                    }
                }
            }
        )

    # Realiza una búsqueda
    async def search(self, query):
        return await self.es.search(
            index="documentos", body={"query": {"multi_match": {"query": query}}}
        )

    # Eliminar un doc por id del doc de BD
    def delete_by_query(self, id):
        return self.es.delete_by_query(
            index="documentos", body={"query": {"match": {"id": id}}}
        )

    # Elimina todos los documentos asociados a un index
    async def delete(self):
        return await self.es.delete_by_query(index="documentos", body={"query": {"match_all": {}}})

    # Elimina un documento asociado a un index
    async def delete_id(self, id):
        try:
            return await self.es.delete(index="documentos", id=id)
        except NotFoundError as e:
            return e.info, 404

    # Actualiza un documento asociado a un index
    async def update(self):
        response = []
        docs = await self.es.search(
            index="documentos", body={"query": {"multi_match": {"query": ""}}}
        )
        now = datetime.datetime.utcnow()
        for doc in docs["hits"]["hits"]:
            response.append(
                await self.es.update(
                    index="documentos", id=doc["_id"], body={"doc": {"modified": now}}
                )
            )
        return jsonable_encoder(response)

    # Retorna documento asociado a un index
    async def get_doc(self, id):
        return await self.es.get(index="documentos", id=id)

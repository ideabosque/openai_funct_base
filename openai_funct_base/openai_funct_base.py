#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import traceback
from typing import Any, Dict, List

import boto3

from silvaengine_utility import Utility


class OpenAIFunctBase:
    def __init__(self, logger: logging.Logger, **setting: Dict[str, Any]):
        try:
            # Set up AWS credentials in Boto3
            self.endpoint_id = setting["endpoint_id"]
            self.logger = logger
            if (
                setting.get("region_name")
                and setting.get("aws_access_key_id")
                and setting.get("aws_secret_access_key")
            ):
                self.aws_lambda = boto3.client(
                    "lambda",
                    region_name=setting.get("region_name"),
                    aws_access_key_id=setting.get("aws_access_key_id"),
                    aws_secret_access_key=setting.get("aws_secret_access_key"),
                )
            else:
                self.aws_lambda = boto3.client(
                    "lambda",
                )
        except Exception as e:
            log = traceback.format_exc()
            logger.error(log)
            raise e

    def execute_graphql_query(
        self,
        funct: str,
        query: str,
        variables: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        params = {
            "query": query,
            "variables": variables,
        }

        result = Utility.invoke_funct_on_aws_lambda(
            self.logger,
            self.aws_lambda,
            **{"endpoint_id": self.endpoint_id, "funct": funct, "params": params},
        )
        return Utility.json_loads(Utility.json_loads(result))["data"]

    def inquiry_data(self, **arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = """fragment VectorDocInfo on VectorDocType{
    vectorDoc
}

query getVectorDocs(
    $userQuery: String!,
    $indexName: String!,
    $vectorField: String!,
    $returnFields: [String]!,
    $hybridFields: [JSON],
    $k: String,
    $logResults: Boolean,
) {
    vectorDocs(
        userQuery: $userQuery,
        indexName: $indexName,
        vectorField: $vectorField,
        returnFields: $returnFields,
        hybridFields: $hybridFields,
        k: $k,
        logResults: $logResults
    ) {
        ...VectorDocInfo
    }
}"""
        return self.execute_graphql_query(
            "data_inquiry_graphql",
            query,
            {
                "userQuery": arguments["user_query"],
                "indexName": "embeddings-index",
                "vectorField": "content_vector",
                "returnFields": [
                    "sku",
                    "name",
                    "url_key",
                    "description",
                    "vector_score",
                ],
            },
        )

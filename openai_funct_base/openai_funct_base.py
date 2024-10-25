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
            self.logger = logger
            self.setting = setting
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
            self.logger.error(log)
            raise e

    def execute_graphql_query(
        self,
        endpoint_id: str,
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
            **{"endpoint_id": endpoint_id, "funct": funct, "params": params},
        )
        result = Utility.json_loads(Utility.json_loads(result))
        if result.get("data"):
            return result["data"]
        if result.get("errors"):
            raise Exception(result["errors"])
        if result.get("message"):
            raise Exception(result["message"])
        raise Exception(f"Unknown error: {result}")

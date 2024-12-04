#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

__author__ = "bibow"

import logging
import traceback
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError

from silvaengine_utility import Utility


class OpenAIFunctBase:
    def __init__(self, logger: logging.Logger, **setting: Dict[str, Any]):
        """
        Initialize the OpenAIFunctBase class.
        :param logger: Logger instance for logging errors and information.
        :param setting: Configuration setting for AWS credentials and region.
        """
        try:
            self.logger = logger
            self.setting = setting
            self._initialize_aws_lambda_client()
        except (BotoCoreError, NoCredentialsError) as boto_error:
            self.logger.error(f"AWS Boto3 error: {boto_error}")
            raise boto_error
        except Exception as e:
            log = traceback.format_exc()
            self.logger.error(log)
            raise e

    def _initialize_aws_lambda_client(self):
        """
        Initialize the AWS Lambda client using the provided credentials or default configuration.
        """
        region_name = self.setting.get("region_name")
        aws_access_key_id = self.setting.get("aws_access_key_id")
        aws_secret_access_key = self.setting.get("aws_secret_access_key")

        if region_name and aws_access_key_id and aws_secret_access_key:
            self.aws_lambda = boto3.client(
                "lambda",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        else:
            self.aws_lambda = boto3.client("lambda")

    def execute_graphql_query(
        self,
        endpoint_id: str,
        function_name: str,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query using an AWS Lambda function.
        :param endpoint_id: The ID of the GraphQL endpoint.
        :param function_name: The name of the AWS Lambda function to invoke.
        :param query: The GraphQL query string.
        :param variables: Optional GraphQL variables.
        :return: Response data from the GraphQL query.
        :raises Exception: If there is an error in the GraphQL response.
        """
        if variables is None:
            variables = {}

        params = {
            "query": query,
            "variables": variables,
        }

        try:
            result = Utility.invoke_funct_on_aws_lambda(
                self.logger,
                self.aws_lambda,
                **{
                    "endpoint_id": endpoint_id,
                    "funct": function_name,
                    "params": params,
                },
            )
            result = Utility.json_loads(Utility.json_loads(result))

            if "data" in result:
                return result["data"]
            elif "errors" in result:
                raise Exception(result["errors"])
            elif "message" in result:
                raise Exception(result["message"])
            else:
                raise Exception(f"Unknown error: {result}")

        except Exception as e:
            self.logger.error(f"Error executing GraphQL query: {e}")
            raise

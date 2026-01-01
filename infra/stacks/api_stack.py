from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    CfnOutput,
)
from constructs import Construct


class ApiStack(Stack):
    """
    API Gateway stack with REST API, usage plans, and API keys.

    Features:
    - REST API with CORS enabled
    - Health check endpoint
    - API Key and Usage Plan for rate limiting
    - Configurable throttling

    Usage:
        api_stack = ApiStack(
            app,
            "MyProject-ApiStack",
            project_name="MyProject",
            resource_suffix="-dev",
            env=env,
        )
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_name: str = "MyProject",
        resource_suffix: str = "",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.project_name = project_name
        self.resource_suffix = resource_suffix

        # Normalize names for AWS resources
        name_prefix = project_name.lower().replace(" ", "-").replace("_", "-")

        # =================================================================
        # API Gateway REST API
        # =================================================================
        self.api = apigateway.RestApi(
            self,
            f"{project_name}Api{resource_suffix}",
            rest_api_name=f"{name_prefix}-api{resource_suffix}",
            description=f"{project_name} API Gateway{resource_suffix}",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                ],
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="v1",
                throttling_rate_limit=1000,
                throttling_burst_limit=2000,
                logging_level=apigateway.MethodLoggingLevel.INFO,
            ),
        )

        # =================================================================
        # Mock Integration (placeholder for Lambda integrations)
        # =================================================================
        mock_integration = apigateway.MockIntegration(
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_templates={
                        "application/json": '{"message": "API Gateway ready for integration"}'
                    },
                )
            ],
            request_templates={"application/json": '{"statusCode": 200}'},
        )

        # =================================================================
        # Endpoints
        # =================================================================

        # Health check endpoint
        health = self.api.root.add_resource("health")
        health.add_method(
            "GET",
            mock_integration,
            method_responses=[apigateway.MethodResponse(status_code="200")],
        )

        # API v1 placeholder
        api_v1 = self.api.root.add_resource("api")
        api_v1.add_method(
            "GET",
            mock_integration,
            method_responses=[apigateway.MethodResponse(status_code="200")],
        )

        # =================================================================
        # API Key & Usage Plan
        # =================================================================
        self.api_key = self.api.add_api_key(
            f"{project_name}ApiKey{resource_suffix}",
            api_key_name=f"{name_prefix}-key{resource_suffix}",
            description=f"API key for {project_name}{resource_suffix}",
        )

        self.usage_plan = self.api.add_usage_plan(
            f"{project_name}UsagePlan{resource_suffix}",
            name=f"{name_prefix}-usage{resource_suffix}",
            description=f"Usage plan for {project_name} API{resource_suffix}",
            throttle=apigateway.ThrottleSettings(rate_limit=100, burst_limit=200),
            quota=apigateway.QuotaSettings(
                limit=10000, period=apigateway.Period.DAY
            ),
            api_stages=[
                apigateway.UsagePlanPerApiStage(
                    api=self.api,
                    stage=self.api.deployment_stage,
                )
            ],
        )

        self.usage_plan.add_api_key(self.api_key)

        # =================================================================
        # Outputs
        # =================================================================
        CfnOutput(
            self,
            "ApiEndpoint",
            value=self.api.url,
            description=f"{project_name} API Gateway endpoint",
            export_name=f"{project_name}-ApiEndpoint{resource_suffix}",
        )

        CfnOutput(
            self,
            "ApiKeyId",
            value=self.api_key.key_id,
            description=f"{project_name} API Key ID",
            export_name=f"{project_name}-ApiKeyId{resource_suffix}",
        )

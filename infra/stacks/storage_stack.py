from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct
from typing import Optional


class StorageStack(Stack):
    """
    S3 storage stack with configurable lifecycle rules.

    Features:
    - S3 bucket with encryption
    - Configurable object expiration
    - CORS configuration for web access
    - Optional integration with Auth stack for IAM policies

    Usage:
        storage_stack = StorageStack(
            app,
            "MyProject-StorageStack",
            project_name="MyProject",
            resource_suffix="-dev",
            expiration_days=1,  # Auto-delete after 1 day
            auth_stack=auth_stack,  # Optional: for IAM integration
            env=env,
        )
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_name: str = "MyProject",
        resource_suffix: str = "",
        expiration_days: int = 1,
        auth_stack: Optional[Stack] = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.project_name = project_name
        self.resource_suffix = resource_suffix

        # Normalize names for AWS resources
        name_prefix = project_name.lower().replace(" ", "-").replace("_", "-")

        # =================================================================
        # S3 Bucket
        # =================================================================
        self.bucket = s3.Bucket(
            self,
            f"{project_name}Bucket{resource_suffix}",
            bucket_name=f"{name_prefix}-storage{resource_suffix.lower()}",
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            # Lifecycle rules
            lifecycle_rules=[
                s3.LifecycleRule(
                    id=f"AutoDelete{expiration_days}Days",
                    enabled=True,
                    expiration=Duration.days(expiration_days),
                    abort_incomplete_multipart_upload_after=Duration.days(1),
                ),
            ],
            # CORS configuration
            cors=[
                s3.CorsRule(
                    allowed_methods=[
                        s3.HttpMethods.GET,
                        s3.HttpMethods.PUT,
                        s3.HttpMethods.POST,
                        s3.HttpMethods.DELETE,
                        s3.HttpMethods.HEAD,
                    ],
                    allowed_origins=["*"],  # Restrict in production
                    allowed_headers=["*"],
                    max_age=3000,
                )
            ],
        )

        # =================================================================
        # IAM Policy for Auth Stack Integration (Optional)
        # =================================================================
        if auth_stack and hasattr(auth_stack, "authenticated_role"):
            # Grant the authenticated role access to this bucket
            self.bucket.grant_read_write(auth_stack.authenticated_role)

            # Or add more specific permissions:
            # auth_stack.authenticated_role.add_to_policy(
            #     iam.PolicyStatement(
            #         actions=["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
            #         resources=[f"{self.bucket.bucket_arn}/*"],
            #     )
            # )

        # =================================================================
        # Outputs
        # =================================================================
        CfnOutput(
            self,
            "BucketName",
            value=self.bucket.bucket_name,
            description=f"{project_name} S3 bucket name",
            export_name=f"{project_name}-BucketName{resource_suffix}",
        )

        CfnOutput(
            self,
            "BucketArn",
            value=self.bucket.bucket_arn,
            description=f"{project_name} S3 bucket ARN",
            export_name=f"{project_name}-BucketArn{resource_suffix}",
        )

        CfnOutput(
            self,
            "BucketPolicy",
            value=f"Objects are automatically deleted after {expiration_days} day(s)",
            description="Bucket retention policy",
        )

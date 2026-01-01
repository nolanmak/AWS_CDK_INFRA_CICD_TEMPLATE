from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class AuthStack(Stack):
    """
    Cognito authentication stack with User Pool, Identity Pool, and IAM roles.

    Features:
    - User Pool with email/username sign-in
    - Self sign-up with email verification
    - Identity Pool for AWS resource access
    - IAM roles for authenticated users
    - Hosted UI domain

    Usage:
        auth_stack = AuthStack(
            app,
            "MyProject-AuthStack",
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
        # Cognito User Pool
        # =================================================================
        self.user_pool = cognito.UserPool(
            self,
            f"{project_name}UserPool{resource_suffix}",
            user_pool_name=f"{name_prefix}-users{resource_suffix}",
            # Sign-in options
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True,
            ),
            # Self sign-up configuration
            self_sign_up_enabled=True,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            # User verification
            user_verification=cognito.UserVerificationConfig(
                email_subject=f"{project_name} - Verify your email",
                email_body=f"Thank you for signing up to {project_name}! Your verification code is {{####}}",
                email_style=cognito.VerificationEmailStyle.CODE,
            ),
            # Password policy
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            # Standard attributes
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True),
                given_name=cognito.StandardAttribute(required=False, mutable=True),
                family_name=cognito.StandardAttribute(required=False, mutable=True),
            ),
            # Account recovery
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            # Deletion protection
            removal_policy=RemovalPolicy.DESTROY if resource_suffix else RemovalPolicy.RETAIN,
        )

        # =================================================================
        # Cognito User Pool Client
        # =================================================================
        self.user_pool_client = cognito.UserPoolClient(
            self,
            f"{project_name}WebClient{resource_suffix}",
            user_pool=self.user_pool,
            user_pool_client_name=f"{name_prefix}-web-client{resource_suffix}",
            # OAuth settings
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                custom=False,
                admin_user_password=True,
            ),
            # Token validity
            access_token_validity=Duration.hours(1),
            id_token_validity=Duration.hours(1),
            refresh_token_validity=Duration.days(30),
            # Security
            prevent_user_existence_errors=True,
            # OAuth scopes
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=False,
                ),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                ],
                callback_urls=[
                    "http://localhost:3000",
                    "https://localhost:3000",
                    # Add your production domain here:
                    # "https://yourdomain.com",
                ],
                logout_urls=[
                    "http://localhost:3000",
                    "https://localhost:3000",
                    # Add your production domain here:
                    # "https://yourdomain.com",
                ],
            ),
            generate_secret=False,
        )

        # =================================================================
        # Cognito Identity Pool
        # =================================================================
        self.identity_pool = cognito.CfnIdentityPool(
            self,
            f"{project_name}IdentityPool{resource_suffix}",
            identity_pool_name=f"{name_prefix}_identity_pool{resource_suffix}".replace("-", "_"),
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=self.user_pool_client.user_pool_client_id,
                    provider_name=self.user_pool.user_pool_provider_name,
                )
            ],
        )

        # =================================================================
        # IAM Role for Authenticated Users
        # =================================================================
        self.authenticated_role = iam.Role(
            self,
            f"CognitoAuthenticatedRole{resource_suffix}",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    },
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
            # Add your custom policies here:
            # inline_policies={
            #     "CustomPolicy": iam.PolicyDocument(
            #         statements=[
            #             iam.PolicyStatement(
            #                 actions=["s3:PutObject", "s3:GetObject"],
            #                 resources=["arn:aws:s3:::your-bucket/*"],
            #             )
            #         ]
            #     )
            # },
        )

        # Attach role to identity pool
        cognito.CfnIdentityPoolRoleAttachment(
            self,
            f"IdentityPoolRoleAttachment{resource_suffix}",
            identity_pool_id=self.identity_pool.ref,
            roles={
                "authenticated": self.authenticated_role.role_arn,
            },
        )

        # =================================================================
        # Cognito Domain (for Hosted UI)
        # =================================================================
        self.user_pool_domain = cognito.UserPoolDomain(
            self,
            f"{project_name}Domain{resource_suffix}",
            user_pool=self.user_pool,
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=f"{name_prefix}{resource_suffix}".replace("-", "").lower()
            ),
        )

        # =================================================================
        # Outputs
        # =================================================================
        CfnOutput(
            self,
            "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID",
            export_name=f"{project_name}-UserPoolId{resource_suffix}",
        )

        CfnOutput(
            self,
            "UserPoolClientId",
            value=self.user_pool_client.user_pool_client_id,
            description="Cognito User Pool Client ID",
            export_name=f"{project_name}-UserPoolClientId{resource_suffix}",
        )

        CfnOutput(
            self,
            "IdentityPoolId",
            value=self.identity_pool.ref,
            description="Cognito Identity Pool ID",
            export_name=f"{project_name}-IdentityPoolId{resource_suffix}",
        )

        CfnOutput(
            self,
            "UserPoolDomain",
            value=self.user_pool_domain.domain_name,
            description="Cognito User Pool Domain",
            export_name=f"{project_name}-UserPoolDomain{resource_suffix}",
        )

        CfnOutput(
            self,
            "CognitoHostedUIUrl",
            value=f"https://{self.user_pool_domain.domain_name}.auth.{self.region}.amazoncognito.com",
            description="Cognito Hosted UI URL",
            export_name=f"{project_name}-HostedUIUrl{resource_suffix}",
        )

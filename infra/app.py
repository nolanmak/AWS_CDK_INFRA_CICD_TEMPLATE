#!/usr/bin/env python3
"""
AWS CDK Application Entry Point

This is the main entry point for the AWS CDK application.
Customize the PROJECT_NAME and stack configurations below.
"""
import os
from dotenv import load_dotenv

from aws_cdk import App, Environment

# Import your stacks here
from stacks.api_stack import ApiStack
from stacks.auth_stack import AuthStack
from stacks.storage_stack import StorageStack

load_dotenv()

# =============================================================================
# CONFIGURATION - Customize these values for your project
# =============================================================================
PROJECT_NAME = os.environ.get("PROJECT_NAME", "MyProject")
ENV_NAME = os.environ.get("ENV", "dev")

# =============================================================================
# AWS Environment
# =============================================================================
app = App()

env = Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

# Resource suffix for multi-environment deployments (e.g., "-dev", "-staging")
resource_suffix = f"-{ENV_NAME}" if ENV_NAME != "production" else ""

# =============================================================================
# Stack Definitions - Uncomment/modify stacks as needed
# =============================================================================

# 1. Authentication Stack (Cognito User Pool)
auth_stack = AuthStack(
    app,
    f"{PROJECT_NAME}-AuthStack",
    project_name=PROJECT_NAME,
    resource_suffix=resource_suffix,
    env=env,
)

# 2. API Gateway Stack
api_stack = ApiStack(
    app,
    f"{PROJECT_NAME}-ApiStack",
    project_name=PROJECT_NAME,
    resource_suffix=resource_suffix,
    env=env,
)

# 3. Storage Stack (S3 with lifecycle rules)
storage_stack = StorageStack(
    app,
    f"{PROJECT_NAME}-StorageStack",
    project_name=PROJECT_NAME,
    resource_suffix=resource_suffix,
    # Pass auth stack if you need cross-stack references
    auth_stack=auth_stack,
    env=env,
)

# =============================================================================
# Synthesize
# =============================================================================
app.synth()

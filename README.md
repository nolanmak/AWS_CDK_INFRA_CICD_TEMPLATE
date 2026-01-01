# AWS CDK Infrastructure Template with CI/CD

A production-ready AWS CDK infrastructure template with GitHub Actions CI/CD pipelines. Clone, configure, and deploy your AWS infrastructure in minutes.

## Features

- **AWS CDK (Python)** - Infrastructure as Code
- **GitHub Actions CI/CD** - Automated testing and deployment
- **Multi-Environment Support** - dev, staging, production
- **Pre-built Stacks**:
  - **API Gateway** - REST API with CORS, API keys, usage plans
  - **Cognito Auth** - User pools, identity pools, hosted UI
  - **S3 Storage** - Encrypted bucket with lifecycle rules

## Quick Start

### 1. Clone & Configure

```bash
# Clone this template
git clone https://github.com/yourusername/AWSCDK_CI_CD.git my-project-infra
cd my-project-infra

# Create your .env file
cp infra/.env.example infra/.env
```

### 2. Update Configuration

Edit `infra/.env`:
```bash
PROJECT_NAME=MyProject
CDK_DEFAULT_ACCOUNT=123456789012
CDK_DEFAULT_REGION=us-east-1
ENV=dev
```

Edit `app.py` to customize your stack names and configurations.

### 3. Local Development

```bash
cd infra

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install -g aws-cdk

# Synthesize CloudFormation templates
cdk synth

# Deploy to AWS (ensure AWS credentials are configured)
cdk deploy --all
```

### 4. GitHub Actions Setup

Add these secrets to your GitHub repository:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |

## Project Structure

```
.
├── .github/
│   └── workflows/
│       ├── deploy.yml      # Production deployment
│       └── test.yml        # PR validation & testing
├── infra/
│   ├── stacks/
│   │   ├── __init__.py
│   │   ├── api_stack.py    # API Gateway
│   │   ├── auth_stack.py   # Cognito Auth
│   │   └── storage_stack.py # S3 Storage
│   ├── app.py              # CDK entry point
│   ├── cdk.json            # CDK configuration
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── tests/                  # Unit tests (optional)
└── README.md
```

## Stack Details

### API Stack (`api_stack.py`)
- REST API Gateway with CORS
- Health check endpoint (`/health`)
- API placeholder endpoint (`/api`)
- API Key with usage plan
- Rate limiting (configurable)

### Auth Stack (`auth_stack.py`)
- Cognito User Pool with email/username sign-in
- Self sign-up with email verification
- User Pool Client for web apps
- Identity Pool for AWS resource access
- IAM roles for authenticated users
- Hosted UI domain

### Storage Stack (`storage_stack.py`)
- S3 bucket with encryption
- Configurable object expiration
- CORS enabled for web uploads
- Auto-delete on stack destruction
- Optional integration with Auth stack

## Customization

### Adding a New Stack

1. Create `infra/stacks/my_stack.py`:
```python
from aws_cdk import Stack, CfnOutput
from constructs import Construct

class MyStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_name: str = "MyProject",
        resource_suffix: str = "",
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Add your resources here
```

2. Import in `infra/stacks/__init__.py`
3. Add to `infra/app.py`

### Modifying Environments

Edit the environment configuration in `app.py`:
```python
resource_suffix = f"-{ENV_NAME}" if ENV_NAME != "production" else ""
```

## CI/CD Workflows

### `deploy.yml`
- Triggers on push to `main` (infra changes only)
- Manual trigger with environment selection
- Validates CDK synth before deploy
- Deploys all stacks with proper ordering

### `test.yml`
- Triggers on PRs to `main`/`develop`
- Runs linting (black, flake8, mypy)
- Tests CDK synth for all environments
- Security scan with Checkov
- Unit tests with coverage

## Commands Reference

```bash
# Synthesize CloudFormation template
cdk synth

# Compare deployed stack with current state
cdk diff

# Deploy all stacks
cdk deploy --all

# Deploy specific stack
cdk deploy MyProject-AuthStack

# Destroy all stacks
cdk destroy --all

# List all stacks
cdk list
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_NAME` | Your project name (used in resource naming) | `MyProject` |
| `CDK_DEFAULT_ACCOUNT` | AWS Account ID | Required |
| `CDK_DEFAULT_REGION` | AWS Region | `us-east-1` |
| `ENV` | Environment (dev/staging/production) | `dev` |

## Security Considerations

- S3 buckets block all public access by default
- Cognito prevents user enumeration attacks
- API Gateway includes rate limiting
- All secrets should be stored in GitHub Secrets
- Checkov scans for security misconfigurations

## License

MIT License - Feel free to use this template for any project.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Happy deploying!** 🚀

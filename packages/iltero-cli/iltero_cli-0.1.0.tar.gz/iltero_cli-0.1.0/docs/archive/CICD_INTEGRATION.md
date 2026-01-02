# CI/CD Integration Guide

Complete guide for integrating Iltero CLI into your CI/CD pipelines.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Jenkins](#jenkins)
- [Azure DevOps](#azure-devops)
- [CircleCI](#circleci)
- [Bitbucket Pipelines](#bitbucket-pipelines)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Iltero CLI is designed for CI/CD integration with:

- **Environment variable configuration** - No interactive prompts
- **Pipeline tokens** - Dedicated tokens for automation
- **Exit codes** - Standard exit codes for pass/fail
- **Multiple output formats** - JSON, SARIF, JUnit XML
- **Threshold configuration** - Fail builds on severity thresholds

## Prerequisites

### 1. Create Pipeline Token

1. Log in to Iltero web UI
2. Navigate to **Settings** → **API Tokens**
3. Click **Create Token**
4. Select **Pipeline Token** type
5. Copy the token (starts with `itk_p_`)

### 2. Add Secret to CI/CD Platform

Add the token as a secret/environment variable:

- GitHub Actions: `ILTERO_PIPELINE_TOKEN`
- GitLab CI: `ILTERO_PIPELINE_TOKEN`
- Jenkins: Use credentials manager
- Azure DevOps: Pipeline variable
- CircleCI: Environment variable

### 3. Install Scanners (Optional)

For local scanning:

```bash
pip install checkov  # Infrastructure as Code scanner
```

## GitHub Actions

### Basic Workflow

```yaml
name: Iltero Compliance

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  compliance-scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Iltero CLI
        run: pip install iltero-cli
      
      - name: Install scanners
        run: pip install checkov
      
      - name: Run compliance scan
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
          ILTERO_OUTPUT_FORMAT: json
        run: |
          iltero scan static \
            --path ./terraform \
            --format json \
            --output scan-results.json
      
      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: scan-results
          path: scan-results.json
      
      - name: Check for critical violations
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: |
          # Fail if critical violations found
          CRITICAL_COUNT=$(jq '.summary.critical // 0' scan-results.json)
          if [ "$CRITICAL_COUNT" -gt 0 ]; then
            echo "❌ Found $CRITICAL_COUNT critical violations"
            exit 1
          fi
          echo "✅ No critical violations found"
```

### Advanced Workflow with Stack Integration

```yaml
name: Iltero Stack Validation

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Iltero CLI
        run: pip install iltero-cli
      
      - name: Pre-plan validation
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: |
          iltero scan static \
            --path . \
            --stack-id ${{ vars.ILTERO_STACK_ID }} \
            --upload \
            --format sarif \
            --output iltero.sarif
      
      - name: Upload SARIF to GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: iltero.sarif
      
      - name: Generate Terraform plan
        run: |
          terraform init
          terraform plan -out=tfplan
      
      - name: Evaluate plan
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: |
          iltero stack plan \
            --stack-id ${{ vars.ILTERO_STACK_ID }} \
            --evaluate \
            --plan-file tfplan
```

### Matrix Testing

```yaml
name: Multi-Environment Testing

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, prod]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Iltero CLI
        run: pip install iltero-cli
      
      - name: Scan ${{ matrix.environment }}
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: |
          iltero scan static \
            --path ./terraform/${{ matrix.environment }} \
            --format json \
            --output ${{ matrix.environment }}-results.json
      
      - uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.environment }}-scan-results
          path: ${{ matrix.environment }}-results.json
```

## GitLab CI

### Basic Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - scan
  - report

variables:
  ILTERO_OUTPUT_FORMAT: json
  ILTERO_NO_COLOR: "true"

before_script:
  - pip install iltero-cli checkov

compliance-scan:
  stage: scan
  image: python:3.11
  script:
    - |
      iltero scan static \
        --path ./terraform \
        --format json \
        --output scan-results.json
    
    # Check thresholds
    - |
      CRITICAL=$(jq '.summary.critical // 0' scan-results.json)
      HIGH=$(jq '.summary.high // 0' scan-results.json)
      
      if [ "$CRITICAL" -gt 0 ]; then
        echo "❌ Found $CRITICAL critical violations"
        exit 1
      fi
      
      if [ "$HIGH" -gt 5 ]; then
        echo "❌ Found $HIGH high violations (threshold: 5)"
        exit 1
      fi
      
      echo "✅ Compliance check passed"
  
  artifacts:
    reports:
      junit: scan-results.xml
    paths:
      - scan-results.json
    expire_in: 30 days
  
  only:
    - merge_requests
    - main
```

### Multi-Stage Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - plan
  - evaluate
  - apply

validate:
  stage: validate
  image: python:3.11
  script:
    - pip install iltero-cli checkov
    - |
      iltero scan static \
        --path . \
        --stack-id ${ILTERO_STACK_ID} \
        --upload \
        --format sarif \
        --output iltero.sarif
  artifacts:
    paths:
      - iltero.sarif
  only:
    - merge_requests
    - main

plan:
  stage: plan
  image: hashicorp/terraform:latest
  script:
    - terraform init
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - tfplan
  only:
    - merge_requests
    - main

evaluate:
  stage: evaluate
  image: python:3.11
  dependencies:
    - plan
  script:
    - pip install iltero-cli
    - |
      iltero stack plan \
        --stack-id ${ILTERO_STACK_ID} \
        --evaluate \
        --plan-file tfplan
  only:
    - merge_requests
    - main

apply:
  stage: apply
  image: hashicorp/terraform:latest
  dependencies:
    - plan
  script:
    - terraform init
    - terraform apply tfplan
  when: manual
  only:
    - main
```

## Jenkins

### Declarative Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        ILTERO_TOKEN = credentials('iltero-pipeline-token')
        ILTERO_OUTPUT_FORMAT = 'json'
        ILTERO_NO_COLOR = 'true'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install iltero-cli checkov'
            }
        }
        
        stage('Compliance Scan') {
            steps {
                sh '''
                    iltero scan static \
                        --path ./terraform \
                        --format json \
                        --output scan-results.json
                '''
            }
        }
        
        stage('Check Thresholds') {
            steps {
                script {
                    def results = readJSON file: 'scan-results.json'
                    def critical = results.summary?.critical ?: 0
                    def high = results.summary?.high ?: 0
                    
                    if (critical > 0) {
                        error("Found ${critical} critical violations")
                    }
                    
                    if (high > 5) {
                        error("Found ${high} high violations (threshold: 5)")
                    }
                    
                    echo "✅ Compliance check passed"
                }
            }
        }
        
        stage('Upload Results') {
            steps {
                archiveArtifacts artifacts: 'scan-results.json'
                
                // Publish to Iltero backend
                sh '''
                    iltero scan static \
                        --path ./terraform \
                        --stack-id ${ILTERO_STACK_ID} \
                        --upload
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'scan-results.json', allowEmptyArchive: true
        }
        failure {
            echo 'Compliance scan failed!'
        }
    }
}
```

### Scripted Pipeline

```groovy
// Jenkinsfile
node {
    withCredentials([string(credentialsId: 'iltero-pipeline-token', variable: 'ILTERO_TOKEN')]) {
        stage('Checkout') {
            checkout scm
        }
        
        stage('Setup') {
            sh 'pip install iltero-cli checkov'
        }
        
        stage('Scan') {
            sh '''
                iltero scan static \
                    --path . \
                    --format json \
                    --output scan-results.json
            '''
        }
        
        stage('Evaluate') {
            def results = readJSON file: 'scan-results.json'
            
            if (results.summary.critical > 0) {
                error("Critical violations found")
            }
            
            echo "Scan passed!"
        }
    }
}
```

## Azure DevOps

### Pipeline YAML

```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  ILTERO_TOKEN: $(ILTERO_PIPELINE_TOKEN)
  ILTERO_OUTPUT_FORMAT: json
  ILTERO_NO_COLOR: true

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'
    displayName: 'Use Python 3.11'
  
  - script: |
      pip install iltero-cli checkov
    displayName: 'Install Iltero CLI'
  
  - script: |
      iltero scan static \
        --path ./terraform \
        --format json \
        --output $(Build.ArtifactStagingDirectory)/scan-results.json
    displayName: 'Run compliance scan'
    env:
      ILTERO_TOKEN: $(ILTERO_PIPELINE_TOKEN)
  
  - script: |
      CRITICAL=$(jq '.summary.critical // 0' $(Build.ArtifactStagingDirectory)/scan-results.json)
      if [ "$CRITICAL" -gt 0 ]; then
        echo "##vso[task.logissue type=error]Found $CRITICAL critical violations"
        exit 1
      fi
    displayName: 'Check thresholds'
  
  - task: PublishBuildArtifacts@1
    inputs:
      pathToPublish: '$(Build.ArtifactStagingDirectory)'
      artifactName: 'scan-results'
    condition: always()
```

## CircleCI

### Config

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  compliance-scan:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      
      - run:
          name: Install Iltero CLI
          command: pip install iltero-cli checkov
      
      - run:
          name: Run compliance scan
          command: |
            iltero scan static \
              --path ./terraform \
              --format json \
              --output scan-results.json
          environment:
            ILTERO_TOKEN: $ILTERO_PIPELINE_TOKEN
            ILTERO_OUTPUT_FORMAT: json
      
      - run:
          name: Check thresholds
          command: |
            CRITICAL=$(jq '.summary.critical // 0' scan-results.json)
            if [ "$CRITICAL" -gt 0 ]; then
              echo "Found $CRITICAL critical violations"
              exit 1
            fi
      
      - store_artifacts:
          path: scan-results.json
          destination: scan-results

workflows:
  version: 2
  compliance:
    jobs:
      - compliance-scan:
          context: iltero-credentials
```

## Bitbucket Pipelines

### Pipeline Config

```yaml
# bitbucket-pipelines.yml
image: python:3.11

pipelines:
  pull-requests:
    '**':
      - step:
          name: Compliance Scan
          caches:
            - pip
          script:
            - pip install iltero-cli checkov
            - |
              iltero scan static \
                --path ./terraform \
                --format json \
                --output scan-results.json
            - |
              CRITICAL=$(jq '.summary.critical // 0' scan-results.json)
              if [ "$CRITICAL" -gt 0 ]; then
                echo "❌ Found $CRITICAL critical violations"
                exit 1
              fi
          artifacts:
            - scan-results.json
  
  branches:
    main:
      - step:
          name: Compliance Scan & Upload
          caches:
            - pip
          script:
            - pip install iltero-cli checkov
            - |
              iltero scan static \
                --path ./terraform \
                --stack-id ${ILTERO_STACK_ID} \
                --upload \
                --format sarif \
                --output iltero.sarif
          artifacts:
            - iltero.sarif
```

## Best Practices

### 1. Use Pipeline Tokens

```bash
# Create dedicated pipeline token (itk_p_*)
# NOT personal tokens (itk_u_*)
```

### 2. Set Appropriate Thresholds

```bash
# Fail on critical
if [ "$CRITICAL" -gt 0 ]; then exit 1; fi

# Warn on high
if [ "$HIGH" -gt 10 ]; then
  echo "⚠️ Warning: $HIGH high severity violations"
fi
```

### 3. Cache Dependencies

```yaml
# GitHub Actions
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# GitLab CI
cache:
  paths:
    - .cache/pip
```

### 4. Use Output Formats

```bash
# SARIF for GitHub Security
--format sarif --output iltero.sarif

# JUnit for test reporting
--format junit --output results.xml

# JSON for custom processing
--format json --output results.json
```

### 5. Environment-Specific Configuration

```yaml
# Different stacks per environment
production:
  variables:
    ILTERO_STACK_ID: stk_prod_123

staging:
  variables:
    ILTERO_STACK_ID: stk_staging_456
```

### 6. Fail Fast

```bash
# Exit early on authentication errors
iltero auth status || exit 1

# Validate before expensive operations
iltero scanner check || exit 1
```

### 7. Secure Secrets

```bash
# ✅ Good - use platform secrets
ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}

# ❌ Bad - hardcoded token
ILTERO_TOKEN: itk_p_hardcoded_token
```

### 8. Artifact Retention

```yaml
# Keep scan results for auditing
artifacts:
  reports:
    junit: results.xml
  paths:
    - scan-results.json
  expire_in: 90 days
```

## Troubleshooting

### Authentication Fails in CI/CD

```bash
# Debug authentication
iltero --debug auth status

# Verify token is set
echo "Token set: ${ILTERO_TOKEN:+yes}"

# Check token format
echo "${ILTERO_TOKEN}" | grep -q "^itk_p_" && echo "Valid pipeline token"
```

### Scanner Not Found

```bash
# Verify scanner installation
which checkov
checkov --version

# Install if missing
pip install checkov
```

### Timeout Issues

```bash
# Increase timeout
export ILTERO_SCAN_TIMEOUT=600
export ILTERO_REQUEST_TIMEOUT=60
```

### Output Format Issues

```bash
# Disable colors for logs
export ILTERO_NO_COLOR=true

# Use JSON for parsing
export ILTERO_OUTPUT_FORMAT=json
```

## Example: Complete GitHub Actions Workflow

```yaml
name: Full Iltero CI/CD

on:
  pull_request:
  push:
    branches: [main]

env:
  ILTERO_OUTPUT_FORMAT: json
  ILTERO_NO_COLOR: true

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Cache pip
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-iltero
      
      - name: Install tools
        run: |
          pip install iltero-cli checkov
          iltero --version
      
      - name: Verify authentication
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: iltero auth status
      
      - name: Check scanners
        run: iltero scanner check
      
      - name: Run static scan
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: |
          iltero scan static \
            --path . \
            --format sarif \
            --output iltero.sarif
      
      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: iltero.sarif
      
      - name: Check compliance
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: |
          iltero scan static \
            --path . \
            --format json \
            --output results.json
          
          CRITICAL=$(jq '.summary.critical // 0' results.json)
          HIGH=$(jq '.summary.high // 0' results.json)
          
          echo "Critical: $CRITICAL"
          echo "High: $HIGH"
          
          if [ "$CRITICAL" -gt 0 ]; then
            echo "::error::Found $CRITICAL critical violations"
            exit 1
          fi
          
          if [ "$HIGH" -gt 5 ]; then
            echo "::warning::Found $HIGH high violations (threshold: 5)"
          fi
      
      - name: Upload to Iltero
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        env:
          ILTERO_TOKEN: ${{ secrets.ILTERO_PIPELINE_TOKEN }}
        run: |
          iltero scan static \
            --path . \
            --stack-id ${{ vars.ILTERO_STACK_ID }} \
            --upload
```

## See Also

- [Getting Started Guide](GETTING_STARTED.md)
- [Configuration Guide](CONFIGURATION.md)
- [Command Reference](COMMAND_REFERENCE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

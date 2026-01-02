# Azure DevOps Integration

Complete guide for integrating Iltero CLI with Azure Pipelines.

## Prerequisites

1. Create pipeline token: `iltero token create --type pipeline`
2. Add to Azure DevOps:
   - Go to **Pipelines** → **Library** → **Variable groups**
   - Create variable: `ILTERO_PIPELINE_TOKEN`
   - Mark as **Secret**

## Basic Pipeline

Create `azure-pipelines.yml`:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  ILTERO_OUTPUT_FORMAT: json
  ILTERO_NO_COLOR: true

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'
    displayName: 'Use Python 3.11'
  
  - script: pip install iltero-cli checkov
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

## Multi-Stage Pipeline

```yaml
stages:
  - stage: Scan
    jobs:
      - job: ComplianceScan
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.11'
          
          - script: pip install iltero-cli checkov
            displayName: 'Install tools'
          
          - script: iltero scan static --path . --format json
            displayName: 'Scan'
            env:
              ILTERO_TOKEN: $(ILTERO_PIPELINE_TOKEN)
```

## See Also

- [CI/CD Overview](README.md)
- [Scan Commands](../commands/scan.md)

# Jenkins Integration

Complete guide for integrating Iltero CLI with Jenkins.

## Prerequisites

1. Create pipeline token: `iltero token create --type pipeline`
2. Add to Jenkins credentials:
   - Go to **Manage Jenkins** → **Credentials**
   - Add **Secret text** credential
   - ID: `iltero-pipeline-token`
   - Secret: Your token

## Declarative Pipeline

Create `Jenkinsfile`:

```groovy
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
        
        stage('Scan') {
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
                    
                    if (critical > 0) {
                        error("Found ${critical} critical violations")
                    }
                    
                    echo "✅ Compliance check passed"
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'scan-results.json', allowEmptyArchive: true
        }
    }
}
```

## Scripted Pipeline

```groovy
node {
    withCredentials([string(credentialsId: 'iltero-pipeline-token', variable: 'ILTERO_TOKEN')]) {
        stage('Checkout') {
            checkout scm
        }
        
        stage('Setup') {
            sh 'pip install iltero-cli checkov'
        }
        
        stage('Scan') {
            sh 'iltero scan static --path . --format json --output results.json'
        }
        
        stage('Evaluate') {
            def results = readJSON file: 'results.json'
            
            if (results.summary.critical > 0) {
                error("Critical violations found")
            }
        }
    }
}
```

## See Also

- [CI/CD Overview](README.md)
- [Scan Commands](../commands/scan.md)

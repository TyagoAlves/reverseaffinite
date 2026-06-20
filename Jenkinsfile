pipeline {
    agent { label 'linux' }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        PYTHON_VERSION = '3.10'
        QT_QPA_PLATFORM = 'offscreen'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3.10 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pytest-timeout pytest-qt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    xvfb-run python3 -m pytest tests/ \
                        --cov=editor \
                        --cov-report=term \
                        --cov-report=xml \
                        -v --tb=short \
                        -m 'not slow and not stress and not perf'
                '''
            }
        }

        stage('Coverage Report') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -m pytest tests/ \
                        --cov=editor \
                        --cov-report=html \
                        -m 'not slow and not stress and not perf'
                '''
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
        }
    }

    post {
        always {
            junit 'coverage.xml'
            cleanWs()
        }
    }
}

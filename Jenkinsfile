pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'devops-platform:ci'
        COMPOSE_PROJECT_NAME = 'self-hosted-devops-platform'
    }

    stages {
        stage('Checkout') {
            steps {
                dir('/workspace') {
                    sh 'git status --short'
                    sh 'test -f app/requirements.txt'
                    sh 'test -f app/tests/test_app.py'
                }
            }
        }

        stage('Unit Tests') {
            steps {
                dir('/workspace') {
                    sh '''
                        python3 -m venv /tmp/ci-venv
                        /tmp/ci-venv/bin/python -m pip install \
                          --no-cache-dir -r app/requirements.txt
                        /tmp/ci-venv/bin/python -m pytest app/tests -v
                    '''
                }
            }
        }

        stage('Build Image') {
            steps {
                dir('/workspace') {
                    sh 'docker build -t "$IMAGE_NAME" .'
                }
            }
        }

        stage('Deploy') {
            steps {
                dir('/workspace') {
                    sh 'docker compose up -d --build db app'
                }
            }
        }

        stage('Smoke Test') {
            steps {
                dir('/workspace') {
                    sh '''
                        for attempt in $(seq 1 20); do
                          if curl -fsS http://app:5000/health; then
                            echo "Smoke test passed"
                            exit 0
                          fi
                          sleep 3
                        done

                        echo "Application health check failed"
                        docker compose logs --tail=100 app db
                        exit 1
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Review the stage results above.'
        }
    }
}

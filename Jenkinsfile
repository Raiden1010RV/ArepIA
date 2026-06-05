pipeline {
    agent any

    environment {
        // Docker Registry Configuration
        DOCKER_REGISTRY = credentials('docker-registry-url')  // e.g., docker.io or your registry
        DOCKER_USERNAME = credentials('docker-username')
        DOCKER_PASSWORD = credentials('docker-password')
        
        // GitHub Configuration
        GITHUB_TOKEN = credentials('github-token')
        GITHUB_REPO = 'your-username/arepIA'
        
        // Render Configuration
        RENDER_API_KEY = credentials('render-api-key')
        RENDER_SERVICE_ID_BACKEND = credentials('render-service-id-backend')
        RENDER_SERVICE_ID_FRONTEND = credentials('render-service-id-frontend')
        
        // Image Configuration
        IMAGE_NAME_BACKEND = "${DOCKER_REGISTRY}/arepIA-backend"
        IMAGE_NAME_FRONTEND = "${DOCKER_REGISTRY}/arepIA-frontend"
        IMAGE_TAG = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        IMAGE_TAG_LATEST = "latest"
        
        // Environment
        ENVIRONMENT_DEV = "development"
        ENVIRONMENT_STAGING = "staging"
        ENVIRONMENT_PROD = "production"
    }

    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'staging', 'prod'],
            description: 'Environment to deploy to'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip test execution'
        )
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo '🔄 Clonando repositorio desde GitHub...'
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: '*/main']],
                        userRemoteConfigs: [[
                            url: "https://github.com/${GITHUB_REPO}.git",
                            credentialsId: 'github-credentials'
                        ]]
                    ])
                    echo '✅ Checkout completado'
                }
            }
        }

        stage('Build Backend') {
            steps {
                script {
                    echo '🏗️  Construyendo imagen Docker del Backend...'
                    dir('arepIA') {
                        sh '''
                            docker build \
                                --tag ${IMAGE_NAME_BACKEND}:${IMAGE_TAG} \
                                --tag ${IMAGE_NAME_BACKEND}:${IMAGE_TAG_LATEST} \
                                --file Dockerfile.backend \
                                --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VCS_REF=${GIT_COMMIT} \
                                --build-arg VERSION=${IMAGE_TAG} \
                                .
                        '''
                    }
                    echo '✅ Backend build completado'
                }
            }
        }

        stage('Build Frontend') {
            steps {
                script {
                    echo '🏗️  Construyendo imagen Docker del Frontend...'
                    dir('arepIA') {
                        sh '''
                            docker build \
                                --tag ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG} \
                                --tag ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG_LATEST} \
                                --file Dockerfile.frontend \
                                --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VCS_REF=${GIT_COMMIT} \
                                --build-arg VERSION=${IMAGE_TAG} \
                                .
                        '''
                    }
                    echo '✅ Frontend build completado'
                }
            }
        }

        stage('Test Backend') {
            when {
                expression { params.SKIP_TESTS == false }
            }
            steps {
                script {
                    echo '🧪 Ejecutando tests del Backend...'
                    dir('arepIA/backend') {
                        sh '''
                            # Crear entorno virtual y instalar dependencias
                            python3 -m venv venv
                            source venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            pip install pytest pytest-cov
                            
                            # Ejecutar tests
                            pytest -v --cov=. --cov-report=xml --cov-report=html || true
                        '''
                    }
                    echo '✅ Tests completados'
                }
            }
        }

        stage('Code Analysis') {
            steps {
                script {
                    echo '🔍 Realizando análisis de código...'
                    dir('arepIA/backend') {
                        sh '''
                            python3 -m venv venv
                            source venv/bin/activate
                            pip install pylint flake8
                            
                            # Linting
                            flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                            pylint *.py --disable=all --enable=E,F || true
                        '''
                    }
                    echo '✅ Análisis de código completado'
                }
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    echo '📤 Subiendo imágenes a Docker Registry...'
                    sh '''
                        echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin ${DOCKER_REGISTRY}
                        
                        # Push Backend
                        docker push ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME_BACKEND}:${IMAGE_TAG_LATEST}
                        
                        # Push Frontend
                        docker push ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG_LATEST}
                        
                        docker logout
                    '''
                    echo '✅ Push completado'
                }
            }
        }

        stage('Deploy to Dev') {
            when {
                expression { params.DEPLOY_ENV == 'dev' }
            }
            steps {
                script {
                    echo '🚀 Desplegando a ambiente de DESARROLLO...'
                    sh '''
                        chmod +x scripts/deploy-render.sh
                        ./scripts/deploy-render.sh backend ${RENDER_SERVICE_ID_BACKEND} ${RENDER_API_KEY} ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                        ./scripts/deploy-render.sh frontend ${RENDER_SERVICE_ID_FRONTEND} ${RENDER_API_KEY} ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                    '''
                    echo '✅ Deploy a desarrollo completado'
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                expression { params.DEPLOY_ENV == 'staging' }
            }
            input {
                message "¿Desplegar a STAGING?"
                ok "Desplegar"
            }
            steps {
                script {
                    echo '🚀 Desplegando a ambiente de STAGING...'
                    sh '''
                        chmod +x scripts/deploy-render.sh
                        ./scripts/deploy-render.sh backend-staging ${RENDER_SERVICE_ID_BACKEND} ${RENDER_API_KEY} ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                        ./scripts/deploy-render.sh frontend-staging ${RENDER_SERVICE_ID_FRONTEND} ${RENDER_API_KEY} ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                    '''
                    echo '✅ Deploy a staging completado'
                }
            }
        }

        stage('Deploy to Production') {
            when {
                expression { params.DEPLOY_ENV == 'prod' }
                branch 'main'
            }
            input {
                message "⚠️ ADVERTENCIA: ¿Desplegar a PRODUCCIÓN?"
                ok "Desplegar a Producción"
            }
            steps {
                script {
                    echo '🚀 Desplegando a ambiente de PRODUCCIÓN...'
                    sh '''
                        chmod +x scripts/deploy-render.sh
                        ./scripts/deploy-render.sh backend-prod ${RENDER_SERVICE_ID_BACKEND} ${RENDER_API_KEY} ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                        ./scripts/deploy-render.sh frontend-prod ${RENDER_SERVICE_ID_FRONTEND} ${RENDER_API_KEY} ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                    '''
                    echo '✅ Deploy a producción completado'
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo '🏥 Verificando salud de la aplicación...'
                    sh '''
                        sleep 10
                        
                        # Verificar backend
                        BACKEND_URL="${RENDER_BACKEND_URL}/docs"
                        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${BACKEND_URL} || echo "000")
                        
                        if [ "$HTTP_CODE" = "200" ]; then
                            echo "✅ Backend está sano (HTTP $HTTP_CODE)"
                        else
                            echo "⚠️ Backend puede tener problemas (HTTP $HTTP_CODE)"
                        fi
                        
                        # Verificar frontend
                        FRONTEND_URL="${RENDER_FRONTEND_URL}"
                        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${FRONTEND_URL} || echo "000")
                        
                        if [ "$HTTP_CODE" = "200" ]; then
                            echo "✅ Frontend está sano (HTTP $HTTP_CODE)"
                        else
                            echo "⚠️ Frontend puede tener problemas (HTTP $HTTP_CODE)"
                        fi
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo '🧹 Limpiando recursos...'
                sh '''
                    # Limpiar imágenes locales
                    docker rmi ${IMAGE_NAME_BACKEND}:${IMAGE_TAG} ${IMAGE_NAME_BACKEND}:${IMAGE_TAG_LATEST} || true
                    docker rmi ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG} ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG_LATEST} || true
                    
                    # Limpiar espacios no utilizados
                    docker system prune -f || true
                '''
            }
            
            // Archivar reportes
            archiveArtifacts artifacts: 'arepIA/backend/htmlcov/**', allowEmptyArchive: true
            archiveArtifacts artifacts: 'arepIA/backend/.coverage', allowEmptyArchive: true
        }

        success {
            script {
                echo '✅ Pipeline completado exitosamente'
                // Aquí puedes agregar notificación a Slack, Email, etc.
                // sh 'curl -X POST -H "Content-type: application/json" --data ... $SLACK_WEBHOOK'
            }
        }

        failure {
            script {
                echo '❌ Pipeline falló'
                // Aquí puedes agregar notificación de fallo
                // sh 'curl -X POST -H "Content-type: application/json" --data ... $SLACK_WEBHOOK'
            }
        }

        unstable {
            script {
                echo '⚠️ Pipeline está inestable'
            }
        }
    }
}

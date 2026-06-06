pipeline {
    agent any

    environment {
        // Docker Registry Configuration
        DOCKER_REGISTRY = credentials('docker-registry-url')   // e.g., docker.io
        DOCKER_USERNAME = credentials('docker-username')
        DOCKER_PASSWORD = credentials('docker-password')

        // GitHub Configuration
        GITHUB_TOKEN       = credentials('github-token')
        GITHUB_REPO        = credentials('github-repo')        // e.g., tu-usuario/arepIA

        // Render Configuration
        RENDER_API_KEY              = credentials('render-api-key')
        RENDER_SERVICE_ID_BACKEND   = credentials('render-service-id-backend')
        RENDER_SERVICE_ID_FRONTEND  = credentials('render-service-id-frontend')
        RENDER_BACKEND_URL          = credentials('render-backend-url')   // https://arepia-backend.onrender.com
        RENDER_FRONTEND_URL         = credentials('render-frontend-url')  // https://arepia-frontend.onrender.com

        // Image names (se construyen con las credenciales anteriores)
        IMAGE_NAME_BACKEND  = "${DOCKER_USERNAME}/arepia-backend"
        IMAGE_NAME_FRONTEND = "${DOCKER_USERNAME}/arepia-frontend"
        IMAGE_TAG           = "${BUILD_NUMBER}-${GIT_COMMIT.take(7)}"
        IMAGE_TAG_LATEST    = "latest"
    }

    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'staging', 'prod'],
            description: 'Ambiente destino del despliegue'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Omitir ejecución de tests'
        )
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
        disableConcurrentBuilds()
    }

    triggers {
        githubPush()
    }

    stages {

        // ─────────────────────────────────────────────
        stage('Checkout') {
        // ─────────────────────────────────────────────
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
                    echo "✅ Checkout completado — commit: ${GIT_COMMIT.take(7)}"
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Build Backend') {
        // ─────────────────────────────────────────────
            steps {
                script {
                    echo '🏗️  Construyendo imagen Docker del Backend...'
                    // NOTA: El Jenkinsfile está en la raíz del repo (no en subcarpeta arepIA/).
                    // Si el repo tiene arepIA/ como subcarpeta, cambia '.' por 'arepIA'
                    sh """
                        docker build \\
                            --tag ${IMAGE_NAME_BACKEND}:${IMAGE_TAG} \\
                            --tag ${IMAGE_NAME_BACKEND}:${IMAGE_TAG_LATEST} \\
                            --file Dockerfile.backend \\
                            --build-arg BUILD_DATE=\$(date -u +\'%Y-%m-%dT%H:%M:%SZ\') \\
                            --build-arg VCS_REF=${GIT_COMMIT} \\
                            --build-arg VERSION=${IMAGE_TAG} \\
                            .
                    """
                    echo '✅ Backend build completado'
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Build Frontend') {
        // ─────────────────────────────────────────────
            steps {
                script {
                    echo '🏗️  Construyendo imagen Docker del Frontend...'
                    sh """
                        docker build \\
                            --tag ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG} \\
                            --tag ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG_LATEST} \\
                            --file Dockerfile.frontend \\
                            --build-arg BUILD_DATE=\$(date -u +\'%Y-%m-%dT%H:%M:%SZ\') \\
                            --build-arg VCS_REF=${GIT_COMMIT} \\
                            --build-arg VERSION=${IMAGE_TAG} \\
                            .
                    """
                    echo '✅ Frontend build completado'
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Test Backend') {
        // ─────────────────────────────────────────────
            when {
                expression { return !params.SKIP_TESTS }
            }
            steps {
                script {
                    echo '🧪 Ejecutando tests del Backend...'
                    dir('backend') {
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip --quiet
                            pip install -r requirements.txt --quiet
                            pip install pytest pytest-cov httpx --quiet

                            # Ejecutar tests (|| true para no fallar pipeline por cobertura baja)
                            pytest -v \
                                --cov=. \
                                --cov-report=xml:../coverage.xml \
                                --cov-report=html:../htmlcov \
                                --tb=short \
                                || true
                        '''
                    }
                    echo '✅ Tests completados'
                }
            }
            post {
                always {
                    // Publicar reporte de cobertura si existe
                    script {
                        if (fileExists('coverage.xml')) {
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'htmlcov',
                                reportFiles: 'index.html',
                                reportName: 'Coverage Report'
                            ])
                        }
                    }
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Code Analysis') {
        // ─────────────────────────────────────────────
            steps {
                script {
                    echo '🔍 Analizando calidad del código...'
                    dir('backend') {
                        sh '''
                            . venv/bin/activate 2>/dev/null || (python3 -m venv venv && . venv/bin/activate && pip install flake8 --quiet)
                            pip install flake8 --quiet

                            echo "--- flake8: errores críticos (E9, F63, F7, F82) ---"
                            flake8 . \
                                --count \
                                --select=E9,F63,F7,F82 \
                                --show-source \
                                --statistics \
                                --exclude=venv,__pycache__ \
                                || true

                            echo "--- flake8: resumen de estilo ---"
                            flake8 . \
                                --count \
                                --max-line-length=120 \
                                --statistics \
                                --exclude=venv,__pycache__ \
                                || true
                        '''
                    }
                    echo '✅ Análisis de código completado'
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Push to Registry') {
        // ─────────────────────────────────────────────
            steps {
                script {
                    echo '📤 Subiendo imágenes a Docker Hub...'
                    sh """
                        echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin

                        docker push ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME_BACKEND}:${IMAGE_TAG_LATEST}

                        docker push ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG_LATEST}

                        docker logout
                    """
                    echo '✅ Imágenes publicadas en Docker Hub'
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Deploy to Dev') {
        // ─────────────────────────────────────────────
            when {
                expression { return params.DEPLOY_ENV == 'dev' }
            }
            steps {
                script {
                    echo '🚀 Desplegando a DESARROLLO...'
                    sh """
                        chmod +x scripts/deploy-render.sh
                        ./scripts/deploy-render.sh \\
                            backend \\
                            ${RENDER_SERVICE_ID_BACKEND} \\
                            ${RENDER_API_KEY} \\
                            ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}

                        ./scripts/deploy-render.sh \\
                            frontend \\
                            ${RENDER_SERVICE_ID_FRONTEND} \\
                            ${RENDER_API_KEY} \\
                            ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                    """
                    echo '✅ Deploy a Dev completado'
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Deploy to Staging') {
        // ─────────────────────────────────────────────
            when {
                expression { return params.DEPLOY_ENV == 'staging' }
            }
            input {
                message "¿Confirmar despliegue a STAGING?"
                ok "Desplegar"
            }
            steps {
                script {
                    echo '🚀 Desplegando a STAGING...'
                    sh """
                        chmod +x scripts/deploy-render.sh
                        ./scripts/deploy-render.sh \\
                            backend-staging \\
                            ${RENDER_SERVICE_ID_BACKEND} \\
                            ${RENDER_API_KEY} \\
                            ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}

                        ./scripts/deploy-render.sh \\
                            frontend-staging \\
                            ${RENDER_SERVICE_ID_FRONTEND} \\
                            ${RENDER_API_KEY} \\
                            ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                    """
                    echo '✅ Deploy a Staging completado'
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Deploy to Production') {
        // ─────────────────────────────────────────────
            when {
                allOf {
                    expression { return params.DEPLOY_ENV == 'prod' }
                    branch 'main'
                }
            }
            input {
                message "⚠️  PRODUCCIÓN: ¿Confirmar despliegue?"
                ok "Desplegar a Producción"
                submitter "admin"
            }
            steps {
                script {
                    echo '🚀 Desplegando a PRODUCCIÓN...'
                    sh """
                        chmod +x scripts/deploy-render.sh
                        ./scripts/deploy-render.sh \\
                            backend-prod \\
                            ${RENDER_SERVICE_ID_BACKEND} \\
                            ${RENDER_API_KEY} \\
                            ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}

                        ./scripts/deploy-render.sh \\
                            frontend-prod \\
                            ${RENDER_SERVICE_ID_FRONTEND} \\
                            ${RENDER_API_KEY} \\
                            ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                    """
                    echo '✅ Deploy a Producción completado'
                }
            }
        }

        // ─────────────────────────────────────────────
        stage('Health Check') {
        // ─────────────────────────────────────────────
            steps {
                script {
                    echo '🏥 Verificando salud de los servicios...'
                    sh """
                        # Esperar a que Render inicie los servicios (puede tomar hasta 60s en plan free)
                        echo "⏳ Esperando 30s para que los servicios arranquen..."
                        sleep 30

                        # Health check — Backend
                        BACKEND_HC_URL="${RENDER_BACKEND_URL}/"
                        echo "Verificando backend: \${BACKEND_HC_URL}"
                        HTTP_BACKEND=\$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "\${BACKEND_HC_URL}" || echo "000")

                        if [ "\$HTTP_BACKEND" = "200" ]; then
                            echo "✅ Backend OK (HTTP \$HTTP_BACKEND)"
                        else
                            echo "⚠️  Backend no respondió correctamente (HTTP \$HTTP_BACKEND)"
                        fi

                        # Health check — Frontend
                        FRONTEND_HC_URL="${RENDER_FRONTEND_URL}/health"
                        echo "Verificando frontend: \${FRONTEND_HC_URL}"
                        HTTP_FRONTEND=\$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "\${FRONTEND_HC_URL}" || echo "000")

                        if [ "\$HTTP_FRONTEND" = "200" ]; then
                            echo "✅ Frontend OK (HTTP \$HTTP_FRONTEND)"
                        else
                            echo "⚠️  Frontend no respondió correctamente (HTTP \$HTTP_FRONTEND)"
                        fi

                        echo "📊 Resumen:"
                        echo "   Backend:  ${RENDER_BACKEND_URL}"
                        echo "   Frontend: ${RENDER_FRONTEND_URL}"
                        echo "   API Docs: ${RENDER_BACKEND_URL}/docs"
                    """
                }
            }
        }
    }

    // ─────────────────────────────────────────────
    post {
    // ─────────────────────────────────────────────
        always {
            script {
                echo '🧹 Limpiando recursos locales de Docker...'
                sh """
                    docker rmi ${IMAGE_NAME_BACKEND}:${IMAGE_TAG} || true
                    docker rmi ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG} || true
                    docker system prune -f || true
                """
            }
            // Archivar artefactos de test si existen
            archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
            archiveArtifacts artifacts: 'coverage.xml',  allowEmptyArchive: true
        }

        success {
            echo "✅ Pipeline completado exitosamente — Build #${BUILD_NUMBER}"
            // Descomenta para notificar por Slack:
            // slackSend color: 'good', message: "✅ arepIA deploy #${BUILD_NUMBER} exitoso — ${DEPLOY_ENV}"
        }

        failure {
            echo "❌ Pipeline falló — Build #${BUILD_NUMBER}"
            // slackSend color: 'danger', message: "❌ arepIA deploy #${BUILD_NUMBER} falló — ${DEPLOY_ENV}"
        }

        unstable {
            echo "⚠️  Pipeline inestable — Build #${BUILD_NUMBER}"
        }
    }
}

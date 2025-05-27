pipeline {
    agent any

    tools {
        python 'Python3'       // 你在 Jenkins 全局配置中注册的 Python 名字
    }

    environment {
        VENV_DIR = 'venv'     // 虚拟环境目录
        ALLURE_RESULTS = 'tests/results/allure-results'
        ALLURE_REPORT = 'tests/results/allure-report'
    }

    stages {

        stage('Clone') {
            steps {
                echo '✅ 拉取代码'
                checkout scm
            }
        }

        stage('Setup Python Env') {
            steps {
                echo '🐍 创建虚拟环境并安装依赖'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    source ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 执行测试用例'
                sh '''
                    source ${VENV_DIR}/bin/activate
                    pytest tests/ --alluredir=${ALLURE_RESULTS}
                '''
            }
        }

        stage('Generate Allure Report') {
            steps {
                echo '📊 生成 Allure 报告'
                allure includeProperties: false, jdk: '', results: [[path: "${ALLURE_RESULTS}"]]
            }
        }
    }

    post {
        always {
            echo '🎉 构建完成，清理环境（如需要）'
        }
        failure {
            echo '❌ 构建失败，请检查日志'
        }
    }
}

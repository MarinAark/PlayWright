pipeline {
    agent any

    environment {
        VENV_DIR = '.venv'
        ALLURE_RESULTS = 'results/allure-results'
        PYTHON_VERSION = '3.8'
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
                    playwright install
                '''
            }
        }
        
        stage('Check Allure Tool') {
            steps {
                echo '🔧 检查Allure工具'
                script {
                    try {
                        // 检查Allure是否可用
                        def allureVersion = sh(
                            script: 'allure --version',
                            returnStdout: true
                        ).trim()
                        echo "✅ Allure工具可用，版本: ${allureVersion}"
                    } catch (Exception e) {
                        echo "❌ Allure工具不可用: ${e.getMessage()}"
                        echo "💡 请确保在Jenkins系统配置中正确配置了Allure命令行工具"
                        echo "📋 配置路径: Manage Jenkins → Configure System → Allure Commandline"
                        
                        // 尝试查找Allure安装
                        sh '''
                            echo "🔍 查找Allure安装..."
                            which allure || echo "Allure不在PATH中"
                            find /opt -name "allure" 2>/dev/null || echo "未找到/opt/allure"
                            find /usr/local -name "allure" 2>/dev/null || echo "未找到/usr/local/allure"
                        '''
                        
                        // 不抛出错误，让流水线继续执行
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 执行测试用例'
                script {
                    try {
                        sh '''
                            source ${VENV_DIR}/bin/activate
                            
                            # 显示环境信息
                            echo "🔍 环境信息:"
                            echo "Python版本: $(python3 --version)"
                            echo "Pytest版本: $(pytest --version)"
                            echo "当前目录: $(pwd)"
                            
                            # 确保结果目录存在
                            mkdir -p results
                            mkdir -p screenshots
                            
                            # 清理之前的测试结果
                            rm -rf ${ALLURE_RESULTS}
                            
                            # 运行所有测试并生成Allure结果
                            echo "🚀 开始执行测试..."
                            pytest tests/ -v --alluredir=${ALLURE_RESULTS} --html=results/report.html --self-contained-html --tb=short
                            
                            # 显示测试结果摘要
                            echo "✅ 测试执行完成"
                            echo "📁 结果目录: ${ALLURE_RESULTS}"
                            
                            # 检查Allure结果
                            if [ -d "${ALLURE_RESULTS}" ]; then
                                echo "📊 Allure结果目录内容:"
                                ls -la ${ALLURE_RESULTS}
                                
                                # 统计结果文件数量
                                xml_count=$(find ${ALLURE_RESULTS} -name "*.xml" | wc -l)
                                json_count=$(find ${ALLURE_RESULTS} -name "*.json" | wc -l)
                                echo "📈 找到 ${xml_count} 个XML文件和 ${json_count} 个JSON文件"
                            else
                                echo "❌ Allure结果目录未创建"
                            fi
                            
                            # 检查HTML报告
                            if [ -f "results/report.html" ]; then
                                echo "📄 HTML报告已生成: results/report.html"
                                echo "📏 文件大小: $(du -h results/report.html | cut -f1)"
                            else
                                echo "❌ HTML报告未生成"
                            fi
                        '''
                    } catch (Exception e) {
                        echo "❌ 测试执行失败: ${e.getMessage()}"
                        echo "🔍 尝试获取更多调试信息..."
                        
                        // 即使测试失败，也尝试生成部分报告
                        sh '''
                            source ${VENV_DIR}/bin/activate
                            echo "📊 检查是否有部分测试结果..."
                            if [ -d "${ALLURE_RESULTS}" ]; then
                                echo "发现部分结果，尝试生成报告..."
                                ls -la ${ALLURE_RESULTS}
                            fi
                        '''
                        
                        // 不抛出错误，让流水线继续执行
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                echo '📊 生成 Allure 报告'
                script {
                    // 检查Allure结果目录和文件
                    def allureDir = "${ALLURE_RESULTS}"
                    def allureFiles = []
                    
                    if (fileExists(allureDir)) {
                        // 检查目录中的文件
                        allureFiles = sh(
                            script: "find ${allureDir} -name '*.xml' -o -name '*.json' | wc -l",
                            returnStdout: true
                        ).trim()
                        
                        echo "📁 Allure结果目录存在: ${allureDir}"
                        echo "📊 找到 ${allureFiles} 个结果文件"
                        
                        if (allureFiles.toInteger() > 0) {
                            echo "✅ Allure结果文件存在，开始生成报告"
                            allure includeProperties: false, jdk: '', results: [[path: allureDir]]
                        } else {
                            echo "⚠️  Allure结果目录存在但为空，尝试重新生成"
                            // 尝试重新运行测试生成结果
                            sh '''
                                source ${VENV_DIR}/bin/activate
                                pytest tests/ -v --alluredir=${ALLURE_RESULTS} --tb=short
                            '''
                            // 再次检查
                            allureFiles = sh(
                                script: "find ${allureDir} -name '*.xml' -o -name '*.json' | wc -l",
                                returnStdout: true
                            ).trim()
                            
                            if (allureFiles.toInteger() > 0) {
                                echo "✅ 重新生成Allure结果成功，开始生成报告"
                                allure includeProperties: false, jdk: '', results: [[path: allureDir]]
                            } else {
                                error "无法生成Allure报告，测试可能完全失败"
                            }
                        }
                    } else {
                        echo "❌ Allure结果目录不存在: ${allureDir}"
                        echo "🔍 检查当前工作目录内容:"
                        sh 'pwd && ls -la'
                        error "无法生成Allure报告，测试可能失败或未生成结果"
                    }
                }
            }
        }
        
        stage('Archive Test Results') {
            steps {
                echo '📁 归档测试结果'
                script {
                    // 归档HTML报告
                    if (fileExists("results/report.html")) {
                        archiveArtifacts artifacts: 'results/report.html', fingerprint: true
                        echo "✅ HTML报告已归档"
                    }
                    
                    // 归档测试数据
                    if (fileExists("test_data")) {
                        archiveArtifacts artifacts: 'test_data/**/*.json', fingerprint: true
                        echo "✅ 测试数据已归档"
                    }
                    
                    // 归档截图（如果有）
                    if (fileExists("screenshots")) {
                        archiveArtifacts artifacts: 'screenshots/**/*.png', fingerprint: true
                        echo "✅ 测试截图已归档"
                    }
                }
            }
        }
    }

    post {
        always {
            echo '✅ 构建结束，尝试发送邮件'
            
            script {
                // 构建邮件内容
                def emailBody = """
构建结果：${currentBuild.currentResult}
项目名称：${env.JOB_NAME}
构建编号：#${env.BUILD_NUMBER}
构建者：${env.BUILD_USER_ID ?: '未知用户'}
构建链接：${env.BUILD_URL}

测试结果：
- Allure报告：${env.BUILD_URL}allure/
- HTML报告：${env.BUILD_URL}artifact/results/report.html

请登录 Jenkins 查看详情。
                """
                
                try {
                    emailext (
                        to: '330354280@qq.com',
                        subject: "${currentBuild.currentResult}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: emailBody,
                        mimeType: 'text/plain'
                    )
                    echo "✅ 邮件发送成功"
                } catch (e) {
                    echo "❌ 邮件发送失败: ${e.getMessage()}"
                }
            }
        }
        
        success {
            echo '🎉 构建成功！'
            script {
                if (fileExists("${ALLURE_RESULTS}")) {
                    echo "📊 Allure报告已生成，可在Jenkins中查看"
                }
            }
        }
        
        failure {
            echo '❌ 构建失败！'
            script {
                echo "构建失败原因可能是："
                echo "1. 测试用例执行失败"
                echo "2. 依赖安装失败"
                echo "3. Allure结果生成失败"
                echo "4. Allure工具未正确配置"
                echo ""
                echo "🔍 调试信息:"
                echo "当前工作目录: ${env.WORKSPACE}"
                echo "Allure结果路径: ${env.ALLURE_RESULTS}"
                
                // 检查文件系统
                sh '''
                    echo "📁 工作目录内容:"
                    pwd && ls -la
                    
                    echo "📁 results目录内容:"
                    ls -la results/ || echo "results目录不存在"
                    
                    echo "📁 Allure结果目录内容:"
                    ls -la ${ALLURE_RESULTS}/ || echo "Allure结果目录不存在"
                '''
                
                echo "请检查Jenkins控制台输出获取详细信息"
            }
        }
        
        unstable {
            echo '⚠️  构建不稳定！'
            script {
                echo "构建不稳定的原因可能是："
                echo "1. 部分测试失败但生成了结果"
                echo "2. Allure工具配置问题"
                echo "3. 测试结果不完整"
                echo ""
                echo "📊 当前状态:"
                if (fileExists("${env.ALLURE_RESULTS}")) {
                    echo "✅ Allure结果目录存在"
                    sh "ls -la ${env.ALLURE_RESULTS}/"
                } else {
                    echo "❌ Allure结果目录不存在"
                }
            }
        }
    }
}
#!/bin/env python
#encoding:utf8
# source xxx.env && python initcompose.py
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

LARADOCK_DIR = 'laradock'
DOCER_COMPOSE = 'docker-compose.yml'
MODULE_NAME = ['version', 'services', 'networks']
SERVICE_NAME = ['applications','workspace','php-fpm','nginx','redis']

def say(msg):
    print("-" * 20)
    print(msg)

def load_env(env_file):
    if not os.path.exists(env_file):
        say("%s 不存在！" % (env_file))
        return False
    with open(env_file) as f:
        for line in f.readlines():
            if line[0] == '#':
                continue
            if line.find('=') < 0:
                continue
            env_str = line.split('=', 1)
            os.environ[env_str[0].strip()] = env_str[1].strip()

# 生成compose配置
def copy_compose(source_file, target_file):
    tf = open(target_file, 'w+')
    with open(source_file) as f:
        modulename = ''
        servicename = ''
        line_num = 0
        for l in f.readlines():
            if line_num == 0:
                tf.write(l)
                line_num += 1
                continue
            if l[0] == '#' or not l.strip():
                continue
            if l.count(' ') == 0:
                modulename = l.strip().strip(':')

            if modulename == 'services':
                if l.count(' ') == 4:
                    servicename = l.strip().strip(':')
            else:
                if l.count(' ') == 2:
                    servicename = l.strip().strip(':')
            if modulename == 'services':
                if not servicename:
                    tf.write(l)
                if servicename in SERVICE_NAME:
                    tf.write(l)
            else:
                if modulename in MODULE_NAME:
                    tf.write(l)
    tf.close()

# 初始化 Laradock 项目
def init_project():
    print("当前项目【%s】,使用的PHP版本【%s】" % (COMPOSE_PROJECT_NAME, PHP_VERSION))
    say("Step1: 正在下载 Laradock 项目")
    os.system("git clone https://github.com/laradock/laradock.git %s" % (LARADOCK_DIR))

    say("Step2: 初始化 Laradock 项目")
    # 生成 .env文件 && 更新一些下载源
    os.system('''
        cd %s && \
        cp env-example .env && \
        echo "COMPOSE_PROJECT_NAME=%s" >> .env && \
        sed -i 's/CHANGE_SOURCE=false/CHANGE_SOURCE=true/g' .env && \
        sed -i 's/composer global install/composer global install \&\& composer config -g repo.packagist composer https:\/\/packagist.phpcomposer.com/g' workspace/Dockerfile-%s
    ''' % (LARADOCK_DIR, COMPOSE_PROJECT_NAME, PHP_VERSION))
    say("Success: 构建完成! Enjoy it!")

def ps_project():
    os.system(r'''
        cd %s && \
        docker-compose ps
    ''' % (LARADOCK_DIR))

def start_project():
    os.system(r'''
        cd %s && \
        docker-compose up -d nginx redis
    ''' % (LARADOCK_DIR))

def stop_project():
    os.system(r'''
        cd %s && \
        docker-compose stop %s
    ''' % (LARADOCK_DIR, " ".join(SERVICE_NAME)))

def rm_project():
    os.system(r'''
        cd %s && \
        docker-compose stop; docker-compose rm
    ''' % (LARADOCK_DIR))

def rebuild_project():
    os.system(r'''
        cd %s && \
        docker-compose stop; docker-compose rm && \
        docker-compose build %s && \
        docker-compose up -d nginx redis
    ''' % (LARADOCK_DIR, " ".join(SERVICE_NAME)))

# 打包 Laradock 项目镜像
def packup_project():

    # 读取生产环境配置文件
    load_env("./%s/.env" % (LARADOCK_DIR))
    env_name = 'pro'
    load_env("./compose/%s.env" % (env_name))
    COMPOSE_PROJECT_NAME = os.getenv('COMPOSE_PROJECT_NAME')

    say('Step1: 创建 %s 的镜像配置' % (COMPOSE_PROJECT_NAME))

    # 拷贝php-fpm配置到compose/tmp目录下
    os.system('''
        cp -r %s/php-fpm ./compose/tmp/ && \
        sed -i '/ADD .\/xlaravel.pool.conf/a\ADD ./php%s.ini \/usr\/local\/etc\/php\/php.ini' ./compose/tmp/php-fpm/Dockerfile-%s
    ''' % (LARADOCK_DIR, PHP_VERSION, PHP_VERSION))

    # 生成 docker-compose.yml
    copy_compose('%s/docker-compose.yml' % (LARADOCK_DIR), DOCER_COMPOSE)

    # 修改 applications 的 build 路径
    os.system(r'''
        sed -i 's/image\: tianon\/true/build\:\n        context\: \. \n        dockerfile: compose\/applications\/Dockerfile/' %s
    ''' % (DOCER_COMPOSE))

    # 修改 workspace 的 build 路径
    os.system(r'''
        sed -i 's/context: \.\/workspace/context: \.\/%s\/workspace/' %s
    ''' % (LARADOCK_DIR, DOCER_COMPOSE))

    # 修改 php-fpm 的 build 路径
    os.system(r'''
        sed -i 's/context: \.\/php-fpm/context: \.\/compose\/tmp\/php-fpm/' %s
    ''' % (DOCER_COMPOSE))

    # 修改 nginx 的 build 路径
    os.system(r'''
        sed -i 's/context: \.\/nginx/context: \.\/%s\/nginx/' %s
    ''' % (LARADOCK_DIR, DOCER_COMPOSE))

    # 修改 redis 的 build 路径
    os.system(r'''
        sed -i 's/build: \.\/redis/build:\n        context: \.\/%s\/redis/' %s
    ''' % (LARADOCK_DIR, DOCER_COMPOSE))

    # 构建镜像
    say('Step2: 正在构建 %s 镜像' % (COMPOSE_PROJECT_NAME))
    os.system(r'''
        docker-compose build %s
    ''' % (" ".join(SERVICE_NAME)))

    say('Step3: 镜像构建完成！你可以上传到Rancher上部署了！')

# 打印系统变量
def showvar_project():
    load_env("./%s/.env" % (LARADOCK_DIR))
    load_env("./compose/%s.env" % (env_name))
    os.system('printenv')

if __name__ == '__main__':
    try:
        env_name = sys.argv[2]
    except:
        env_name = 'local'
    try:
        load_env("./compose/%s.env" % (env_name))
        COMPOSE_PROJECT_NAME = os.getenv('COMPOSE_PROJECT_NAME')
        PHP_VERSION = os.getenv('PHP_VERSION')
        action = sys.argv[1]
        exec(action+'_project()')
    except:
        print("python initcompose {init|ps|start|stop|rm|rebuild|packup|showvar}")

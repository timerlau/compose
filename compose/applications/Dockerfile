FROM alpine
MAINTAINER songmw songmingwei@100tal.com

COPY . /var/www/app
COPY ./compose/nginx/ /etc/nginx/sites-available/

RUN chmod 777 -R /var/www/app/storage && \
rm -rf /var/www/app/laradock

# 设置需要共享的目录
VOLUME /var/www/app
VOLUME /etc/nginx/sites-available
VOLUME /var/log/nginx
VOLUME /data

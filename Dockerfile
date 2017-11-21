# A basic apache server. To use either add or bind mount content under /var/www
FROM esolomo/betterdevops_targetweb:1.0

MAINTAINER Emmanuel Solomo version: 1.0


WORKDIR /apps/targetweb_ftpmgr

EXPOSE 443

CMD ["python2.7","webfutur.py"]
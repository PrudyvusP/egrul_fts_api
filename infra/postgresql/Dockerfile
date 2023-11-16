FROM postgres:13.0-alpine
COPY ./init.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/init.sh
ENTRYPOINT ["init.sh"]
CMD ["docker-entrypoint.sh", "postgres"]

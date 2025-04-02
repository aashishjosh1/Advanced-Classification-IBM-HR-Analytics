FROM continuumio/anaconda3:2021.05
EXPOSE 7000
RUN apt-get update && \
    apt-get install -y apache2 \
    apache2-dev \
    vim \
 && apt-get clean \
 && apt-get autoremove \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /var/www/predicting_employee_attrition/
COPY ./ /var/www/predicting_employee_attrition/
RUN pip install -r requirements.txt
RUN /opt/conda/bin/mod_wsgi-express install-module
RUN mod_wsgi-express setup-server "/var/www/predicting_employee_attrition/source_code/predicting_employee_attrition.wsgi" --port=7000 \
    --user www-data --group www-data \
    --server-root=/etc/mod_wsgi-express-80
CMD ["/etc/mod_wsgi-express-80/apachectl", "start", "-D", "FOREGROUND"]
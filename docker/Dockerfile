FROM node:9.11 as static
RUN mkdir -p /opt/static
WORKDIR /opt/static
COPY logan/static /opt/static
RUN yarn

FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/djangoapp/src

COPY Pipfile Pipfile.lock /opt/services/djangoapp/src/
WORKDIR /opt/services/djangoapp/src
RUN pip install -U pip && pip install pipenv && pipenv install --system

COPY logan /opt/services/djangoapp/src/logan

COPY --from=static /opt/static/node_modules /opt/services/djangoapp/src/logan/static/node_modules
RUN cd logan && python manage.py collectstatic --no-input --clear

# Could be optimized for production: only need gunicorn conf file (locales should be bind-mounted)
COPY . /opt/services/djangoapp/src

# For Continuous Integration only
ARG ci
ENV CI=${ci:-false}
RUN if [ "${CI}" = "true" ]; then \
        apt-get update ; \
        apt-get install -y make libenchant-dev; \
        apt-get clean; \
    fi
RUN if [ "${CI}" = "true" ]; then pipenv install --dev --system; fi

EXPOSE 8000
CMD ["gunicorn", "-c", "docker/services/gunicorn/conf.py", "--bind", ":8000", "--chdir", "logan", "logan.wsgi:application"]

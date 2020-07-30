FROM klotio/python:0.1

RUN apk add --no-cache --virtual .pip-deps  \
        gcc \
        libc-dev \
        make \
    && pip install --no-cache-dir \
		flask==1.1.2 \
		flask_restful==0.3.8 \
    && apk del --no-network .pip-deps \
	&& find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' +

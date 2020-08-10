FROM klotio/python:0.2

COPY requirements.txt .
COPY setup.py .
COPY lib lib

RUN apk add --no-cache --virtual .pip-deps  \
        gcc \
        libc-dev \
        make \
		git \
    && pip install --no-cache-dir -r requirements.txt \
	&& python setup.py install \
    && apk del --no-network .pip-deps \
	&& find /usr/local -depth \
		\( \
			\( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
			-o \
			\( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
		\) -exec rm -rf '{}' + \
	&& rm requirements.txt \
	&& rm setup.py \
	&& rm -rf build \
	&& rm -rf dist \
	&& rm -rf lib/klotio_python.egg-info \
	&& rm -rf lib/klotio

CMD "/opt/service/bin/api.py"

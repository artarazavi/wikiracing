FROM python:3.7

ENV HOST 0.0.0.0
ENV PORT 5001
ENV DEBUG true

COPY . /src/app/api
WORKDIR /src/app/api

RUN python -m pip install --upgrade pip

# install requirements
RUN pip install -r requirements.txt

# expose the app port
EXPOSE 5001

# run the app server
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5001"]
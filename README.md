wikiracing
docker-compose build
docker-compose up

to test 
cd tests
py.test [name of test or no name for all]

check whats going on on redis
localhost:8081

spin up task with flower to check celery
docker-compose restart [task name or task names] flower
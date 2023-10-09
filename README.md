# housing_api
This is an `api` giving you all the required housing data for different postcodes across the UK.  

In order to be able to run it locally, you will need `Docker` installed on your system.

Also, this `backend` api should be used accordingly with the `Frontend` app in https://github.com/soroushkhosravi/my-react-app.

# Starting the project

1. First, you should run the following command to have database migrations in place.
```
docker-compose run alembic alembic upgrade heads
```

2. You then, run the following command to spin up the required `docker containers`.

```
docker-compose up
```


# Running the tests

In order to run the tests, run the following command in the root of the repository:

```
docker-compose run web pytest
```
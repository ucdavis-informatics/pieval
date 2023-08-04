# Mongo Container docs

[Official Mongo Container page](https://hub.docker.com/_/mongo)


```sh
# pull an image
docker pull amd64/mongo:6
```


```sh
# start  FOR THE FIRST TIME the container such that it can be reached on the host
docker run --name pv_mongo -p 27017:27017 mongo:6
```

```sh
# RE-starting the pv mongo container
docker start pv_mongo
```
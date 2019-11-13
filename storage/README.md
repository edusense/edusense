EduSense Storage
================

This is a repository for storage backend component of EduSense.
Storage server can be compiled manually natively using Go compiler or
automatically using Dockerfile.

## Getting Started

### Custom build

#### Build storage
```
go build go.edusense.io/storage/apiserver
```

#### Run storage
```
export SSL_CERT=<contents of SSL cert>
export SSL_CERT_PRIVATE_KEY=<contents of SSL private key>
export APP_USERNAME=<username_for_authentication>
export APP_PASSWORD=<password_for_authentication>
./apiserver \
  --port <port for REST API (default 3000)> \
  --dbhost <db_host: host for MongoDB (default localhost)>:<db_port: port for MongoDB (default 27017)> \
  --db <db_name: db name (default edusense)>
```

### Docker build

#### Bulid image
```
docker build .
```

You may also want to name the image like below:
```
docker build . -t <tag_name>
```


#### Run image
To run, you can give the same parameters with LOCAL_USER_ID environment
variable.
```
export LOCAL_USER_ID=$(id -u)
docker run <image_name> <arguments>
```

## License

The source code in this directory and its subdirectories are all governed
by [BSD 3-Clause License](/LICENSE). By compiling this source code, you should
comply with the terms for "derivation" or "derived work" noted by each of the
software libraries this code depends on. The following is the list of direct
dependencies of storage server implementation:

- [globalsign/mgo](https://github.com/globalsign/mgo): [license](https://github.com/globalsign/mgo/tree/master/LICENSE)
- [gorilla/mux](https://github.com/gorilla/mux): [license](https://github.com/gorilla/mux/tree/master/LICENSE)
- [graph-gophers/graphql-go](https://github.com/graph-gophers/graphql-go): [license](https://github.com/graph-gophers/graphql-go/tree/master/LICENSE)

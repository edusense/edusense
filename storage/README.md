EduSense Storage
================

This is a repository for storage backend component of EduSense.
Storage server can be compiled manually natively using Go compiler or
automatically using Dockerfile.

## Getting Started

This instruction is for manually setting up storage servers. For those
who are new to EduSense, we recommend to take a look at automated
multi-container setup provided [here](/compose/README.md). The setup code
will provide a good reference to figure out how each EduSense component
should be connected to each other.

In the following sectinos, we provide two different instructions: deploying without
Docker and with Docker.

### Building/Deploying without Docker

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

### Building/Deploying with Docker

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
docker --net="host" run <image_name> <arguments>
```

### Command Line Arguments & Environment Variables

Storage server takes the following command line arguements:

* **-port**: port number (integer) users wants to put the API end point
* **-dbhost**: hostport for mongodb backend.
* **-db**: database name inside mongoDB.

Also, the storage server takes the following environment variables:

* **SSL_CERT**: SSL certificate for HTTPS connection
* **SSL_CERT_PRIVATE_KEY**: private key used to create the SSL certificate above
* **APP_USERNAME**: root user name to authorize API access
* **APP_PASSWORD**: root user password to authorize API access

## Developer Guide

Welcome to storage server code base! For developers who are new to storage server,
they can start looking at [apiserver/app.go](apiserver/app.go).

### Directory Structure

* **[apiserver/](apiserver)**: Frontend API server. Implements endpoints, authentication and other utilities.
  * **[app.go](apiserver/app.go)**: Implements RESTful endpoints.
  * **[auth.go](apiserver/auth.go)**: Implements authentication.
  * **[manage.go](apiserver/manage.go)**: Implements camera connectivity monitoring utilities.
  * **[proto.go](apiserver/proto.go)**: Defines request/response protocol for the endpoints.
* **[dbhandler/](dbhandler)**: DB connectors. Transforms data operations into DB commands.
  * **[interface.go](dbhandler/interface.go)**: Defines abstractions for DB operations.
  * **[mongo/](dbhandler/mongo)**: Implements DB operations for MongoDB binding.
* **[models/](models)**: DB-independent data model definitions.
  * **[audioframe.go](models/audioframe.go)**: Defines processed audio frame structs.
  * **[frame.go](models/frame.go)**: Defines frame filter structs.
  * **[session.go](models/session.go)**: Defines class session structs.
  * **[videoframe.go](models/videoframe.go)**: Defines processed video frame structs.
* **[query/](query)**: Query logic. Implement GraphQL functionalities.
  * **[schema.go](query/schema.go)**: Defines GraphQL schema.
  * **[resolver/](query/resolver)**: Implements GraphQL query resolving.

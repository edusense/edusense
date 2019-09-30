EduSense Storage
================

This is a repository for storage backend component of EduSense.
Core functionalities are implemented with Go language (golang.org).

## Get Started

### Build storage
```
go build go.edusense.io/storage/apiserver
```

### Run storage
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

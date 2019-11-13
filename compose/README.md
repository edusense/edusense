Running EduSense on Docker
==========================

# Continuous Integration

## Storage (MongoDB + Storage Web Server)

### YAML setup

Before getting started, you need to configure SSL & app username / password.
If you want to use without SSL or use default credentials, put path to an empty
file. For example, `touch username` and put the created file path(`username`).

### Use Docker-compose for single node setup
```
docker-compose -f ./docker-compose-storage.yml up
docker-compose -f ./docker-compose-storage.yml down
```
# Deploying EduSense without Compilation for Production

Dockerfiles in this directory are mainly for automated builds in certain
environments where we need to download the code from publicly available
repositories (i.e. Docker Hub) and deploy EduSense without need for
compiling/developing/integrating the applications from source code.

## License

The source code in this directory and its subdirectories are all governed
by [BSD 3-Clause License](/LICENSE). By compiling this source code using the
Dockerfiles or docker-compose files, you should comply with the terms for
"derivation" or "derived work" noted by each of the software libraries each
EduSense container depends on.

Developer Guide
===============

This is a documentation for EduSense client developers. EduSense clients should
fetch data from [storage servers](/storage). Our frontend services operate on top
of these APIs.

## Core Concepts

## Storage API

External APIs for storage servers are based on RESTful HTTP APIs. Currently, storage server
uses native JSON-encoded string to post data to the backend server (mutation) while
it uses [GraphQL](https://graphql.org/) inside JSON-encoded data structure for query.
*Note: We plan to apply GraphQL to mutations also, but it is not implemented in our
code base yet.*

### Authentication

To access data in storage servers, users should provide correct credentials. We use
basic HTTP authentication method. For details on HTTP Basic authentication: please refer to
[HTTP Basic Auth](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#Basic_authentication_scheme).

### API Specifications

#### Insert Session

#### Insert Frame

* **POST** `/sessions/{session_id}/{type}/frames/{schema}/{channel}/`
* URL arguments
  * `session_id`: session identifier string
  * `type`: type of the frame (`video` or `audio`)
  * `schema`: schema string
  * `channel`: channel string (`instructor` or `student`)

#### Query

* **POST** `/query`

### Code Examples

A simple python code that accesses frame data from storage server:
```
import requests
from requests.auth import HTTPBasicAuth
import json
import time

APP_USERNAME = # app username
APP_PASSWORD = # app password

start_time = time.time()
r = requests.post('https://<storage_server_hostname>:<storage_server_port>/query',
                  json={'query': '{sessions(sessionId: \"<session_id>\") { id keyword schemas videoFrames(schema: \"<schema_name>\", channel: <channel: student or instructor>, frameNumber: {filters: [{op: gte number: 1000}, {op: lte number: 1500}]}) { people { openposeId inference { trackingId face { orientation }} } }}}'},
    auth=HTTPBasicAuth(APP_USERNAME, APP_PASSWORD))

print json.dumps(json.loads(r.json()["response"]), indent=2)
```

Developer Guide
===============

This is a documentation for EduSense client developers. EduSense clients should
fetch data from [storage servers](/storage). Our storage server operates on top
of these APIs.

## Core Concepts

Taking into account that there will be a huge diversity in how users organize
classroom data, EduSense storage backend is designed to provide high flexibility
by holding a minimal set of contextual data inside storage backend. EduSense
encourages users to build a separate application with deployment-specific contextual
information. To support these use cases, we provide the following minimal HTTP RESTful
APIs. EduSense developers should be conservative about adding new APIs as it may tamper
usability.

For simplicity, session and frame management in EduSense storage follows the following
few rules.

### Session Management

1. Class session means the single, continuous time period when a class takes place. In
   general university settings, these class sessions repeat on a weekly basis. For example,
   a semester-long course is composed of multiple class sessions repeated over the
   semester.
1. Each class session has a custom `keyword` and a unique machine-generated session identifier (`session_id`).
1. A custom `keyword` is a way for users to search for specific class sessions they want. For example,
   in CMU, we use some keyword structure like:
   `cmu_0000A_weh_7111_201911251753` noting that the corresponding session has `0000A` as
   class code and took place in `weh_7111` at `201911251753`. Our default search algorithm
   for session keywords is *prefix-match*; we encourage developers to implement prefix-coded
   hierarchy for keyword schema.
1. A machine-generated(readable) `session_id` serves as a unique identifier for each session.
   After looking up session identifiers by a keyword, you can post/get frames and session metadata
   using this session id.

### Frame Management

1. Each session can have multiple ways to represent data (e.g., different data format). Different
   data representation formats can be distinguished from each other by string `schema` field. Users can
   effectively *version* their data schema using this field for compatibility.
1. Processed frames for each class session are indexed by `timestamp` and `frame_number`. All frames
   should have these fields.
1. To distinguish instructor frames (back camera) from student frames (front camera), we use a separate
   field `channel` which can be either `instructor` or `student`.
1. Since GraphQL requires frames to be formatted in a unified schema, we have a separate field
   `type`. If a user posts a frame with `type` being `video`, users can query the frame by GraphQL's video
   frame schema. If a user posts a frame with `type` being `audio`, users can query the frame by GraphQL's
   audio frame schema. If `type` is either `video` or `audio`, if the posted frame does not follow the
   certain schema, it will return error in response. Otherwise--if `type` is neither `video` nor `audio`--
   the frame will be regarded as free-form, returning errors when user tries to query the frame using
   GraphQL.

## Storage API

External APIs for storage servers are based on RESTful HTTP APIs. Currently, storage server
uses native JSON-encoded string to post data to the backend server (mutation) while
it uses [GraphQL](https://graphql.org/) inside JSON-encoded data structure for query.
*Note: We plan to apply GraphQL to mutations also, but it is not implemented in our
code base yet.*

### Authentication

To access data in storage servers, users should provide correct credentials (APP_USERNAME, APP_PASSWORD).
We use basic HTTP authentication method. For details on HTTP Basic authentication: please refer to
[HTTP Basic Auth](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#Basic_authentication_scheme).

### API Specifications

#### Insert Session

If a user want to add a new session to the database table, they should first create a
session with fresh session ID.

* **POST** `/sessions`
* URL arguments: N/A
* Request Body
  * `keyword`: an auxiliary keyword this session is mapped to. Keywords and sessions have
    one-to-many relations.
  * `metadata`: a free-form JSON object that serves as metadata for the session.
* Reply Body
  * `success`: boolean for success/failure
  * `session_id`: new session id string
  * `error`: string error message
  * `error_code`: integer error code
* Code Example

  ```
  import requests
  from requests.auth import HTTPBasicAuth
  import json
  import time

  APP_USERNAME = # app username
  APP_PASSWORD = # app password

  start_time = time.time()
  r = requests.post('https://<storage_server_hostname>:<storage_server_port>/sessions',
                    json={'metadata': {'free': 'form'}, 'keyword': 'this_is_keyword'},
      auth=HTTPBasicAuth(APP_USERNAME, APP_PASSWORD))

  print json.dumps(json.loads(r.json()["response"]), indent=2)
  ```

#### Insert Frame

Once a session is ready, a user can start adding new frames to the session.

* **POST** `/sessions/{session_id}/{type}/frames/{schema}/{channel}/`
* URL arguments
  * `session_id`: session identifier string
  * `type`: type of the frame (`video` or `audio` for known video/audio format, otherwise free-form)
  * `schema`: schema string
  * `channel`: channel string (`instructor` or `student`)
* Request Body
  * `frames`: a list of free, known videoframe or known audioframes.
* Reply Body
  * `success`: boolean for success/failure
  * `error`: string error message
  * `error_code`: integer error code
* Code Example

  ```
  import requests
  from requests.auth import HTTPBasicAuth
  import json
  import time

  APP_USERNAME = # app username
  APP_PASSWORD = # app password

  start_time = time.time()
  r = requests.post('https://<storage_server_hostname>:<storage_server_port>/sessions/<session_id>/<type>/frames/<schema>/<instructor>',
                    json={'frames': [<frame>, <frame>, ...]},
      auth=HTTPBasicAuth(APP_USERNAME, APP_PASSWORD))

  print json.dumps(json.loads(r.json()["response"]), indent=2)
  ```

#### Query

* **POST** `/query`
* URL arguments: N/A
* Request Body
  * `query`: query string for GraphQL
  * `operationName`: operation name string for GraphQL
  * `variables`: JSON-encoded dictionary of variables
* Reply Body
  * `success`: boolean for success/failure
  * `error`: string error message
  * `error_code`: integer error code
  * `response`: string response for GraphQL
* Code Example

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

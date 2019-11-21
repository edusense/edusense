Developer Guide
===============

This is a documentation for EduSense client developers. EduSense clients should
fetch data from [storage servers](/storage). Our frontend services operate on top
of these APIs.

### APIs

External interfaces heavily depend on RESTful HTTP APIs. Currently, storage server
uses native JSON-encoded string to post data to the backend server (mutation) while
it uses [GraphQL](https://graphql.org/) inside JSON-encoded data structure for query.
*Note: We plan to apply GraphQL to mutations also, but it is not implemented in our
code base yet.*

GraphQL allows us to only send and receive fields requested, otherwise we need to
exchange a full data structure between servers and clients. GraphQL requires clients
to query data following certain schema. The schema for edusense is noted
[here](/storage/query/schema.go).

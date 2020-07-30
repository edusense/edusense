// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package query

import (
	graphql "github.com/graph-gophers/graphql-go"
	dbhandler "go.edusense.io/storage/dbhandler"
	resolver "go.edusense.io/storage/query/resolver"
)

// QuerySchema defines GraphQL schema for session/frame queries.
// TODO(DohyunKimOfficial): We only support query with GraphQL. We need to
// properly implement Mutations via GraphQL.
const QuerySchema = `
    schema {
      query: Query
    }

    type Time {
      RFC3339: String!
      unixSeconds: Int!
      unixNanoseconds: Int!
    }

    enum Channel {
      instructor
      student
    }

    type Query {
      sessions (sessionId: ID, keyword: String): [Session!]!
      classrooms : [Classroom!]!
    }

    type Classroom {
      building: String!
      room: String!
      floor: String!
      dimensions: [Float!]!
      dimensionsScale: String!
      numberOfSeats: Int!
      numberOfWindows: Int!

      frontCameraModel: String!
      rearCameraModel: String!
      frontCameraIP: String!
      rearCameraIP: String!

      blackboardBoundary: [[Float!]!]!
      podiumBoundary: [[Float!]!]!
      projectorBoundary: [[Float!]!]!

      courses: [[String!]!]!
    }

    enum RangeQueryOperator {
      gte
      gt
      eq
      lt
      lte
    }

    input FrameNumberQuery {
      filters: [FrameNumberQueryFilter!]
    }

    input FrameNumberQueryFilter {
      op: RangeQueryOperator!
      number: Int!
    }

    input TimestampQuery {
      filters: [TimestampQueryFilter!]
    }

    enum TimeFormat {
      RFC3339
      unixTimestamp
    }

    input TimestampQueryFilter {
      op: RangeQueryOperator!
      format: TimeFormat!
      timestamp: TimestampInput!
    }

    input TimestampInput {
      RFC3339: String
      unixSeconds: Int
      unixNanoseconds: Int
    }

    type Session {
      id: ID!
      keyword: String!
      version: String!
      schemas: [String!]!
      createdAt: Time!
      videoFrames(schema: String!, channel: Channel!, frameNumber: FrameNumberQuery, timestamp: TimestampQuery): [VideoFrame!]!
      audioFrames(schema: String!, channel: Channel!, frameNumber: FrameNumberQuery, timestamp: TimestampQuery): [AudioFrame!]!
    }

    type VideoFrame {
      frameNumber: Int!
      timestamp: Time!
      thumbnail: Thumbnail
      people: [Person]
    }

    type Thumbnail {
      originalCols: Int!
      originalRows: Int!
      binary: String!
    }

    type Person {
      body: [Int!]
      face: [Int!]
      hand: [Int!]
      openposeId: Int
      inference: VideoInference
    }

    enum ArmPose {
      handsRaised
      armsCrossed
      handsOnFace
      other
      error
    }

    enum SitStand {
      sit
      stand
      error
    }

    enum MouthOpen {
      open
      closed
      error
    }

    enum MouthSmile {
      smile
      noSmile
      error
    }

    enum FaceOrientation {
      front
      back
      error
    }

    type VideoInference {
      posture: Posture
      face: Face
      head: Head
      trackingId: Int
    }

    type Posture {
      armPose: ArmPose
      sitStand: SitStand
      centroidDelta: [Int!]
      armDelta: [[Int!]!]
    }

    type Face {
      boundingBox: [[Int!]!]
      mouthOpen: MouthOpen
      mouthSmile: MouthSmile
      orientation: FaceOrientation
    }

    type Head {
      roll: Float!
      pitch: Float!
      yaw: Float!
      translationVector: [Float!]
      gazeVector: [[Int!]!]
    }

    type AudioFrame {
      frameNumber: Int!
      timestamp: Time!
      channel: Channel!
      audio: Audio!
    }

    type Audio {
      amplitude: Float!,
      melFrequency: [[Float!]!]!
      inference: AudioInference!
    }

    enum Speaker {
      ambient
      student
      instructor
    }

    type AudioInference {
      speech: Speech!
    }

    type Speech {
      confidence: Float!
      speaker: Speaker!
    }
  `

// MustParseSchema parses the GraphQL schema. If parse fails, it will crash
// the application.
func MustParseSchema(driver dbhandler.DatabaseDriver) *graphql.Schema {
	schema := graphql.MustParseSchema(QuerySchema, &resolver.QueryResolver{Driver: driver})
	return schema
}

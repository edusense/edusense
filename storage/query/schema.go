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
      classrooms: [Classroom!]!
      courses: [Course!]!  
      analytics (sessionId: ID, keyword: String): [Analytics!]!
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

      courseList: [[String!]!]!
    }

    type Course {
      classID: String!
      section: String!
      semester: String!
      year: Int!
      lectureType: String!

      instructors: [[String!]!]!
      teachingAssistants: [[String!]!]!
      initialEnrollment: Int!
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
      mfccFeatures: [[Float!]!]!
      polyFeatures: [[Float!]!]!
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

    type Analytics {
      id: String!
      keyword: String!
      metaInfo: MetaInfo!
      debugInfo: String!
      secondLevel: [SecondLevel]!
      blockLevel: [BlockLevel]!
      sessionLevel: SessionLevel
    }

    type MetaInfo {
      pipelineVersion: String!
      analysisStartTime: Int!
      totalRuntime: Float!
      runModules: [String!]!
      ModuleRuntime: [Float!]!
      SuccessModules: [String!]!
      FailureModules: [String!]!
    }

    type SecondLevel {
      secondInfo: SecondInfo!
      audio: SecondAudioAnalysis
      gaze: SecondGazeAnalysis
      location: SecondLocationAnalysis
      posture: SecondPostureAnalysis
      crossModal: String
    }

    type BlockLevel {
      blockInfo: BlockInfo!
      audio: BlockAudioAnalysis
      gaze: BlockGazeAnalysis
      location: BlockLocationAnalysis
      posture: BlockPostureAnalysis
      crossModal: String
    }

    type SessionLevel {
      sessionInfo: SessionInfo!
      audio: SessionAudioAnalysis
      gaze: SessionGazeAnalysis
      location: SessionLocationAnalysis
      posture: SessionPostureAnalysis
      crossModal: String
    }

    type SecondInfo {
      unixSeconds: Int
      frameStart: Int
      frameEnd: Int
    }

    type BlockInfo {
      unixStartSeconds: Int!
      blockLength: Int!
      id: Int!
    }

    type SessionInfo {
      unixStartSeconds: Int!
      sessionLength: Int!
    }

    type SecondAudioAnalysis {
      isSilence: Boolean
      isObjectNoise: Boolean
      isTeacherOnly: Boolean
      isSingleSpeaker: Boolean
    }

    type BlockAudioAnalysis {
      silenceFraction: Float
      objectFraction: Float
      teacherOnlyFraction: Float
      singleSpeakerFraction: Float
      teacherActivityType: [String]
      teacherActivityFraction: [Float]
      teacherActivityTimes: [[[Int]!]!]
    }

    type SessionAudioAnalysis {
      audioBasedActivityType: [String]
      audioBasedActivityFraction: [Float]
      audioBasedActivityBlocks: [[[Int]!]!]
    }

    type PrincipalGaze {
      direction: [Float]
      directionVariation: [Float]
      longestStayFraction: [Float]
    }

    type SecondGazeAnalysis {
      instructor: SecondInstructorGaze
      student: SecondStudentGaze
    }

    type SecondInstructorGaze {
      angle: Float
      angleChange: Float
      direction: String
      viewingSectorThreshold: Float
      countStudentsInGaze: Int
      towardsStudents: Boolean
      lookingDown: Boolean
    }

    type SecondStudentGaze {
      id: [Int]
      angle: [Float]
      angleChange: [Float]
      direction: [String]
      towardsInstructor: [Boolean]
      lookingDown: [Boolean]
      lookingFront: [Boolean]
    }


    type BlockGazeAnalysis {
      instructor: BlockInstructorGaze
      student: BlockStudentGaze
    }

    type BlockInstructorGaze {
      gazeCategory: String
      totalCategoryFraction: [Float]
      longestCategoryFraction: [Float]
      principalGaze: PrincipalGaze
      rollMean: Float
      yawMean: Float
      pitchMean: Float
      rollVariance: Float
      yawVariance: Float
      pitchVariance: Float
    }

    type BlockStudentGaze {
      id: [Int]
      numOccurencesInBlock: [Int]
      gazeCategory: [String]
      totalCategoryFraction: [[Float]!]
      longestCategoryFraction: [[Float]!]
      directionMean: [[Float]!]
      directionVariation: [[Float]!]
      towardsInstructorFraction: [Float]
      lookingDownFraction: [Float]
      lookingFrontFraction: [Float]
      rollMean: [Float]
      yawMean: [Float]
      pitchMean: [Float]
      rollVariance: [Float]
      yawVariance: [Float]
      pitchVariance: [Float]
    }


    type SessionGazeAnalysis {
      instructor: SessionInstructorGaze
      student: SessionStudentGaze
    }

    type SessionInstructorGaze {
      gazePreference: String
	    topLocations: [[Float]!]
	    topLocationsGazeLeftFraction: [[Float]!]
	    objectCategory: [String]
	    lookingAtObjectFraction: [Float]
    }

    type SessionStudentGaze {
      id: [Int]
      gazeCategory: [String]
      gazeCategoryFraction: [[Float]!]
    }

    type PrincipalMovement {
      directionMean: [Float]
      directionVariation: [Float]
      directionComps: [Float]
    }

    type SecondLocationAnalysis {
      instructor: SecondInstructorLocation
      student: SecondStudentLocation
    }

    type SecondInstructorLocation{
      atBoard: Boolean
      atPodium: Boolean
      isMoving: Boolean
      locationCoordinates: [Int]
      locationCategory: String
      locationEntropy: Float
      headEntropy: Float
    }

    type SecondStudentLocation {
      id: [Int]
	    trackingIdMap: [[Int]!]
	    isMoving: [Boolean]
	    locationCoordinates: [[Int]!]
	    locationCategory: [String]
	    locationEntropy: [Float]
	    headEntropy: [Float]
    }

    type BlockLocationAnalysis {
      instructor: BlockInstructorLocation
      student: BlockStudentLocation
    }

    type BlockInstructorLocation {
      totalBoardFraction: Float
      longestBoardFraction: Float
      totalPodiumFraction: Float
      longestPodiumFraction: Float
      totalMovingFraction: Float
      longestMovingFraction: Float
      locationCategory: [String]
      categoryFraction: [Float]
      longestCategoryFraction: [Float]
      stayAtLocation: [[Int]!]
      stayAtLocationTimes: [[Float]!]
      longestStayFraction: Float
      principalMovement: PrincipalMovement
    }

    type BlockStudentLocation {
      id: [Int]
      numOccurrencesInBlock: [Int]
      isSettled: [Boolean]
      meanBodyEntropy: [Float]
      maxBodyEntropy: [Float]
      varBodyEntropy: [Float]
      meanHeadEntropy: [Float]
      maxHeadEntropy: [Float]
      varHeadEntropy: [Float]
      stayCoordinates: [[Int]!]
      clusterCount: Int
      clusterCenters: [[Float]!]
      clusterStudentIds: [[Int]!]
      seatingArrangement: String
    }

    type SessionLocationAnalysis {
      instructor: SessionInstructorLocation
      student: SessionStudentLocation
    }

    type SessionInstructorLocation{
      locationBasedActivityType: [String]
      locationBasedActivityFraction: [Float]
      locationBasedActivityBlocks: [[[Int]!]!]                
      locationClusterCount: Int
      locationClusterCenter: [[Float]!]
      locationClusterSize: [Int]
      totalBoardFraction: Float
      longestBoardFraction: Float
      totalPodiumFraction: Float
      longestPodiumFraction: Float
      totalMovingFraction: Float
      longestMovingFraction: Float
      locationCategory: String
      categoryFraction: [Float]
      longestCategoryFraction: [Float]
    }

    type SessionStudentLocation {
      id: [Int]
      settleDownTime: [Float]
      entryTime: [Float]
      entryLocation: [[Float]!]
      exitTime: [Float]
      exitLocation: [[Float]!]
      seatingCategories: [String]
      seatingCategoryBlocks: [[Int]!]
    }

    type SecondPostureAnalysis {
      instructor: SecondInstructorPosture
      student: SecondStudentPosture
    }
    
    type SecondInstructorPosture {
      isStanding: Boolean
      isPointing: Boolean
      pointingDirection: [Float]
      handPosture: String 
      headPosture: String
      centroidFaceDistance: Float
      centroidFaceDistanceAbsolute: Float
    }
    
    type SecondStudentPosture {
      id: [Int]
      isStanding: [Boolean]
      bodyPosture: [String!]
      handPosture: [String!] 
      headPosture: [String!]
    }

    type BlockPostureAnalysis {
      instructor: BlockInstructorPosture
      student: BlockStudentPosture
    }
    
    type BlockInstructorPosture {
      standingFraction: Float
      handPostureCategory: [String]
      handPostureCategoryFraction: [Float]
      headPostureCategory: [String]
      headPostureCategoryFraction: [Float]
      meanCentroidFaceDistance: Float
      varCentroidFaceDistance: Float
    }
    
    type BlockStudentPosture {
      id: [Int]
      numOccurrencesInBlock: [Int]
      isStandingFraction: [Boolean]
      bodyPostureCategory: [String]
      bodyPostureCategoryFraction: [[Float]!]
      headPostureCategory: [String]
      headPostureCategoryFraction: [[Float]!]
      handPostureCategory: [String]
      handPostureCategoryFraction: [[Float]!]
    }

    type SessionPostureAnalysis {
      instructor: SessionInstructorPosture
      student: SessionStudentPosture
    }
    
    type SessionInstructorPosture {
      bodyPosturePreference: String
      pointingClusterCount: Int
      pointingClusterCenter: [[Float]!]
      pointingClusterSize: [Int]
    }
    
    type SessionStudentPosture {
      id: [Int]
	    handPosturePreference: [String]
	    headPosturePreference: [String]
    }

    type BackfillMetaData {
      courseNumber: String!
      sessions: [BackfillSession!]!
    }

    type BackfillSession {
      id: String
      keyword: String
      name: String
      debugInfo: String
      commitId: String
      analyticsCommitId: String
      startTime: Time
      runtime: Float
      status: String
      pipelineVersion: String
      analysisStartTime: Time
      analysisRuntime: Float
      analysisComplete: Bool
    }

  `

// MustParseSchema parses the GraphQL schema. If parse fails, it will crash
// the application.
func MustParseSchema(driver dbhandler.DatabaseDriver) *graphql.Schema {
	schema := graphql.MustParseSchema(QuerySchema, &resolver.QueryResolver{Driver: driver})
	return schema
}

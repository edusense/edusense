// Copyright (c) 2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

// 
type Analytics struct {
	Id        	 string      `json:"id" bson:"id"`
	Keyword   	 string      `json:"keyword" bson:"keyword"`
	MetaInfo  	 MetaInfo      `json:metaInfo" bson:"metaInfo"`
	DebugInfo 	 string    `json:"debugInfo,omitempty" bson:"debugInfo"`
	SecondLevel  []SecondLevel    `json:"secondLevel,omitempty" bson:"secondLevel"`
	BlockLevel   []BlockLevel    `json:"blockLevel,omitempty" bson:"blockLevel"`
	SessionLevel SessionLevel    `json:"SessionLevel,omitempty" bson:"SessionLevel"`
}

// 
type MetaInfo struct {
	PipelineVersion string `json:"pipelineVersion,omitempty" bson:"pipelineVersion"`
    AnalysisStartTime *int32  `json:"analysisStartTime bson:"analysisStartTime"`
    TotalRuntime *float64 `json:"totalRuntime" bson:"totalRuntime"`
    RunModules []string `json:"runModules" bson:"runModules"`
    ModuleRuntime []*float64 `json:"moduleRuntime" bson:"moduleRuntime"`
    SuccessModules []string `json:"successModules" bson:"successModules"`
    FailureModules []string `json:"failureModules" bson:"failureModules"`
}

type SecondLevel struct {
	SecondInfo SecondInfo `json:"secondInfo" bson:"secondInfo"`
	Audio SecondAudioAnalysis `json:"audio,omitempty" bson:"audio"`
	Gaze SecondGazeAnalysis `json:"gaze,omitempty" bson:"gaze"`
	Location SecondLocationAnalysis `json:"location,omitempty" bson:"location"`
	Posture SecondPostureAnalysis `json:"posture,omitempty" bson:"posture"`
	CrossModal string `json:"crossModal,omitempty" bson:"crossModal"`
}

type BlockLevel struct {
	BlockInfo BlockInfo `json:"blockInfo" bson:"blockInfo"`
	Audio BlockAudioAnalysis `json:"audio,omitempty" bson:"audio"`
	Gaze BlockGazeAnalysis `json:"gaze,omitempty" bson:"gaze"`
	Location BlockLocationAnalysis `json:"location,omitempty" bson:"location"`
	Posture BlockPostureAnalysis `json:"posture,omitempty" bson:"posture"`
	CrossModal string `json:"crossModal,omitempty" bson:"crossModal"`
}

type SessionLevel struct {
	SessionInfo SessionInfo `json:"sessionInfo" bson:"sessionInfo"`
	Audio SessionAudioAnalysis `json:"audio,omitempty" bson:"audio"`
	Gaze SessionGazeAnalysis `json:"gaze,omitempty" bson:"gaze"`
	Location SessionLocationAnalysis `json:"location,omitempty" bson:"location"`
	Posture SessionPostureAnalysis `json:"posture,omitempty" bson:"posture"`
	CrossModal string `json:"crossModal,omitempty" bson:"crossModal"`
}

type SecondInfo struct {
	UnixSeconds *int32 `json:"unixSeconds,omitempty" bson:"unixSeconds"`
	FrameStart *int32  `json:"frameStart,omitempty" bson:"frameStart"`
	FrameEnd *int32  `json:"frameEnd,omitempty" bson:"frameEnd"`
}

type BlockInfo struct {
	UnixStartSeconds *int32 `json:"unixStartSeconds" bson:"unixStartSeconds"`
	BlockLength *int32  `json:"blockLength" bson:"blockLength"`
	Id *int32  `json:"id" bson:"id"`
}

type SessionInfo struct {
	UnixStartSeconds *int32 `json:"unixStartSeconds" bson:"unixStartSeconds"`
	SessionLength *int32  `json:"blockLength" bson:"SessionLength"`
}

type SecondAudioAnalysis struct {
	IsSilence *bool `json:"isSilence,omitempty" bson:"isSilence"`
	IsObjectNoise *bool `json:"isObjectNoise,omitempty" bson:"isObjectNoise"`
	IsTeacherOnly *bool `json:"isTeacherOnly,omitempty" bson:"isTeacherOnly"`
	IsSingleSpeaker *bool `json:"isSingleSpeaker,omitempty" bson:"isSingleSpeaker"`
}

type BlockAudioAnalysis struct {
	SilenceFraction *float64 `json:"silenceFraction,omitempty" bson:"silenceFraction"`
	ObjectFraction *float64 `json:"objectFraction,omitempty" bson:"objectFraction"`
	TeacherOnlyFraction *float64 `json:"teacherOnlyFraction,omitempty" bson:"teacherOnlyFraction"`
	SingleSpeakerFraction *float64 `json:"singleSpeakerFraction,omitempty" bson:"singleSpeakerFraction"`
	TeacherActivityType []string `json:"teacherActivityType,omitempty" bson:"teacherActivityType"`
	TeacherActivityFraction []*float64 `json:"teacherActivityFraction,omitempty" bson:"teacherActivityFraction"`
	TeacherActivityTimes [][][]*int32 `json:"teacherActivityTimes,omitempty" bson:"teacherActivityTimes"`
}

type SessionAudioAnalysis struct {
	AudioBasedActivityType []string `json:"audioBasedActivityType,omitempty" bson:"audioBasedActivityType"`
	AudioBasedActivityFraction []*float64 `json:"audioBasedActivityFraction,omitempty" bson:"audioBasedActivityFraction"`
	AudioBasedActivityBlocks [][][]*int32 `json:"audioBasedActivityBlocks,omitempty" bson:"audioBasedActivityBlocks"`
}

type SecondGazeAnalysis struct {
	Instructor SecondInstructorGaze `json:"instructor,omitempty" bson:"instructor"`
	Student SecondStudentGaze `json:"student,omitempty" bson:"student"`
}

type SecondInstructorGaze struct {
	Angle *float64 `json:"angle,omitempty" bson:"angle"`
	AngleChange *float64 `json:"angleChange,omitempty" bson:"angleChange"`
	Direction *string `json:"direction,omitempty" bson:"direction"`
	ViewingSectorThreshold *float64 `json:"viewingSectorThreshold,omitempty" bson:"viewingSectorThreshold"`
	CountStudentsInGaze *int32 `json:"countStudentsInGaze,omitempty" bson:"countStudentsInGaze"`
	TowardsStudents *bool `json:"towardsStudents,omitempty" bson:"towardsStudents"`
	LookingDown *bool `json:"lookingDown,omitempty" bson:"lookingDown"`
}

type PrincipalGaze struct {
	Direction []*float64 `json:"direction,omitempty" bson:"direction"`
	DirectionVariation []*float64 `json:"directionVariation,omitempty" bson:"directionVariation"`
	LongestStayFraction []*float64 `json:"longestStayFraction,omitempty" bson:"longestStayFraction"`
}

type SecondStudentGaze struct {
	Id []*int32 `json:"id,omitempty" bson:"id"`
	Angle []*float64 `json:"angle,omitempty" bson:"angle"`
	AngleChange []*float64 `json:"angleChange,omitempty" bson:"angleChange"`
	Direction []*string `json:"direction,omitempty" bson:"direction"`
	TowardsInstructor []*bool `json:"towardsInstructor,omitempty" bson:"towardsInstructor"`
	LookingDown []*bool `json:"lookingDown,omitempty" bson:"lookingDown"`
	LookingFront []*bool `json:"lookingFront,omitempty" bson:"lookingFront"`
}

type BlockGazeAnalysis struct {
	Instructor BlockInstructorGaze `json:"instructor,omitempty" bson:"instructor"`
	Student BlockStudentGaze `json:"student,omitempty" bson:"student"`
}

type BlockInstructorGaze struct {
	GazeCategory string `json:"gazeCategory,omitempty" bson:"gazeCategory"`
	TotalCategoryFraction []*float64 `json:"totalCategoryFraction,omitempty" bson:"totalCategoryFraction"`
	LongestCategoryFraction []*float64 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	PrincipalGaze PrincipalGaze `json:"principalGaze,omitempty" bson:"principalGaze"`
	RollMean *float64 `json:"rollMean,omitempty" bson:"rollMean"`
	YawMean *float64 `json:"yawMean,omitempty" bson:"yawMean"`
	PitchMean *float64 `json:"pitchMean,omitempty" bson:"pitchMean"`
	RollVariance *float64 `json:"rollVariance,omitempty" bson:"rollVariance"`
	YawVariance *float64 `json:"yawVariance,omitempty" bson:"yawVariance"`
	PitchVariance *float64 `json:"pitchVariance,omitempty" bson:"pitchVariance"`
}

type BlockStudentGaze struct {
	Id []*int32 `json:"id,omitempty" bson:"id"`
	NumOccurencesInBlock []*int32 `json:"numOccurencesInBlock,omitempty" bson:"numOccurencesInBlock"`
	GazeCategory []string `json:"gazeCategory,omitempty" bson:"gazeCategory"`
	TotalCategoryFraction [][]*float64 `json:"totalCategoryFraction,omitempty" bson:"totalCategoryFraction"`
	LongestCategoryFraction [][]*float64 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	DirectionMean [][]*float64 `json:"directionMean,omitempty" bson:"directionMean"`
	DirectionVariation [][]*float64 `json:"directionVariation,omitempty" bson:"directionVariation"`
	TowardsInstructorFraction []*float64 `json:"towardsInstructorFraction,omitempty" bson:"towardsInstructorFraction"`
	LookingDownFraction []*float64 `json:"lookingDownFraction,omitempty" bson:"lookingDownFraction"`
	LookingFrontFraction []*float64 `json:"lookingFrontFraction,omitempty" bson:"lookingFrontFraction"`
	RollMean []*float64 `json:"rollMean,omitempty" bson:"rollMean"`
	YawMean []*float64 `json:"yawMean,omitempty" bson:"yawMean"`
	PitchMean []*float64 `json:"pitchMean,omitempty" bson:"pitchMean"`
	RollVariance []*float64 `json:"rollVariance,omitempty" bson:"rollVariance"`
	YawVariance []*float64 `json:"yawVariance,omitempty" bson:"yawVariance"`
	PitchVariance []*float64 `json:"pitchVariance,omitempty" bson:"pitchVariance"`
}

type SessionGazeAnalysis struct {
	Instructor SessionInstructorGaze `json:"instructor,omitempty" bson:"instructor"`
	Student SessionStudentGaze `json:"student,omitempty" bson:"student"`
}

type SessionInstructorGaze struct {
	GazePreference string `json:"gazePreference,omitempty" bson:"gazePreference"`
	TopLocations [][]*float64 `json:"topLocations,omitempty" bson:"topLocations"`
	TopLocationsGazeLeftFraction [][]*float64 `json:"topLocationsGazeLeftFraction,omitempty" bson:"topLocationsGazeLeftFraction"`
	ObjectCategory []string `json:"objectCategory,omitempty" bson:"objectCategory"`
	LookingAtObjectFraction []*float64 `json:"lookingAtObjectFraction,omitempty" bson:"lookingAtObjectFraction"`
}

type SessionStudentGaze struct {
	Id []*int32 `json:"id,omitempty" bson:"id"`
	GazeCategory []string `json:"gazeCategory,omitempty" bson:"gazeCategory"`
	GazeCategoryFraction [][]*float64 `json:"gazeCategoryFraction,omitempty" bson:"gazeCategoryFraction"`
}

type SecondLocationAnalysis struct{
	Instructor SecondInstructorLocation `json:"instructor,omitempty" bson:"instructor"`
	Student SecondStudentLocation `json:"student,omitempty" bson:"student"`
}

type SecondInstructorLocation struct{
	AtBoard *bool `json:"atBoard,omitempty" bson:"atBoard"`
	AtPodium *bool `json:"atPodium,omitempty" bson:"atPodium"`
	IsMoving *bool `json:"isMoving,omitempty" bson:"isMoving"`
	LocationCoordinates []*int32 `json:"locationCoordinates,omitempty" bson:"locationCoordinates"`
	LocationCategory *string `json:"locationCategory,omitempty" bson:"locationCategory"`
	LocationEntropy *float64 `json:"locationEntropy,omitempty" bson:"locationEntropy"`
	HeadEntropy *float64 `json:"headEntropy,omitempty" bson:"headEntropy"`
}

type PrincipalMovement struct{
	DirectionMean []*float64 `json:"directionMean,omitempty" bson:"directionMean"`
	DirectionVariation []*float64 `json:"directionVariation,omitempty" bson:"directionVariation"`
	DirectionComps []*float64 `json:"directionComps,omitempty" bson:"directionComps"`
}

type SecondStudentLocation struct{
	Id []*int32 `json:"id,omitempty" bson:"id"`
	TrackingIdMap [][]*int32 `json:"trackingIdMap,omitempty" bson:"trackingIdMap"`
	IsMoving []*bool `json:"isMoving,omitempty" bson:"isMoving"`
	LocationCoordinates [][]*int32 `json:"locationCoordinates,omitempty" bson:"locationCoordinates"`
	LocationCategory []*string `json:"locationCategory,omitempty" bson:"locationCategory"`
	LocationEntropy []*float64 `json:"locationEntropy,omitempty" bson:"locationEntropy"`
	HeadEntropy []*float64 `json:"headEntropy,omitempty" bson:"headEntropy"`	
}

type BlockLocationAnalysis struct{
	Instructor BlockInstructorLocation `json:"instructor,omitempty" bson:"instructor"`
	Student BlockStudentLocation `json:"student,omitempty" bson:"student"`
}

type BlockInstructorLocation struct{
	TotalBoardFraction *float64 `json:"totalBoardFraction,omitempty" bson:"totalBoardFraction"`
	LongestBoardFraction *float64 `json:"longestBoardFraction,omitempty" bson:"longestBoardFraction"`
	TotalPodiumFraction *float64 `json:"totalPodiumFraction,omitempty" bson:"totalPodiumFraction"`
	LongestPodiumFraction *float64 `json:"longestPodiumFraction,omitempty" bson:"longestPodiumFraction"`
	TotalMovingFraction *float64 `json:"totalMovingFraction,omitempty" bson:"totalMovingFraction"`
	LongestMovingFraction *float64 `json:"longestMovingFraction,omitempty" bson:"longestMovingFraction"`
	// TODO: change back to string
	LocationCategory []*string `json:"locationCategory,omitempty" bson:"locationCategory"`
	CategoryFraction []*float64 `json:"CategoryFraction,omitempty" bson:"CategoryFraction"`
	LongestCategoryFraction []*float64 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	StayAtLocation [][]*int32 `json:"stayAtLocation,omitempty" bson:"stayAtLocation"`
	StayAtLocationTimes [][]*float64 `json:"stayAtLocationTimes,omitempty" bson:"stayAtLocationTimes"`
	LongestStayFraction *float64 `json:"longestStayFraction,omitempty" bson:"longestStayFraction"`
	PrincipalMovement PrincipalMovement `json:"principalMovement,omitempty" bson:"principalMovement"`
}

type BlockStudentLocation struct {
	Id []*int32 `json:"id,omitempty" bson:"id"`
	NumOccurrencesInBlock []*int32 `json:"numOccurrencesInBlock,omitempty" bson:"numOccurrencesInBlock"`
	IsSettled []*bool `json:"isSettled,omitempty" bson:"isSettled"`
	MeanBodyEntropy []*float64 `json:"meanBodyEntropy,omitempty" bson:"meanBodyEntropy"`
	MaxBodyEntropy []*float64 `json:"maxBodyEntropy,omitempty" bson:"maxBodyEntropy"`
	VarBodyEntropy []*float64 `json:"varBodyEntropy,omitempty" bson:"varBodyEntropy"`
	MeanHeadEntropy []*float64 `json:"meanHeadEntropy,omitempty" bson:"meanHeadEntropy"`
	MaxHeadEntropy []*float64 `json:"maxHeadEntropy,omitempty" bson:"maxHeadEntropy"`
	VarHeadEntropy []*float64 `json:"varHeadEntropy,omitempty" bson:"varHeadEntropy"`
	StayCoordinates [][]*int32 `json:"stayCoordinates,omitempty" bson:"stayCoordinates"`
	ClusterCount *int32 `json:"clusterCount,omitempty" bson:"clusterCount"`
	ClusterCenters [][]*float64 `json:"clusterCenters,omitempty" bson:"clusterCenters"`
	ClusterStudentIds [][]*int32 `json:"clusterStudentIds,omitempty" bson:"clusterStudentIds"`
	SeatingArrangement string `json:"seatingArrangement,omitempty" bson:"seatingArrangement"`
}

type SessionLocationAnalysis struct {
	Instructor SessionInstructorLocation `json:"instructor,omitempty" bson:"instructor"`
	Student SessionStudentLocation `json:"student,omitempty" bson:"student"`
}

type SessionInstructorLocation struct {
	LocationBasedActivityType []string `json:"locationBasedActivityType,omitempty" bson:"locationBasedActivityType"`
	LocationBasedActivityFraction []*float64 `json:"locationBasedActivityFraction,omitempty" bson:"locationBasedActivityFraction"`
    LocationBasedActivityBlocks [][][]*int32 `json:"locationBasedActivityBlocks,omitempty" bson:"locationBasedActivityBlocks"`                
	LocationClusterCount *int32 `json:"locationClusterCount,omitempty" bson:"locationClusterCount"`
	LocationClusterCenter [][]*float64 `json:"locationClusterCenter,omitempty" bson:"locationClusterCenter"`
	LocationClusterSize []*int32 `json:"locationClusterSize,omitempty" bson:"locationClusterSize"`
	TotalBoardFraction *float64 `json:"totalBoardFraction,omitempty" bson:"totalBoardFraction"`
	LongestBoardFraction *float64 `json:"longestBoardFraction,omitempty" bson:"longestBoardFraction"`
	TotalPodiumFraction *float64 `json:"totalPodiumFraction,omitempty" bson:"totalPodiumFraction"`
	LongestPodiumFraction *float64 `json:"longestPodiumFraction,omitempty" bson:"longestPodiumFraction"`
	TotalMovingFraction *float64 `json:"totalMovingFraction,omitempty" bson:"totalMovingFraction"`
	LongestMovingFraction *float64 `json:"longestMovingFraction,omitempty" bson:"longestMovingFraction"`
	LocationCategory *string `json:"locationCategory,omitempty" bson:"locationCategory"`
	CategoryFraction []*float64 `json:"CategoryFraction,omitempty" bson:"CategoryFraction"`
	LongestCategoryFraction []*float64 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
}

type SessionStudentLocation struct {
	Id []*int32 `json:"id,omitempty" bson:"id"`
	SettleDownTime []*float64 `json:"settleDownTime,omitempty" bson:"settleDownTime"`
	EntryTime []*float64 `json:"entryTime,omitempty" bson:"entryTime"`
	EntryLocation [][]*float64 `json:"entryLocation,omitempty" bson:"entryLocation"`
	ExitTime []*float64 `json:"exitTime,omitempty" bson:"exitTime"`
	ExitLocation [][]*float64 `json:"exitLocation,omitempty" bson:"exitLocation"`
	SeatingCategories []string `json:"seatingCategories,omitempty" bson:"seatingCategories"`
	SeatingCategoryBlocks [][]*int32 `json:"seatingCategoryBlocks,omitempty" bson:"seatingCategoryBlocks"`
}


type SecondPostureAnalysis struct {
	Instructor SecondInstructorPosture `json:"instructor,omitempty" bson:"instructor"`
	Student SecondStudentPosture `json:"student,omitempty" bson:"student"`
}

type SecondInstructorPosture struct{
	IsStanding *bool `json:"isStanding,omitempty" bson:"isStanding"`
	IsPointing *bool `json:"isPointing,omitempty" bson:"isPointing"`
	PointingDirection []*float64 `json:"pointingDirection,omitempty" bson:"pointingDirection"`
	HandPosture string `json:"handPosture,omitempty" bson:"handPosture"`
	HeadPosture string `json:"headPosture,omitempty" bson:"headPosture"`
	CentroidFaceDistance *float64 `json:"centroidFaceDistance,omitempty" bson:"centroidFaceDistance"`
	CentroidFaceDistanceAbsolute *float64 `json:"centroidFaceDistanceAbsolute,omitempty" bson:"centroidFaceDistanceAbsolute"`
}

type SecondStudentPosture struct{
	Id []*int32 `json:"id,omitempty" bson:"id"`
	IsStanding []*bool `json:"isStanding,omitempty" bson:"isStanding"`
	BodyPosture []string `json:"bodyPosture,omitempty" bson:"bodyPosture"`
	HeadPosture []string `json:"headPosture,omitempty" bson:"headPosture"`
	HandPosture []string `json:"handPosture,omitempty" bson:"handPosture"`
}

type BlockPostureAnalysis struct {
	Instructor BlockInstructorPosture `json:"instructor,omitempty" bson:"instructor"`
	Student BlockStudentPosture `json:"student,omitempty" bson:"student"`
}

type BlockInstructorPosture struct {
	StandingFraction *float64 `json:"standingFraction,omitempty" bson:"standingFraction"`
	HandPostureCategory []string `json:"handPostureCategory,omitempty" bson:"handPostureCategory"`
	HandPostureCategoryFraction []*float64 `json:"handPostureCategoryFraction,omitempty" bson:"handPostureCategoryFraction"`
	HeadPostureCategory []string `json:"headPostureCategory,omitempty" bson:"headPostureCategory"`
	HeadPostureCategoryFraction []*float64 `json:"headPostureCategoryFraction,omitempty" bson:"headPostureCategoryFraction"`
	MeanCentroidFaceDistance *float64 `json:"meanCentroidFaceDistance,omitempty" bson:"meanCentroidFaceDistance"`
	VarCentroidFaceDistance *float64 `json:"varCentroidFaceDistance,omitempty" bson:"varCentroidFaceDistance"`
}

type BlockStudentPosture struct {
	Id []*int32 `json:"id,omitempty" bson:"id"`
	NumOccurrencesInBlock []*int32 `json:"numOccurrencesInBlock,omitempty" bson:"numOccurrencesInBlock"`
	IsStandingFraction []*bool `json:"isStandingFraction,omitempty" bson:"isStandingFraction"`
	BodyPostureCategory []string `json:"bodyPostureCategory,omitempty" bson:"bodyPostureCategory"`
	BodyPostureCategoryFraction [][]*float64 `json:"bodyPostureCategoryFraction,omitempty" bson:"bodyPostureCategoryFraction"`
	HeadPostureCategory []string `json:"headPostureCategory,omitempty" bson:"headPostureCategory"`
	HeadPostureCategoryFraction [][]*float64 `json:"headPostureCategoryFraction,omitempty" bson:"headPostureCategoryFraction"`
	HandPostureCategory []string `json:"handPostureCategory,omitempty" bson:"handPostureCategory"`
	HandPostureCategoryFraction [][]*float64 `json:"handPostureCategoryFraction,omitempty" bson:"handPostureCategoryFraction"`
}

type SessionPostureAnalysis struct {
	Instructor SessionInstructorPosture `json:"instructor,omitempty" bson:"instructor"`
	Student SessionStudentPosture `json:"student,omitempty" bson:"student"`
}

type SessionInstructorPosture struct {
	BodyPosturePreference string `json:"bodyPosturePreference,omitempty" bson:"bodyPosturePreference"`
	PointingClusterCount *int32 `json:"pointingClusterCount,omitempty" bson:"pointingClusterCount"`
	PointingClusterCenter [][]*float64 `json:"pointingClusterCenter,omitempty" bson:"pointingClusterCenter"`
	PointingClusterSize []*int32 `json:"pointingClusterSize,omitempty" bson:"pointingClusterSize"`
}

type SessionStudentPosture struct {
	Id []*int32 `json:"id,omitempty" bson:"id"`
	HandPosturePreference []string `json:"handPosturePreference,omitempty" bson:"handPosturePreference"`
	HeadPosturePreference []string `json:"headPosturePreference,omitempty" bson:"headPosturePreference"`
}
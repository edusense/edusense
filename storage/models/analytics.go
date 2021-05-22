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
    AnalysisStartTime *int  `json:"analysisStartTime bson:"analysisStartTime"`
    TotalRuntime *float32 `json:"totalRuntime" bson:"totalRuntime"`
    RunModules []string `json:"runModules" bson:"runModules"`
    ModuleRuntime []*float32 `json:"moduleRuntime" bson:"moduleRuntime"`
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
	UnixSeconds *int `json:"unixSeconds,omitempty" bson:"unixSeconds"`
	FrameStart *int  `json:"frameStart,omitempty" bson:"frameStart"`
	FrameEnd *int  `json:"frameEnd,omitempty" bson:"frameEnd"`
}

type BlockInfo struct {
	UnixStartSeconds *int `json:"unixStartSeconds" bson:"unixStartSeconds"`
	BlockLength *int  `json:"blockLength" bson:"blockLength"`
	Id *int  `json:"id" bson:"id"`
}

type SessionInfo struct {
	UnixStartSeconds *int `json:"unixStartSeconds" bson:"unixStartSeconds"`
	SessionLength *int  `json:"blockLength" bson:"SessionLength"`
}

type SecondAudioAnalysis struct {
	IsSilence *bool `json:"isSilence,omitempty" bson:"isSilence"`
	IsObjectNoise *bool `json:"isObjectNoise,omitempty" bson:"isObjectNoise"`
	IsTeacherOnly *bool `json:"isTeacherOnly,omitempty" bson:"isTeacherOnly"`
	IsSingleSpeaker *bool `json:"isSingleSpeaker,omitempty" bson:"isSingleSpeaker"`
}

type BlockAudioAnalysis struct {
	SilenceFraction *float32 `json:"silenceFraction,omitempty" bson:"silenceFraction"`
	ObjectFraction *float32 `json:"objectFraction,omitempty" bson:"objectFraction"`
	TeacherOnlyFraction *float32 `json:"teacherOnlyFraction,omitempty" bson:"teacherOnlyFraction"`
	SingleSpeakerFraction *float32 `json:"singleSpeakerFraction,omitempty" bson:"singleSpeakerFraction"`
	TeacherActivityType []string `json:"teacherActivityType,omitempty" bson:"teacherActivityType"`
	TeacherActivityFraction []*float32 `json:"teacherActivityFraction,omitempty" bson:"teacherActivityFraction"`
	TeacherActivityTimes [][][]*int `json:"teacherActivityTimes,omitempty" bson:"teacherActivityTimes"`
}

type SessionAudioAnalysis struct {
	AudioBasedActivityType []string `json:"audioBasedActivityType,omitempty" bson:"audioBasedActivityType"`
	AudioBasedActivityFraction []*float32 `json:"audioBasedActivityFraction,omitempty" bson:"audioBasedActivityFraction"`
	AudioBasedActivityBlocks [][][]*int `json:"audioBasedActivityBlocks,omitempty" bson:"audioBasedActivityBlocks"`
}

type SecondGazeAnalysis struct {
	Instructor SecondInstructorGaze `json:"instructor,omitempty" bson:"instructor"`
	Student SecondStudentGaze `json:"student,omitempty" bson:"student"`
}

type SecondInstructorGaze struct {
	Angle *float32 `json:"angle,omitempty" bson:"angle"`
	AngleChange *float32 `json:"angleChange,omitempty" bson:"angleChange"`
	Direction *bool `json:"direction,omitempty" bson:"direction"`
	ViewingSectorThreshold *float32 `json:"viewingSectorThreshold,omitempty" bson:"viewingSectorThreshold"`
	CountStudentsInGaze *int `json:"countStudentsInGaze,omitempty" bson:"countStudentsInGaze"`
	TowardsStudents *bool `json:"towardsStudents,omitempty" bson:"towardsStudents"`
	LookingDown *bool `json:"lookingDown,omitempty" bson:"lookingDown"`
}

type PrincipalGaze struct {
	Direction []*float32 `json:"direction,omitempty" bson:"direction"`
	DirectionVariation []*float32 `json:"directionVariation,omitempty" bson:"directionVariation"`
	LongestStayFraction []*float32 `json:"longestStayFraction,omitempty" bson:"longestStayFraction"`
}

type SecondStudentGaze struct {
	Id []*int `json:"id,omitempty" bson:"id"`
	Angle []*float32 `json:"angle,omitempty" bson:"angle"`
	AngleChange []*float32 `json:"angleChange,omitempty" bson:"angleChange"`
	Direction []*bool `json:"direction,omitempty" bson:"direction"`
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
	TotalCategoryFraction []*float32 `json:"totalCategoryFraction,omitempty" bson:"totalCategoryFraction"`
	LongestCategoryFraction []*float32 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	PrincipalGaze PrincipalGaze `json:"principalGaze,omitempty" bson:"principalGaze"`
	RollMean *float32 `json:"rollMean,omitempty" bson:"rollMean"`
	YawMean *float32 `json:"yawMean,omitempty" bson:"yawMean"`
	PitchMean *float32 `json:"pitchMean,omitempty" bson:"pitchMean"`
	RollVariance *float32 `json:"rollVariance,omitempty" bson:"rollVariance"`
	YawVariance *float32 `json:"yawVariance,omitempty" bson:"yawVariance"`
	PitchVariance *float32 `json:"pitchVariance,omitempty" bson:"pitchVariance"`
}

type BlockStudentGaze struct {
	Id []*int `json:"id,omitempty" bson:"id"`
	NumOccurencesInBlock []*int `json:"numOccurencesInBlock,omitempty" bson:"numOccurencesInBlock"`
	GazeCategory []string `json:"gazeCategory,omitempty" bson:"gazeCategory"`
	TotalCategoryFraction [][]*float32 `json:"totalCategoryFraction,omitempty" bson:"totalCategoryFraction"`
	LongestCategoryFraction [][]*float32 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	DirectionMean [][]*float32 `json:"directionMean,omitempty" bson:"directionMean"`
	DirectionVariation [][]*float32 `json:"directionVariation,omitempty" bson:"directionVariation"`
	TowardsInstructorFraction []*float32 `json:"towardsInstructorFraction,omitempty" bson:"towardsInstructorFraction"`
	LookingDownFraction []*float32 `json:"lookingDownFraction,omitempty" bson:"lookingDownFraction"`
	LookingFrontFraction []*float32 `json:"lookingFrontFraction,omitempty" bson:"lookingFrontFraction"`
	RollMean []*float32 `json:"rollMean,omitempty" bson:"rollMean"`
	YawMean []*float32 `json:"yawMean,omitempty" bson:"yawMean"`
	PitchMean []*float32 `json:"pitchMean,omitempty" bson:"pitchMean"`
	RollVariance []*float32 `json:"rollVariance,omitempty" bson:"rollVariance"`
	YawVariance []*float32 `json:"yawVariance,omitempty" bson:"yawVariance"`
	PitchVariance []*float32 `json:"pitchVariance,omitempty" bson:"pitchVariance"`
}

type SessionGazeAnalysis struct {
	Instructor SessionInstructorGaze `json:"instructor,omitempty" bson:"instructor"`
	Student SessionStudentGaze `json:"student,omitempty" bson:"student"`
}

type SessionInstructorGaze struct {
	GazePreference string `json:"gazePreference,omitempty" bson:"gazePreference"`
	TopLocations [][]*float32 `json:"topLocations,omitempty" bson:"topLocations"`
	TopLocationsGazeLeftFraction [][]*float32 `json:"topLocationsGazeLeftFraction,omitempty" bson:"topLocationsGazeLeftFraction"`
	ObjectCategory []string `json:"objectCategory,omitempty" bson:"objectCategory"`
	LookingAtObjectFraction []*float32 `json:"lookingAtObjectFraction,omitempty" bson:"lookingAtObjectFraction"`
}

type SessionStudentGaze struct {
	Id []*int `json:"id,omitempty" bson:"id"`
	GazeCategory []string `json:"gazeCategory,omitempty" bson:"gazeCategory"`
	GazeCategoryFraction [][]*float32 `json:"gazeCategoryFraction,omitempty" bson:"gazeCategoryFraction"`
}

type SecondLocationAnalysis struct{
	Instructor SecondInstructorLocation `json:"instructor,omitempty" bson:"instructor"`
	Student SecondStudentLocation `json:"student,omitempty" bson:"student"`
}

type SecondInstructorLocation struct{
	AtBoard *bool `json:"atBoard,omitempty" bson:"atBoard"`
	AtPodium *bool `json:"atPodium,omitempty" bson:"atPodium"`
	IsMoving *bool `json:"isMoving,omitempty" bson:"isMoving"`
	LocationCoordinates []*int `json:"locationCoordinates,omitempty" bson:"locationCoordinates"`
	LocationEntropy *float32 `json:"locationEntropy,omitempty" bson:"locationEntropy"`
	HeadEntropy *float32 `json:"headEntropy,omitempty" bson:"headEntropy"`
}

type PrincipalMovement struct{
	DirectionMean []*float32 `json:"directionMean,omitempty" bson:"directionMean"`
	DirectionVariation []*float32 `json:"directionVariation,omitempty" bson:"directionVariation"`
	DirectionComps []*float32 `json:"directionComps,omitempty" bson:"directionComps"`
}

type SecondStudentLocation struct{
	Id []*int `json:"id,omitempty" bson:"id"`
	TrackingIdMap [][]*int `json:"trackingIdMap,omitempty" bson:"trackingIdMap"`
	IsMoving []*bool `json:"isMoving,omitempty" bson:"isMoving"`
	LocationCoordinates [][]*int `json:"locationCoordinates,omitempty" bson:"locationCoordinates"`
	LocationCategory []string `json:"locationCategory,omitempty" bson:"locationCategory"`
	LocationEntropy []*float32 `json:"locationEntropy,omitempty" bson:"locationEntropy"`
	HeadEntropy []*float32 `json:"headEntropy,omitempty" bson:"headEntropy"`	
}

type BlockLocationAnalysis struct{
	Instructor BlockInstructorLocation `json:"instructor,omitempty" bson:"instructor"`
	Student BlockStudentLocation `json:"student,omitempty" bson:"student"`
}

type BlockInstructorLocation struct{
	TotalBoardFraction *float32 `json:"totalBoardFraction,omitempty" bson:"totalBoardFraction"`
	LongestBoardFraction *float32 `json:"longestBoardFraction,omitempty" bson:"longestBoardFraction"`
	TotalPodiumFraction *float32 `json:"totalPodiumFraction,omitempty" bson:"totalPodiumFraction"`
	LongestPodiumFraction *float32 `json:"longestPodiumFraction,omitempty" bson:"longestPodiumFraction"`
	TotalMovingFraction *float32 `json:"totalMovingFraction,omitempty" bson:"totalMovingFraction"`
	LongestMovingFraction *float32 `json:"longestMovingFraction,omitempty" bson:"longestMovingFraction"`
	LocationCategory string `json:"locationCategory,omitempty" bson:"locationCategory"`
	CategoryFraction []*float32 `json:"CategoryFraction,omitempty" bson:"CategoryFraction"`
	LongestCategoryFraction []*float32 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	StayAtLocation [][]*int `json:"stayAtLocation,omitempty" bson:"stayAtLocation"`
	StayAtLocationTimes [][]*float32 `json:"stayAtLocationTimes,omitempty" bson:"stayAtLocationTimes"`
	LongestStayFraction *float32 `json:"longestStayFraction,omitempty" bson:"longestStayFraction"`
	PrincipalMovement PrincipalMovement `json:"principalMovement,omitempty" bson:"principalMovement"`
}

type BlockStudentLocation struct {
	Id []*int `json:"id,omitempty" bson:"id"`
	NumOccurrencesInBlock []*int `json:"numOccurrencesInBlock,omitempty" bson:"numOccurrencesInBlock"`
	IsSettled []*int `json:"isSettled,omitempty" bson:"isSettled"`
	MeanBodyEntropy []*float32 `json:"meanBodyEntropy,omitempty" bson:"meanBodyEntropy"`
	MaxBodyEntropy []*float32 `json:"maxBodyEntropy,omitempty" bson:"maxBodyEntropy"`
	VarBodyEntropy []*float32 `json:"varBodyEntropy,omitempty" bson:"varBodyEntropy"`
	MeanHeadEntropy []*float32 `json:"meanHeadEntropy,omitempty" bson:"meanHeadEntropy"`
	MaxHeadEntropy []*float32 `json:"maxHeadEntropy,omitempty" bson:"maxHeadEntropy"`
	VarHeadEntropy []*float32 `json:"varHeadEntropy,omitempty" bson:"varHeadEntropy"`
	StayCoordinates []*int `json:"stayCoordinates,omitempty" bson:"stayCoordinates"`
	ClusterCount *int `json:"clusterCount,omitempty" bson:"clusterCount"`
	ClusterCenters [][]*float32 `json:"clusterCenters,omitempty" bson:"clusterCenters"`
	ClusterStudentIds [][]*int `json:"clusterStudentIds,omitempty" bson:"clusterStudentIds"`
	SeatingArrangement string `json:"seatingArrangement,omitempty" bson:"seatingArrangement"`
}

type SessionLocationAnalysis struct {
	Instructor SessionInstructorLocation `json:"instructor,omitempty" bson:"instructor"`
	Student SessionStudentLocation `json:"student,omitempty" bson:"student"`
}

type SessionInstructorLocation struct {
	LocationBasedActivityType []string `json:"locationBasedActivityType,omitempty" bson:"locationBasedActivityType"`
	LocationBasedActivityFraction []*float32 `json:"locationBasedActivityFraction,omitempty" bson:"locationBasedActivityFraction"`
    LocationBasedActivityBlocks [][][]*int `json:"locationBasedActivityBlocks,omitempty" bson:"locationBasedActivityBlocks"`                
	LocationClusterCount *int `json:"locationClusterCount,omitempty" bson:"locationClusterCount"`
	LocationClusterCenter [][]*float32 `json:"locationClusterCenter,omitempty" bson:"locationClusterCenter"`
	LocationClusterSize []*int `json:"locationClusterSize,omitempty" bson:"locationClusterSize"`
	TotalBoardFraction *float32 `json:"totalBoardFraction,omitempty" bson:"totalBoardFraction"`
	LongestBoardFraction *float32 `json:"longestBoardFraction,omitempty" bson:"longestBoardFraction"`
	TotalPodiumFraction *float32 `json:"totalPodiumFraction,omitempty" bson:"totalPodiumFraction"`
	LongestPodiumFraction *float32 `json:"longestPodiumFraction,omitempty" bson:"longestPodiumFraction"`
	TotalMovingFraction *float32 `json:"totalMovingFraction,omitempty" bson:"totalMovingFraction"`
	LongestMovingFraction *float32 `json:"longestMovingFraction,omitempty" bson:"longestMovingFraction"`
	LocationCategory string `json:"locationCategory,omitempty" bson:"locationCategory"`
	CategoryFraction []*float32 `json:"CategoryFraction,omitempty" bson:"CategoryFraction"`
	LongestCategoryFraction []*float32 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
}

type SessionStudentLocation struct {
	Id []*int `json:"id,omitempty" bson:"id"`
	SettleDownTime []*float32 `json:"settleDownTime,omitempty" bson:"settleDownTime"`
	EntryTime []*float32 `json:"entryTime,omitempty" bson:"entryTime"`
	EntryLocation [][]*float32 `json:"entryLocation,omitempty" bson:"entryLocation"`
	ExitTime []*float32 `json:"exitTime,omitempty" bson:"exitTime"`
	ExitLocation [][]*float32 `json:"exitLocation,omitempty" bson:"exitLocation"`
	SeatingCategories []string `json:"seatingCategories,omitempty" bson:"seatingCategories"`
	SeatingCategoryBlocks [][]*int `json:"seatingCategoryBlocks,omitempty" bson:"seatingCategoryBlocks"`
}


type SecondPostureAnalysis struct {
	Instructor SecondInstructorPosture `json:"instructor,omitempty" bson:"instructor"`
	Student SecondStudentPosture `json:"student,omitempty" bson:"student"`
}

type SecondInstructorPosture struct{
	IsStanding *bool `json:"isStanding,omitempty" bson:"isStanding"`
	IsPointing *bool `json:"isPointing,omitempty" bson:"isPointing"`
	PointingDirection []*float32 `json:"pointingDirection,omitempty" bson:"pointingDirection"`
	HandPosture string `json:"handPosture,omitempty" bson:"handPosture"`
	HeadPosture string `json:"headPosture,omitempty" bson:"headPosture"`
	CentroidFaceDistance *float32 `json:"centroidFaceDistance,omitempty" bson:"centroidFaceDistance"`
	CentroidFaceDistanceAbsolute *float32 `json:"centroidFaceDistanceAbsolute,omitempty" bson:"centroidFaceDistanceAbsolute"`
}

type SecondStudentPosture struct{
	Id []*int `json:"id,omitempty" bson:"id"`
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
	StandingFraction *float32 `json:"standingFraction,omitempty" bson:"standingFraction"`
	HandPostureCategory []string `json:"handPostureCategory,omitempty" bson:"handPostureCategory"`
	HandPostureCategoryFraction []*float32 `json:"handPostureCategoryFraction,omitempty" bson:"handPostureCategoryFraction"`
	HeadPostureCategory []string `json:"headPostureCategory,omitempty" bson:"headPostureCategory"`
	HeadPostureCategoryFraction []*float32 `json:"headPostureCategoryFraction,omitempty" bson:"headPostureCategoryFraction"`
	MeanCentroidFaceDistance *float32 `json:"meanCentroidFaceDistance,omitempty" bson:"meanCentroidFaceDistance"`
	VarCentroidFaceDistance *float32 `json:"varCentroidFaceDistance,omitempty" bson:"varCentroidFaceDistance"`
}

type BlockStudentPosture struct {
	Id []*int `json:"id,omitempty" bson:"id"`
	NumOccurrencesInBlock []*int `json:"numOccurrencesInBlock,omitempty" bson:"numOccurrencesInBlock"`
	IsStandingFraction []*bool `json:"isStandingFraction,omitempty" bson:"isStandingFraction"`
	BodyPostureCategory []string `json:"bodyPostureCategory,omitempty" bson:"bodyPostureCategory"`
	BodyPostureCategoryFraction [][]*float32 `json:"bodyPostureCategoryFraction,omitempty" bson:"bodyPostureCategoryFraction"`
	HeadPostureCategory []string `json:"headPostureCategory,omitempty" bson:"headPostureCategory"`
	HeadPostureCategoryFraction [][]*float32 `json:"headPostureCategoryFraction,omitempty" bson:"headPostureCategoryFraction"`
	HandPostureCategory []string `json:"handPostureCategory,omitempty" bson:"handPostureCategory"`
	HandPostureCategoryFraction [][]*float32 `json:"handPostureCategoryFraction,omitempty" bson:"handPostureCategoryFraction"`
}

type SessionPostureAnalysis struct {
	Instructor SessionInstructorPosture `json:"instructor,omitempty" bson:"instructor"`
	Student SessionStudentPosture `json:"student,omitempty" bson:"student"`
}

type SessionInstructorPosture struct {
	BodyPosturePreference string `json:"bodyPosturePreference,omitempty" bson:"bodyPosturePreference"`
	PointingClusterCount *int `json:"pointingClusterCount,omitempty" bson:"pointingClusterCount"`
	PointingClusterCenter [][]*float32 `json:"pointingClusterCenter,omitempty" bson:"pointingClusterCenter"`
	PointingClusterSize []*int `json:"pointingClusterSize,omitempty" bson:"pointingClusterSize"`
}

type SessionStudentPosture struct {
	Id []*int `json:"id,omitempty" bson:"id"`
	HandPosturePreference []string `json:"handPosturePreference,omitempty" bson:"handPosturePreference"`
	HeadPosturePreference []string `json:"headPosturePreference,omitempty" bson:"headPosturePreference"`
}
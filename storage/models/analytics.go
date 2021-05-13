// Copyright (c) 2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

import (
	"time"
)

// 
type Analytics struct {
	ID        	 string      `json:"id" bson:"id"`
	Keyword   	 string      `json:"keyword" bson:"keyword"`
	MetaInfo  	 MetaInfo      `json:metaInfo" bson:"metaInfo"`
	DebugInfo 	 string    `json:"debugInfo,omitempty" bson:"debugInfo"`
	SecondLevel  SecondLevel    `json:"secondLevel,omitempty" bson:"secondLevel"`
	BlockLevel   BlockLevel    `json:"blockLevel,omitempty" bson:"blockLevel"`
	SessionLevel SessionLevel    `json:"SessionLevel,omitempty" bson:"SessionLevel"`
}

// 
type MetaInfo struct {
	PipelineVersion string `json:"pipelineVersion,omitempty" bson:"pipelineVersion"`
    AnalysisStartTime int  `json:"analysisStartTime bson:"analysisStartTime"`
    TotalRuntime float32 `json:"totalRuntime" bson:"totalRuntime"`
    RunModules []string `json:"RunModules" bson:"RunModules"`
    ModuleRuntime []float32 `json:"ModuleRuntime" bson:"ModuleRuntime"`
    SuccessModules []string `json:"SuccessModules" bson:"SuccessModules"`
    FailureModules []string `json:"FailureModules" bson:"FailureModules"`
}

type SecondLevel struct {
	SecondInfo SecondInfo `json:"secondInfo" bson:"secondInfo"`
	Audio Audio `json:"audio,omitempty" bson:"audio"`
	Gaze Gaze `json:"gaze,omitempty" bson:"gaze"`
	Location Location `json:"location,omitempty" bson:"location"`
	Posture Posture `json:"posture,omitempty" bson:"posture"`
	CrossModal string `json:"crossModal,omitempty" bson:"crossModal"`
}

type BlockLevel struct {
	BlockInfo BlockInfo `json:"blockInfo" bson:"blockInfo"`
	Audio Audio `json:"audio,omitempty" bson:"audio"`
	Gaze Gaze `json:"gaze,omitempty" bson:"gaze"`
	Location Location `json:"location,omitempty" bson:"location"`
	Posture Posture `json:"posture,omitempty" bson:"posture"`
	CrossModal string `json:"crossModal,omitempty" bson:"crossModal"`
}

type SessionLevel struct {
	SessionInfo SessionInfo `json:"sessionInfo" bson:"sessionInfo"`
	Audio Audio `json:"audio,omitempty" bson:"audio"`
	Gaze Gaze `json:"gaze,omitempty" bson:"gaze"`
	Location Location `json:"location,omitempty" bson:"location"`
	Posture Posture `json:"posture,omitempty" bson:"posture"`
	CrossModal string `json:"crossModal,omitempty" bson:"crossModal"`
}

type SecondInfo struct {
	UnixSeconds int `json:"unixSeconds,omitempty" bson:"unixSeconds"`
	FrameStart int  `json:"frameStart,omitempty" bson:"frameStart"`
	FrameEnd int  `json:"frameEnd,omitempty" bson:"frameEnd"`
}

type BlockInfo struct {
	UnixStartSeconds int `json:"unixStartSeconds" bson:"unixStartSeconds"`
	BlockLength int  `json:"blockLength" bson:"blockLength"`
	ID int  `json:"id" bson:"id"`
}

type SessionInfo struct {
	UnixStartSeconds int `json:"unixStartSeconds" bson:"unixStartSeconds"`
	SessionLength int  `json:"blockLength" bson:"SessionLength"`
}

type Audio struct {
	IsSilence bool `json:"isSilence,omitempty" bson:"isSilence"`
	IsObjectNoise bool `json:"isObjectNoise,omitempty" bson:"isObjectNoise"`
	IsTeacherOnly bool `json:"isTeacherOnly,omitempty" bson:"isTeacherOnly"`
	IsSingleSpeaker bool `json:"isSingleSpeaker,omitempty" bson:"isSingleSpeaker"`
	SilenceFraction float32 `json:"silenceFraction,omitempty" bson:"silenceFraction"`
	ObjectFraction float32 `json:"objectFraction,omitempty" bson:"objectFraction"`
	TeacherOnlyFraction float32 `json:"teacherOnlyFraction,omitempty" bson:"objectFraction"`
	SingleSpeakerFraction float32 `json:"singleSpeakerFraction,omitempty" bson:"singleSpeakerFraction"`
	TeacherActivityType []string `json:"teacherActivityType,omitempty" bson:"teacherActivityType"`
	TeacherActivityFraction []float32 `json:"teacherActivityFraction,omitempty" bson:"teacherActivityFraction"`
	TeacherActivityTimes [][]interface{} `json:"teacherActivityTimes,omitempty" bson:"teacherActivityTimes"`
	AudioBasedActivityType []string `json:"audioBasedActivityType,omitempty" bson:"audioBasedActivityType"`
	AudioBasedActivityFraction []float `json:"audioBasedActivityFraction,omitempty" bson:"audioBasedActivityFraction"`
	AudioBasedActivityBlocks [][]interface{} `json:"audioBasedActivityBlocks,omitempty" bson:"audioBasedActivityBlocks"`
}


type Gaze struct {
	Instructor InstructorGaze `json:"instructor,omitempty" bson:"instructor"`
	Student StudentGaze `json:"student,omitempty" bson:"student"`
}

type InstrcutorGaze struct {
	GazeCategory string `json:"gazeCategory,omitempty" bson:"gazeCategory"`
	TotalCategoryFraction []float32 `json:"totalCategoryFraction,omitempty" bson:"totalCategoryFraction"`
	LongestCategoryFraction []float32 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	PrincipalGaze PrincipalGaze `json:"principalGaze,omitempty" bson:"principalGaze"`
	RollMean float32 `json:"rollMean,omitempty" bson:"rollMean"`
	YawMean float32 `json:"yawMean,omitempty" bson:"yawMean"`
	PitchMean float32 `json:"pitchMean,omitempty" bson:"pitchMean"`
	RollVariance float32 `json:"rollVariance,omitempty" bson:"rollVariance"`
	YawVariance float32 `json:"yawVariance,omitempty" bson:"yawVariance"`
	PitchVariance float32 `json:"pitchVariance,omitempty" bson:"pitchVariance"`
	Angle float32 `json:"angle,omitempty" bson:"angle"`
	AngleChange float32 `json:"angleChange,omitempty" bson:"angleChange"`
	Direction bool `json:"direction,omitempty" bson:"direction"`
	ViewingSectorThreshold float32 `json:"viewingSectorThreshold,omitempty" bson:"viewingSectorThreshold"`
	CountStudentsInGaze int `json:"countStudentsInGaze,omitempty" bson:"countStudentsInGaze"`
	TowardsStudents bool `json:"towardsStudents,omitempty" bson:"towardsStudents"`
	LookingDown bool `json:"lookingDown,omitempty" bson:"lookingDown"`
}

type PrincipalGaze struct {
	Direction []float32 `json:"direction,omitempty" bson:"direction"`
	DirectionVariation []float32 `json:"directionVariation,omitempty" bson:"directionVariation"`
	LongestStayFraction []float32 `json:"longestStayFraction,omitempty" bson:"longestStayFraction"`
}

type StudentGaze struct {
	GazeCategory string `json:"gazeCategory,omitempty" bson:"gazeCategory"`
	ID []int `json:"id,omitempty" bson:"id"`
	Angle []float32 `json:"angle,omitempty" bson:"angle"`
	AngleChange []float32 `json:"angleChange,omitempty" bson:"angleChange"`
	Direction []bool `json:"direction,omitempty" bson:"direction"`
	TowardsInstructor []bool `json:"towardsInstructor,omitempty" bson:"towardsInstructor"`
	LookingDown []bool `json:"lookingDown,omitempty" bson:"lookingDown"`
	LookingFront []bool `json:"lookingFront,omitempty" bson:"lookingFront"`
	NumOccurencesInBlock []int `json:"numOccurencesInBlock,omitempty" bson:"numOccurencesInBlock"`
	TotalCategoryFraction [][]float32 `json:"totalCategoryFraction,omitempty" bson:"totalCategoryFraction"`
	LongestCategoryFraction [][]float32 `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	DirectionMean []interface{} `json:"directionMean,omitempty" bson:"directionMean"`
	DirectionVariation []interface{} `json:"directionVariation,omitempty" bson:"directionVariation"`
	TowardsInstructorFraction []float32 `json:"towardsInstructorFraction,omitempty" bson:"towardsInstructorFraction"`
	LookingDownFraction []float32 `json:"lookingDownFraction,omitempty" bson:"lookingDownFraction"`
	LookingFrontFraction []float32 `json:"lookingFrontFraction,omitempty" bson:"lookingFrontFraction"`
	RollMean []float32 `json:"rollMean,omitempty" bson:"rollMean"`
	YawMean []float32 `json:"yawMean,omitempty" bson:"yawMean"`
	PitchMean []float32 `json:"pitchMean,omitempty" bson:"pitchMean"`
	RollVariance []float32 `json:"rollVariance,omitempty" bson:"rollVariance"`
	YawVariance []float32 `json:"yawVariance,omitempty" bson:"yawVariance"`
	PitchVariance []float32 `json:"pitchVariance,omitempty" bson:"pitchVariance"`
}

type Location struct{
	Instructor InstructorLocation `json:"instructor,omitempty" bson:"instructor"`
	Student StudentLocation `json:"student,omitempty" bson:"student"`
}

type InstructorLocation struct{
	TotalBoardFraction float32 `json:"totalBoardFraction,omitempty" bson:"totalBoardFraction"`
	LongestBoardFraction float32 `json:"longestBoardFraction,omitempty" bson:"longestBoardFraction"`
	TotalPodiumFraction float32 `json:"totalPodiumFraction,omitempty" bson:"totalPodiumFraction"`
	LongestPodiumFraction float32 `json:"longestPodiumFraction,omitempty" bson:"longestPodiumFraction"`
	TotalMovingFraction float32 `json:"totalMovingFraction,omitempty" bson:"totalMovingFraction"`
	LongestMovingFraction float32 `json:"longestMovingFraction,omitempty" bson:"longestMovingFraction"`
	LocationCategory string `json:"locationCategory,omitempty" bson:"locationCategory"`
	CategoryFraction interface{} `json:"CategoryFraction,omitempty" bson:"CategoryFraction"`
	LongestCategoryFraction interface{} `json:"longestCategoryFraction,omitempty" bson:"longestCategoryFraction"`
	StayAtLocation []interface{} `json:"stayAtLocation,omitempty" bson:"stayAtLocation"`
	StayAtLocationTimes []interface{} `json:"stayAtLocationTimes,omitempty" bson:"stayAtLocationTimes"`
	LongestStayFraction []interface{} `json:"longestStayFraction,omitempty" bson:"longestStayFraction"`
	PrincipleMovement PrincipleMovement `json:"principleMovement,omitempty" bson:"principleMovement"`
	AtBoard bool `json:"atBoard,omitempty" bson:"atBoard"`
	AtPodium bool `json:"atPodium,omitempty" bson:"atPodium"`
	IsMoving bool `json:"isMoving,omitempty" bson:"isMoving"`
	LocationCoordinates interface{} `json:"locationCoordinates,omitempty" bson:"locationCoordinates"`
	LocationCategory string `json:"locationCategory,omitempty" bson:"locationCategory"`
	LocationEntropy float32 `json:"locationEntropy,omitempty" bson:"locationEntropy"`
	HeadEntropy float32 `json:"headEntropy,omitempty" bson:"headEntropy"`
	LocationBasedActivityType []string `json:"locationBasedActivityType,omitempty" bson:"locationBasedActivityType"`
	LocationBasedActivityFraction []float32 `json:"locationBasedActivityFraction,omitempty" bson:"locationBasedActivityFraction"`
    LocationBasedActivityBlocks [][]interface{} `json:"locationBasedActivityBlocks,omitempty" bson:"locationBasedActivityBlocks"`                
	LocationClusterCount int `json:"locationClusterCount,omitempty" bson:"locationClusterCount"`
	LocationClusterCenter [][]float32 `json:"locationClusterCenter,omitempty" bson:"locationClusterCenter"`
	LocationClusterSize []int `json:"locationClusterSize,omitempty" bson:"locationClusterSize"`
}

type PrincipalMovement struct{
	DirectionMean []float32 `json:"directionMean,omitempty" bson:"directionMean"`
	DirectionVariation []float32 `json:"directionVariation,omitempty" bson:"directionVariation"`
	DirectionComps []float32 `json:"directionComps,omitempty" bson:"directionComps"`
}

type StudentLocation struct{
}


type Posture struct{
	Instructor InstructorPosture `json:"instructor,omitempty" bson:"instructor"`
	Student StudentPosture `json:"student,omitempty" bson:"student"`
}

type InstructorPosture struct{
}

type StudentPosture struct{
}
package models

import (
	"time"
)

// AnalysisFrame Specification
type AnalysisFrame struct {
	FrameNumber 	uint32    `json:"frameNumber" bson:"frameNumber"`
	Timestamp   	time.Time `json:"timestamp" bson:"timestamp"`
	Channel     	string    `json:"channel" bson:"channel"`
	AnalysisData   	AnalysisData `json:"analysisData,omitempty" bson:"analysisData"`
}

// AnalysisData Specification
type AnalysisData struct {
	Students 	[]PersonAnalysis `json:"students,omitempty" bson:"students"`
	Instructors []PersonAnalysis `json:"instructors,omitempty" bson:"instructors"`
}

// PersonAnalysis Specification
type PersonAnalysis struct {
	Posture PostureAnalysis `json:"posture,omitempty" bson:"posture"`
	Face 	FaceAnalysis  `json:"face,omitempty" bson:"face"`
}

type PostureAnalysis struct {
	Upright 	bool `json:"upright,omitempty" bson:"upright"`
	Attention 	float32 `json:"attention,omitempty" bson:"attention"`
}

type FaceAnalysis struct {
	Emotion float32 `json:"emotion,omitempty" bson:"emotion"`
	Gaze 	float32 `json:"gaze,omitempty" bson:"gaze"`
}

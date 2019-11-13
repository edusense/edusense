// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

import (
	"time"
)

// Frame specification
type VideoFrame struct {
	FrameNumber uint32    `json:"frameNumber" bson:"frameNumber"`
	Timestamp   time.Time `json:"timestamp" bson:"timestamp"`
	Channel     string    `json:"channel" bson:"channel"`
	Thumbnail   Thumbnail `json:"thumbnail,omitempty" bson:"thumbnail"`
	People      []Person  `json:"people,omitempty" bson:"people"`
}

// Thumbnail specification
type Thumbnail struct {
	Rows   uint16 `json:"originalRows,omitempty" bson:"rows"`
	Cols   uint16 `json:"originalCols,omitempty" bson:"cols"`
	Binary []byte `json:"binary,omitempty" bson:"binary"`
}

// Person specification
type Person struct {
	Body       []uint16        `json:"body,omitempty" bson:"body"`
	Face       []uint16        `json:"face,omitempty" bson:"face"`
	Hand       []uint16        `json:"hand,omitempty" bson:"hand"`
	OpenposeID uint16          `json:"openposeId,omitempty" bson:"openposeId"`
	Inference  PersonInference `json:"inference,omitempty" bson:"inference"`
}

// Inference specification
type PersonInference struct {
	Posture    Posture `json:"posture,omitempty" bson:"posture"`
	Face       Face    `json:"face,omitempty" bson:"face"`
	Head       Head    `json:"head,omitempty" bson:"head"`
	TrackingID int16   `json:"trackingId,omitempty" bson:"trackingId"`
}

// Posture specification
type Posture struct {
	ArmPose       string    `json:"armPose,omitempty" bson:"armPose"`
	SitStand      string    `json:"sitStand,omitempty" bson:"sitStand"`
	CentroidDelta []int16   `json:"centroidDelta,omitempty" bson:"centroidDelta"`
	ArmDelta      [][]int16 `json:"armDelta,omitempty" bson:"armDelta"`
}

// Face specification
type Face struct {
	BoundingBox [][]int16 `json:"boundingBox,omitempty" bson:"boundingBox"`
	MouthOpen   string    `json:"mouthOpen,omitempty" bson:"mouthOpen"`
	MouthSmile  string    `json:"mouthSmile,omitempty" bson:"mouthSmile"`
	Orientation string    `json:"orientation,omitempty" bson:"orientation"`
}

// Head specification
type Head struct {
	Roll              float32     `json:"roll,omitempty" bson:"roll"`
	Pitch             float32     `json:"pitch,omitempty" bson:"pitch"`
	Yaw               float32     `json:"yaw,omitempty" bson:"yaw"`
	TranslationVector []float32   `json:"translationVector,omitempty" bson:"translationVector"`
	GazeVector        [][]float32 `json:"gazeVector,omitempty" bson:"gazeVector"`
}

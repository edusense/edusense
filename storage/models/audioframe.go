// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

import (
	"time"
)

// AudioFrame defines mongoDB
type AudioFrame struct {
	FrameNumber uint32    `json:"frameNumber" bson:"frameNumber"`
	Timestamp   time.Time `json:"timestamp" bson:"timestamp"`
	Channel     string    `json:"channel" bson:"channel"`
	Audio       Audio     `json:"audio" bson:"audio"`
}

// Audio defines
type Audio struct {
	Amplitude    float32        `json:"amplitude" bson:"amplitude"`
	MelFrequency [][]float32    `json:"melFrequency" bson:"melFrequency"`
	Inference    AudioInference `json:"inference" bson:"inference"`
}

// Inference from single stream specification
type AudioInference struct {
	Speech Speech `json:"speech,omitempty" bson:"speech"`
}

// Speech specification
type Speech struct {
	Confidence float32 `json:"confidence,omitempty" bson:"confidence"`
	Speaker    string  `json:"speaker,omitempty" bson:"speaker"`
}

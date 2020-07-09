// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

import (
	"time"
)

// AudioFrame defines mongoDB
type RaspiFrame struct {
	FrameNumber uint32    `json:"frameNumber" bson:"frameNumber"`
	Timestamp   time.Time `json:"timestamp" bson:"timestamp"`
	Channel     string    `json:"channel" bson:"channel"`
	Audio       Audio_rpi `json:"audio" bson:"audio"`
}

// Audio defines
type Audio_rpi struct {
	SSL	map[int][]float64	`json:"ssl" bson:"ssl"`
	FFT	[]float64		`json:"fft" bson:"fft"`
	SST	map[int][]float64	`json:"sst" bson:"sst"`
}

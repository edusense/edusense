// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

import (
	"time"
)

// Frame filter specification for range search
type FrameFilter struct {
	FrameStart uint32    `json:"startFrame,omitempty" bson:"startFrame"`
	FrameEnd   uint32    `json:"endFrame,omitempty" bson:"endFrame"`
	TimeStart  time.Time `json:"startTime,omitempty" bson:"startTime"`
	TimeEnd    time.Time `json:"endTime,omitempty" bson:"endTime"`
}

type FrameNumberFilter struct {
	Operator    string
	FrameNumber uint32
}

type TimestampFilter struct {
	Operator  string
	Timestamp time.Time
}

// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

// This struct can be used to store general details about the database
type Classroom struct {
	Building		string		`json:"building,omitempty" bson:"building"`
	Room			string		`json:"room,omitempty" bson:"room"`
	Floor			string		`json:"floor,omitempty" bson:"floor"`
	Dimensions		[]float32	`json:"dimensions,omitempty" bson:"dimensions"`
	DimensionsScale		string		`json:"dimensionsScale,omitempty" bson:"dimensionsScale"`
	NumberOfSeats		uint32		`json:"numberOfSeats,omitempty" bson:"numberOfSeats"`
	NumberofWindows		uint32		`json:"numberOfWindows,omitempty" bson:"numberOfWindows"`

	FrontCameraModel	string		`json:"frontCameraModel,omitempty" bson:"frontCameraModel"`
	RearCameraModel		string		`json:"rearCameraModel,omitempty" bson:"rearCameraModel"`
	FrontCameraIP		string		`json:"frontCameraIP,omitempty" bson:"frontCameraIP"`
	RearCameraIP		string          `json:"rearCameraIP,omitempty" bson:"rearCameraIP"`

	BlackboardBoundary	[]float32	`json:"blackboardBoundary,omitempty" bson:"blackboardBoundary"`
	PodiumBoundary		[]float32       `json:"podiumBoundary,omitempty" bson:"podiumBoundary"`
	ProjectorBoundary	[]float32       `json:"projectorBoundary,omitempty" bson:"projectorBoundary"`

	Courses			[]string	`json:"courses,omitempty" bson:"courses"`
}


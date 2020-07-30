// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

// This struct can be used to store general details about the database
type Course struct {
	ClassID			string		`json:"classID,omitempty" bson:"classID"`
	Section			string		`json:"section,omitempty" bson:"section"`
	Semester                string          `json:"semester,omitempty" bson:"semester"`
	Year                    uint16          `json:"year,omitempty" bson:"year"`
	LectureType		string		`json:"lectureType,omitempty" bson:"lectureType"`

	Instructors		[][]string      `json:"instructors,omitempty" bson:"instructors"`
	TeachingAssistants	[][]string      `json:"teachingAssistants,omitempty" bson:"teachingAssistants"`
	InitialEnrollment	uint16		`json:"initEnrollment,omitempty" bson:"initialEnrollment"`

}


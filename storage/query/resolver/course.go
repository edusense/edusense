// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

import (//"fmt"
	"context"
//	"errors"
	"time"

	//graphql "github.com/graph-gophers/graphql-go"
//	dbhandler "go.edusense.io/storage/dbhandler"
	models "go.edusense.io/storage/models"
)

// SessionResolver queries database and resolves query-agnostic Session model.
type CourseResolver struct {
	CourseMetadata    models.Course
}


// Sessions returns list of session resolvers from underlying database.
func (q QueryResolver) Courses (ctx context.Context) ([]*CourseResolver, error) {
	//To search database from creation of database until now
	filter := &models.SessionFilter{
		TimestampStart: time.Unix(0, 0),
		TimestampEnd:   time.Now(),
	}

	sessions, err := q.Driver.GetCourse(filter)
	if err != nil {
		return []*CourseResolver{}, err
	}

	resolvers := make([]*CourseResolver, len(sessions))
	for i, f := range sessions {
		resolvers[i] = &CourseResolver{CourseMetadata : f}
	}

	return resolvers, nil
}

// ID extracts Session ID from given Session resolver.
func (s *CourseResolver) ClassID(ctx context.Context) (string, error) {
	return s.CourseMetadata.ClassID, nil
}

func (s *CourseResolver) Section(ctx context.Context) (string, error) {
	return s.CourseMetadata.Section, nil
}

func (s *CourseResolver) Semester(ctx context.Context) (string, error) {
	return s.CourseMetadata.Semester, nil
}

func (s *CourseResolver) Year(ctx context.Context) (int32, error) {
	return int32(s.CourseMetadata.Year), nil
}

func (s *CourseResolver) LectureType(ctx context.Context) (string, error) {
	return s.CourseMetadata.LectureType, nil
}

func (s *CourseResolver) Instructors(ctx context.Context) ([][]string, error) {
	return s.CourseMetadata.Instructors, nil
}

func (s *CourseResolver) TeachingAssistants(ctx context.Context) ([][]string, error) {
	return s.CourseMetadata.TeachingAssistants, nil
}

func (s *CourseResolver) InitialEnrollment(ctx context.Context) (int32, error) {
	return int32(s.CourseMetadata.InitialEnrollment), nil
}

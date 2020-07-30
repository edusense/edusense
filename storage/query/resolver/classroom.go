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
type ClassroomResolver struct {
	Classroom_metadata    models.Classroom
}


// Sessions returns list of session resolvers from underlying database.
func (q QueryResolver) Classrooms (ctx context.Context) ([]*ClassroomResolver, error) {
	//To search database from creation of database until now

	/*resolvers := &ClassroomResolver{Classroom_metadata : models.Classroom{Building : "YOBuilding"}}
	fmt.Println(resolvers)
	pesolvers := make([]*ClassroomResolver, 2)
	pesolvers[0] = &ClassroomResolver{Classroom_metadata : models.Classroom{Building : "AnotherBuilding"}}
	pesolvers[1] = &ClassroomResolver{Classroom_metadata : models.Classroom{Building : "AnotherBuilding"}}
	*/

        filter := &models.SessionFilter{
		TimestampStart: time.Unix(0, 0),
		TimestampEnd:   time.Now(),
	}

	sessions, err := q.Driver.GetClassroom(filter)
	if err != nil {
		return []*ClassroomResolver{}, err
	}

	resolvers := make([]*ClassroomResolver, len(sessions))
	for i, f := range sessions {
		resolvers[i] = &ClassroomResolver{Classroom_metadata : f}
	}

	return resolvers, nil
}

// ID extracts Session ID from given Session resolver.
func (s *ClassroomResolver) Building(ctx context.Context) (string, error) {
	return s.Classroom_metadata.Building, nil
}

func (s *ClassroomResolver) Room(ctx context.Context) (string, error) {
	return s.Classroom_metadata.Room, nil
}

func (s *ClassroomResolver) Floor(ctx context.Context) (string, error) {
	return s.Classroom_metadata.Floor, nil
}

func (s *ClassroomResolver) Dimensions(ctx context.Context) ([]float64, error) {
	dimensions := make([]float64, len(s.Classroom_metadata.Dimensions))
	for i := range s.Classroom_metadata.Dimensions {
		dimensions[i] = float64(s.Classroom_metadata.Dimensions[i])
	}

	return dimensions, nil
}

func (s *ClassroomResolver) DimensionsScale(ctx context.Context) (string, error) {
	return s.Classroom_metadata.DimensionsScale, nil
}

func (s *ClassroomResolver) NumberOfSeats(ctx context.Context) (int32, error) {
	return int32(s.Classroom_metadata.NumberOfSeats), nil
}

func (s *ClassroomResolver) NumberOfWindows(ctx context.Context) (int32, error) {
	return int32(s.Classroom_metadata.NumberOfWindows), nil
}

func (s *ClassroomResolver) FrontCameraModel(ctx context.Context) (string, error) {
	return s.Classroom_metadata.FrontCameraModel, nil
}

func (s *ClassroomResolver) RearCameraModel(ctx context.Context) (string, error) {
	return s.Classroom_metadata.RearCameraModel, nil
}

func (s *ClassroomResolver) FrontCameraIP(ctx context.Context) (string, error) {
	return s.Classroom_metadata.FrontCameraIP, nil
}

func (s *ClassroomResolver) RearCameraIP(ctx context.Context) (string, error) {
	return s.Classroom_metadata.RearCameraIP, nil
}

func (s *ClassroomResolver) BlackboardBoundary(ctx context.Context) ([][]float64, error) {
	if len(s.Classroom_metadata.BlackboardBoundary) == 0 {
		return [][]float64{}, nil
	}

	blackboard := make([][]float64, len(s.Classroom_metadata.BlackboardBoundary))
	for i, m := range s.Classroom_metadata.BlackboardBoundary {
		arr := make([]float64, len(m))
		for j, k := range m {
			arr[j] = float64(k)
		}
		blackboard[i] = arr
	}

	return blackboard, nil
}

func (s *ClassroomResolver) PodiumBoundary(ctx context.Context) ([][]float64, error) {
	if len(s.Classroom_metadata.PodiumBoundary) == 0 {
		return [][]float64{}, nil
	}

	podium := make([][]float64, len(s.Classroom_metadata.PodiumBoundary))
	for i, m := range s.Classroom_metadata.PodiumBoundary {
		arr := make([]float64, len(m))
		for j, k := range m {
			arr[j] = float64(k)
		}
		podium[i] = arr
	}

	return podium, nil
}


func (s *ClassroomResolver) ProjectorBoundary(ctx context.Context) ([][]float64, error) {
	if len(s.Classroom_metadata.ProjectorBoundary) == 0 {
		return [][]float64{}, nil
	}

	projector := make([][]float64, len(s.Classroom_metadata.ProjectorBoundary))
	for i, m := range s.Classroom_metadata.ProjectorBoundary {
		arr := make([]float64, len(m))
		for j, k := range m {
			arr[j] = float64(k)
		}
		projector[i] = arr
	}

	return projector, nil
}

func (s *ClassroomResolver) Courses(ctx context.Context) ([][]string, error) {
	return s.Classroom_metadata.Courses, nil
}


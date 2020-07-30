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
	ClassroomMetadata    models.Classroom
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
		resolvers[i] = &ClassroomResolver{ClassroomMetadata : f}
	}

	return resolvers, nil
}

// ID extracts Session ID from given Session resolver.
func (s *ClassroomResolver) Building(ctx context.Context) (string, error) {
	return s.ClassroomMetadata.Building, nil
}

func (s *ClassroomResolver) Room(ctx context.Context) (string, error) {
	return s.ClassroomMetadata.Room, nil
}

func (s *ClassroomResolver) Floor(ctx context.Context) (string, error) {
	return s.ClassroomMetadata.Floor, nil
}

func (s *ClassroomResolver) Dimensions(ctx context.Context) ([]float64, error) {
	dimensions := make([]float64, len(s.ClassroomMetadata.Dimensions))
	for i := range s.ClassroomMetadata.Dimensions {
		dimensions[i] = float64(s.ClassroomMetadata.Dimensions[i])
	}

	return dimensions, nil
}

func (s *ClassroomResolver) DimensionsScale(ctx context.Context) (string, error) {
	return s.ClassroomMetadata.DimensionsScale, nil
}

func (s *ClassroomResolver) NumberOfSeats(ctx context.Context) (int32, error) {
	return int32(s.ClassroomMetadata.NumberOfSeats), nil
}

func (s *ClassroomResolver) NumberOfWindows(ctx context.Context) (int32, error) {
	return int32(s.ClassroomMetadata.NumberOfWindows), nil
}

func (s *ClassroomResolver) FrontCameraModel(ctx context.Context) (string, error) {
	return s.ClassroomMetadata.FrontCameraModel, nil
}

func (s *ClassroomResolver) RearCameraModel(ctx context.Context) (string, error) {
	return s.ClassroomMetadata.RearCameraModel, nil
}

func (s *ClassroomResolver) FrontCameraIP(ctx context.Context) (string, error) {
	return s.ClassroomMetadata.FrontCameraIP, nil
}

func (s *ClassroomResolver) RearCameraIP(ctx context.Context) (string, error) {
	return s.ClassroomMetadata.RearCameraIP, nil
}

func (s *ClassroomResolver) BlackboardBoundary(ctx context.Context) ([][]float64, error) {
	if len(s.ClassroomMetadata.BlackboardBoundary) == 0 {
		return [][]float64{}, nil
	}

	blackboard := make([][]float64, len(s.ClassroomMetadata.BlackboardBoundary))
	for i, m := range s.ClassroomMetadata.BlackboardBoundary {
		arr := make([]float64, len(m))
		for j, k := range m {
			arr[j] = float64(k)
		}
		blackboard[i] = arr
	}

	return blackboard, nil
}

func (s *ClassroomResolver) PodiumBoundary(ctx context.Context) ([][]float64, error) {
	if len(s.ClassroomMetadata.PodiumBoundary) == 0 {
		return [][]float64{}, nil
	}

	podium := make([][]float64, len(s.ClassroomMetadata.PodiumBoundary))
	for i, m := range s.ClassroomMetadata.PodiumBoundary {
		arr := make([]float64, len(m))
		for j, k := range m {
			arr[j] = float64(k)
		}
		podium[i] = arr
	}

	return podium, nil
}


func (s *ClassroomResolver) ProjectorBoundary(ctx context.Context) ([][]float64, error) {
	if len(s.ClassroomMetadata.ProjectorBoundary) == 0 {
		return [][]float64{}, nil
	}

	projector := make([][]float64, len(s.ClassroomMetadata.ProjectorBoundary))
	for i, m := range s.ClassroomMetadata.ProjectorBoundary {
		arr := make([]float64, len(m))
		for j, k := range m {
			arr[j] = float64(k)
		}
		projector[i] = arr
	}

	return projector, nil
}

func (s *ClassroomResolver) CourseList(ctx context.Context) ([][]string, error) {
	return s.ClassroomMetadata.CourseList, nil
}


// Copyright (c) 2017-2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

type AnalyticsArgs struct {
	SessionID *string
	Keyword *string
}


func (q QueryResolver) Analytics (ctx context.Context, args AnalyticsArgs) ([]*AnalyticsResolver, error) {
	if args.SessionID != nil || args.Keyword != nil {
		selected_analytics, err := q.Driver.GetAnalyticsFilter(args.SessionID, args.Keyword)

		if err != nil {
			return []*AnalyticsResolver{}, err
		}

		resolvers := make([]*AnalyticsResolver, len(selected_analytics))

		for i, f := range selected_analytics {
			resolvers[i] = &AnalyticsResolver{Analytics : f}
		}
		return resolvers, nil
	}
	
	
	all_analytics, err := q.Driver.GetAnalytics()
	if err != nil {
		return []*AnalyticsResolver{}, err
	}
	resolvers := make([]*AnalyticsResolver, len(all_analytics))

	for i, f := range all_analytics {
		resolvers[i] = &AnalyticsResolver{Analytics : f}
	}

	return resolvers, nil
}


type AnalyticsResolver struct {
	Analytics models.Analytics
}


func (a *AnalyticsResolver) Id(ctx context.Context) (string, error) {
	return a.Analytics.Id, nil
}

func (a *AnalyticsResolver) Keyword(ctx context.Context) (string, error) {
	return a.Analytics.Keyword, nil
}

func (a *AnalyticsResolver) MetaInfo(ctx context.Context) (*MetaInfoResolver, error) {
	return &MetaInfoResolver{MetaInfo: a.Analytics.MetaInfo}, nil
}

func (a *AnalyticsResolver) DebugInfo(ctx context.Context) (string, error) {
	return a.Analytics.DebugInfo, nil
}

func (a *AnalyticsResolver) SecondLevel(ctx context.Context) ([]*SecondLevelResolver, error) {
	vector := make([]*SecondLevelResolver, len(a.Analytics.SecondLevel))
	for i, k := range a.Analytics.SecondLevel {
		vector[i] = &SecondLevelResolver{SecondLevel: k}
	}
	return vector, nil
}

func (a *AnalyticsResolver) BlockLevel(ctx context.Context) ([]*BlockLevelResolver, error) {
	vector := make([]*BlockLevelResolver, len(a.Analytics.BlockLevel))
	for i, k := range a.Analytics.BlockLevel {
		vector[i] = &BlockLevelResolver{BlockLevel: k}
	}
	return vector, nil
}

func (a *AnalyticsResolver) SessionLevel(ctx context.Context) (*SessionLevelResolver, error) {
	return &SessionLevelResolver{SessionLevel: a.Analytics.SessionLevel}, nil
}


type MetaInfoResolver struct {
	MetaInfo models.MetaInfo
}

func (m *MetaInfoResolver) PipelineVersion(ctx context.Context) (string, error) {
	return m.MetaInfo.PipelineVersion, nil
}

func (m *MetaInfoResolver) AnalysisStartTime(ctx context.Context) (int32, error) {
	return int32(*m.MetaInfo.AnalysisStartTime), nil
}

func (m *MetaInfoResolver) TotalRuntime(ctx context.Context) (float64, error) {
	return float64(*m.MetaInfo.TotalRuntime), nil
}

func (m *MetaInfoResolver) RunModules(ctx context.Context) ([]string, error) {

	return m.MetaInfo.RunModules, nil
}

func (m *MetaInfoResolver) ModuleRuntime(ctx context.Context) ([]float64, error) {
	vector := make([]float64, len(m.MetaInfo.ModuleRuntime))
	for i, k := range m.MetaInfo.ModuleRuntime {
		vector[i] = float64(*k)
	}
	return vector, nil
}

func (m *MetaInfoResolver) SuccessModules(ctx context.Context) ([]string, error) {
	return m.MetaInfo.SuccessModules, nil
}

func (m *MetaInfoResolver) FailureModules(ctx context.Context) ([]string, error) {
	return m.MetaInfo.FailureModules, nil
}

type SecondLevelResolver struct {
	SecondLevel models.SecondLevel
}

func (s *SecondLevelResolver) SecondInfo(ctx context.Context) (*SecondInfoResolver, error) {
	return &SecondInfoResolver{SecondInfo: s.SecondLevel.SecondInfo} , nil
}

func (s *SecondLevelResolver) Audio(ctx context.Context) (*SecondAudioAnalysisResolver, error) {
	return &SecondAudioAnalysisResolver{Audio: s.SecondLevel.Audio} , nil
}

func (s *SecondLevelResolver) Gaze(ctx context.Context) (*SecondGazeAnalysisResolver, error) {
	return &SecondGazeAnalysisResolver{Gaze: s.SecondLevel.Gaze} , nil
}

func (s *SecondLevelResolver) Location(ctx context.Context) (*SecondLocationAnalysisResolver, error) {
	return &SecondLocationAnalysisResolver{Location: s.SecondLevel.Location} , nil
}

func (s *SecondLevelResolver) Posture(ctx context.Context) (*SecondPostureAnalysisResolver, error) {
	return &SecondPostureAnalysisResolver{Posture: s.SecondLevel.Posture} , nil
}

func (s *SecondLevelResolver) CrossModal(ctx context.Context) (*string, error) {
	return &s.SecondLevel.CrossModal , nil
}

type SecondInfoResolver struct {
	SecondInfo models.SecondInfo
}

func (s *SecondInfoResolver) UnixSeconds(ctx context.Context) (*int32, error) {
	return s.SecondInfo.UnixSeconds, nil
}

func (s *SecondInfoResolver) FrameStart(ctx context.Context) (*int32, error) {
	return s.SecondInfo.FrameStart, nil
}

func (s *SecondInfoResolver) FrameEnd(ctx context.Context) (*int32, error) {
	return s.SecondInfo.FrameEnd, nil
}


type SecondAudioAnalysisResolver struct {
	Audio models.SecondAudioAnalysis
}

func (s *SecondAudioAnalysisResolver) IsSilence(ctx context.Context) (*bool, error) {
	return s.Audio.IsSilence, nil
}

func (s *SecondAudioAnalysisResolver) IsObjectNoise(ctx context.Context) (*bool, error) {
	return s.Audio.IsObjectNoise, nil
}

func (s *SecondAudioAnalysisResolver) IsTeacherOnly(ctx context.Context) (*bool, error) {
	return s.Audio.IsTeacherOnly, nil
}

func (s *SecondAudioAnalysisResolver) IsSingleSpeaker(ctx context.Context) (*bool, error) {
	return s.Audio.IsSingleSpeaker, nil
}

type SecondGazeAnalysisResolver struct {
	Gaze models.SecondGazeAnalysis
}

func (s *SecondGazeAnalysisResolver) Instructor(ctx context.Context) (*SecondInstructorGazeResolver, error) {
	return &SecondInstructorGazeResolver{Instructor: s.Gaze.Instructor}, nil
}

func (s *SecondGazeAnalysisResolver) Student(ctx context.Context) (*SecondStudentGazeResolver, error) {
	return &SecondStudentGazeResolver{Student: s.Gaze.Student}, nil
}

type SecondInstructorGazeResolver struct {
	Instructor models.SecondInstructorGaze
}

func (s *SecondInstructorGazeResolver) Angle(ctx context.Context) (*float64, error) {
	return s.Instructor.Angle, nil
}

func (s *SecondInstructorGazeResolver) AngleChange(ctx context.Context) (*float64, error) {
	return s.Instructor.AngleChange, nil
}

func (s *SecondInstructorGazeResolver) Direction(ctx context.Context) (*string, error) {
	return s.Instructor.Direction, nil
}

func (s *SecondInstructorGazeResolver) ViewingSectorThreshold(ctx context.Context) (*float64, error) {
	return s.Instructor.ViewingSectorThreshold, nil
}

func (s *SecondInstructorGazeResolver) CountStudentsInGaze(ctx context.Context) (*int32, error) {
	return s.Instructor.CountStudentsInGaze, nil
}

func (s *SecondInstructorGazeResolver) TowardsStudents(ctx context.Context) (*bool, error) {
	return s.Instructor.TowardsStudents, nil
}

func (s *SecondInstructorGazeResolver) LookingDown(ctx context.Context) (*bool, error) {
	return s.Instructor.LookingDown, nil
}

type SecondStudentGazeResolver struct {
	Student models.SecondStudentGaze
}

func (s *SecondStudentGazeResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentGazeResolver) Angle(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.Angle))
	for i, k := range s.Student.Angle {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentGazeResolver) AngleChange(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.AngleChange))
	for i, k := range s.Student.AngleChange {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentGazeResolver) Direction(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.Direction))
	for i, k := range s.Student.Direction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentGazeResolver) TowardsInstructor(ctx context.Context) (*[]*bool, error) {
	vector := make([]*bool, len(s.Student.TowardsInstructor))
	for i, k := range s.Student.TowardsInstructor {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentGazeResolver) LookingDown(ctx context.Context) (*[]*bool, error) {
	vector := make([]*bool, len(s.Student.LookingDown))
	for i, k := range s.Student.LookingDown {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentGazeResolver) LookingFront(ctx context.Context) (*[]*bool, error) {
	vector := make([]*bool, len(s.Student.LookingFront))
	for i, k := range s.Student.LookingFront {
		vector[i] = k
	}
	return &vector, nil
}

type SecondLocationAnalysisResolver struct {
	Location models.SecondLocationAnalysis
}

func (s *SecondLocationAnalysisResolver) Instructor(ctx context.Context) (*SecondInstructorLocationResolver, error) {
	return &SecondInstructorLocationResolver{Instructor: s.Location.Instructor}, nil
}

func (s *SecondLocationAnalysisResolver) Student(ctx context.Context) (*SecondStudentLocationResolver, error) {
	return &SecondStudentLocationResolver{Student: s.Location.Student}, nil
}

type SecondInstructorLocationResolver struct {
	Instructor models.SecondInstructorLocation
}

func (s *SecondInstructorLocationResolver) AtBoard(ctx context.Context) (*bool, error) {
	return s.Instructor.AtBoard, nil
}

func (s *SecondInstructorLocationResolver) AtPodium(ctx context.Context) (*bool, error) {
	return s.Instructor.AtPodium, nil
}

func (s *SecondInstructorLocationResolver) IsMoving(ctx context.Context) (*bool, error) {
	return s.Instructor.IsMoving, nil
}

func (s *SecondInstructorLocationResolver) LocationCoordinates(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Instructor.LocationCoordinates))
	for i, k := range s.Instructor.LocationCoordinates {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondInstructorLocationResolver) LocationCategory(ctx context.Context) (*string, error) {
	return s.Instructor.LocationCategory, nil
}

func (s *SecondInstructorLocationResolver) LocationEntropy(ctx context.Context) (*float64, error) {
	return s.Instructor.LocationEntropy, nil
}

func (s *SecondInstructorLocationResolver) HeadEntropy(ctx context.Context) (*float64, error) {
	return s.Instructor.HeadEntropy, nil
}

type SecondStudentLocationResolver struct {
	Student models.SecondStudentLocation
}


func (s *SecondStudentLocationResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentLocationResolver) TrackingIdMap(ctx context.Context) (*[][]*int32, error) {
	matrix := s.Student.TrackingIdMap
	vector := make([][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *SecondStudentLocationResolver) IsMoving(ctx context.Context) (*[]*bool, error) {
	vector := make([]*bool, len(s.Student.IsMoving))
	for i, k := range s.Student.IsMoving {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentLocationResolver) LocationCoordinates(ctx context.Context) (*[][]*int32, error) {
	matrix := s.Student.LocationCoordinates
	vector := make([][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *SecondStudentLocationResolver) LocationCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.LocationCategory))
	for i, k := range s.Student.LocationCategory {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentLocationResolver) LocationEntropy(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.LocationEntropy))
	for i, k := range s.Student.LocationEntropy {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentLocationResolver) HeadEntropy(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.HeadEntropy))
	for i, k := range s.Student.HeadEntropy {
		vector[i] = k
	}
	return &vector, nil
}



// ********************************************************************************

type SecondPostureAnalysisResolver struct {
	Posture models.SecondPostureAnalysis
}

func (s *SecondPostureAnalysisResolver) Instructor(ctx context.Context) (*SecondInstructorPostureResolver, error) {
	return &SecondInstructorPostureResolver{Instructor: s.Posture.Instructor}, nil
}

func (s *SecondPostureAnalysisResolver) Student(ctx context.Context) (*SecondStudentPostureResolver, error) {
	return &SecondStudentPostureResolver{Student: s.Posture.Student}, nil
}

type SecondInstructorPostureResolver struct {
	Instructor models.SecondInstructorPosture
}

func (s *SecondInstructorPostureResolver) IsStanding(ctx context.Context) (*bool, error) {
	return s.Instructor.IsStanding, nil
}

func (s *SecondInstructorPostureResolver) IsPointing(ctx context.Context) (*bool, error) {
	return s.Instructor.IsPointing, nil
}

func (s *SecondInstructorPostureResolver) PointingDirection(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.PointingDirection))
	for i, k := range s.Instructor.PointingDirection {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondInstructorPostureResolver) HandPosture(ctx context.Context) (*string, error) {
	return &s.Instructor.HandPosture, nil
}

func (s *SecondInstructorPostureResolver) HeadPosture(ctx context.Context) (*string, error) {
	return &s.Instructor.HeadPosture, nil
}

func (s *SecondInstructorPostureResolver) CentroidFaceDistance(ctx context.Context) (*float64, error) {
	return s.Instructor.CentroidFaceDistance, nil
}

func (s *SecondInstructorPostureResolver) CentroidFaceDistanceAbsolute(ctx context.Context) (*float64, error) {
	return s.Instructor.CentroidFaceDistanceAbsolute, nil
}

type SecondStudentPostureResolver struct {
	Student models.SecondStudentPosture
}

func (s *SecondStudentPostureResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentPostureResolver) IsStanding(ctx context.Context) (*[]*bool, error) {
	vector := make([]*bool, len(s.Student.IsStanding))
	for i, k := range s.Student.IsStanding {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentPostureResolver) BodyPosture(ctx context.Context) (*[]string, error) {
	vector := make([]string, len(s.Student.BodyPosture))
	for i, k := range s.Student.BodyPosture {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentPostureResolver) HandPosture(ctx context.Context) (*[]string, error) {
	vector := make([]string, len(s.Student.HandPosture))
	for i, k := range s.Student.HandPosture {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SecondStudentPostureResolver) HeadPosture(ctx context.Context) (*[]string, error) {
	vector := make([]string, len(s.Student.HeadPosture))
	for i, k := range s.Student.HeadPosture {
		vector[i] = k
	}
	return &vector, nil
}

type BlockLevelResolver struct {
	BlockLevel models.BlockLevel
}

func (s *BlockLevelResolver) BlockInfo(ctx context.Context) (*BlockInfoResolver, error) {
	return &BlockInfoResolver{BlockInfo: s.BlockLevel.BlockInfo} , nil
}

func (s *BlockLevelResolver) Audio(ctx context.Context) (*BlockAudioAnalysisResolver, error) {
	return &BlockAudioAnalysisResolver{Audio: s.BlockLevel.Audio} , nil
}

func (s *BlockLevelResolver) Gaze(ctx context.Context) (*BlockGazeAnalysisResolver, error) {
	return &BlockGazeAnalysisResolver{Gaze: s.BlockLevel.Gaze} , nil
}

func (s *BlockLevelResolver) Location(ctx context.Context) (*BlockLocationAnalysisResolver, error) {
	return &BlockLocationAnalysisResolver{Location: s.BlockLevel.Location} , nil
}

func (s *BlockLevelResolver) Posture(ctx context.Context) (*BlockPostureAnalysisResolver, error) {
	return &BlockPostureAnalysisResolver{Posture: s.BlockLevel.Posture} , nil
}

func (s *BlockLevelResolver) CrossModal(ctx context.Context) (*string, error) {
	return &s.BlockLevel.CrossModal , nil
}

type BlockInfoResolver struct {
	BlockInfo models.BlockInfo
}

func (s *BlockInfoResolver) UnixStartSeconds(ctx context.Context) (int32, error) {
	return *s.BlockInfo.UnixStartSeconds, nil
}

func (s *BlockInfoResolver) BlockLength(ctx context.Context) (int32, error) {
	return *s.BlockInfo.BlockLength, nil
}

func (s *BlockInfoResolver) Id(ctx context.Context) (int32, error) {
	return *s.BlockInfo.Id, nil
}

type BlockAudioAnalysisResolver struct {
	Audio models.BlockAudioAnalysis
}

func (s *BlockAudioAnalysisResolver) SilenceFraction(ctx context.Context) (*float64, error) {
	return s.Audio.SilenceFraction, nil
}

func (s *BlockAudioAnalysisResolver) ObjectFraction(ctx context.Context) (*float64, error) {
	return s.Audio.ObjectFraction, nil
}

func (s *BlockAudioAnalysisResolver) TeacherOnlyFraction(ctx context.Context) (*float64, error) {
	return s.Audio.TeacherOnlyFraction, nil
}

func (s *BlockAudioAnalysisResolver) SingleSpeakerFraction(ctx context.Context) (*float64, error) {
	return s.Audio.SingleSpeakerFraction, nil
}

func (s *BlockAudioAnalysisResolver) TeacherActivityType(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Audio.TeacherActivityFraction))
	for i, k := range s.Audio.TeacherActivityType {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *BlockAudioAnalysisResolver) TeacherActivityFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Audio.TeacherActivityFraction))
	for i, k := range s.Audio.TeacherActivityFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockAudioAnalysisResolver) TeacherActivityTimes(ctx context.Context) (*[][][]*int32, error) {
	matrix := s.Audio.TeacherActivityTimes
	vector := make([][][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([][]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = make([]*int32, len(matrix[i][j]))
			for k := range matrix[i][j]{
				vector[i][j][k] = matrix[i][j][k]
			}
		}
	}
	return &vector, nil
}


type BlockGazeAnalysisResolver struct {
	Gaze models.BlockGazeAnalysis
}

func (s *BlockGazeAnalysisResolver) Instructor(ctx context.Context) (*BlockInstructorGazeResolver, error) {
	return &BlockInstructorGazeResolver{Instructor: s.Gaze.Instructor}, nil
}

func (s *BlockGazeAnalysisResolver) Student(ctx context.Context) (*BlockStudentGazeResolver, error) {
	return &BlockStudentGazeResolver{Student: s.Gaze.Student}, nil
}

type BlockInstructorGazeResolver struct {
	Instructor models.BlockInstructorGaze
}

func (s *BlockInstructorGazeResolver) GazeCategory(ctx context.Context) (*string, error) {
	return &s.Instructor.GazeCategory, nil
}

func (s *BlockInstructorGazeResolver) TotalCategoryFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.TotalCategoryFraction))
	for i, k := range s.Instructor.TotalCategoryFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockInstructorGazeResolver) LongestCategoryFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.LongestCategoryFraction))
	for i, k := range s.Instructor.LongestCategoryFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockInstructorGazeResolver) PrincipalGaze(ctx context.Context) (*PrincipalGazeResolver, error) {
	return &PrincipalGazeResolver{PrincipalGaze: s.Instructor.PrincipalGaze} , nil
}

func (s *BlockInstructorGazeResolver) RollMean(ctx context.Context) (*float64, error) {
	return s.Instructor.RollMean, nil
}

func (s *BlockInstructorGazeResolver) YawMean(ctx context.Context) (*float64, error) {
	return s.Instructor.YawMean, nil
}

func (s *BlockInstructorGazeResolver) PitchMean(ctx context.Context) (*float64, error) {
	return s.Instructor.PitchMean, nil
}

func (s *BlockInstructorGazeResolver) RollVariance(ctx context.Context) (*float64, error) {
	return s.Instructor.RollVariance, nil
}

func (s *BlockInstructorGazeResolver) YawVariance(ctx context.Context) (*float64, error) {
	return s.Instructor.YawVariance, nil
}

func (s *BlockInstructorGazeResolver) PitchVariance(ctx context.Context) (*float64, error) {
	return s.Instructor.PitchVariance, nil
}

type PrincipalGazeResolver struct {
	PrincipalGaze models.PrincipalGaze
}

func (s *PrincipalGazeResolver) Direction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.PrincipalGaze.Direction))
	for i, k := range s.PrincipalGaze.Direction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *PrincipalGazeResolver) DirectionVariation(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.PrincipalGaze.DirectionVariation))
	for i, k := range s.PrincipalGaze.DirectionVariation {
		vector[i] = k
	}
	return &vector, nil
}

func (s *PrincipalGazeResolver) LongestStayFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.PrincipalGaze.LongestStayFraction))
	for i, k := range s.PrincipalGaze.LongestStayFraction {
		vector[i] = k
	}
	return &vector, nil
}

type BlockStudentGazeResolver struct {
	Student models.BlockStudentGaze
}

func (s *BlockStudentGazeResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) NumOccurencesInBlock(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.NumOccurencesInBlock))
	for i, k := range s.Student.NumOccurencesInBlock {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) GazeCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.GazeCategory))
	for i, k := range s.Student.GazeCategory {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) TotalCategoryFraction(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.TotalCategoryFraction
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) LongestCategoryFraction(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.LongestCategoryFraction
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) DirectionMean(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.DirectionMean
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) DirectionVariation(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.DirectionVariation
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) TowardsInstructorFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.TowardsInstructorFraction))
	for i, k := range s.Student.TowardsInstructorFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) LookingDownFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.LookingDownFraction))
	for i, k := range s.Student.LookingDownFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) LookingFrontFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.LookingFrontFraction))
	for i, k := range s.Student.LookingFrontFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) RollMean(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.RollMean))
	for i, k := range s.Student.RollMean {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) YawMean(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.YawMean))
	for i, k := range s.Student.YawMean {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) PitchMean(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.PitchMean))
	for i, k := range s.Student.PitchMean {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) RollVariance(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.RollVariance))
	for i, k := range s.Student.RollVariance {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) YawVariance(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.YawVariance))
	for i, k := range s.Student.YawVariance {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentGazeResolver) PitchVariance(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.PitchVariance))
	for i, k := range s.Student.PitchVariance {
		vector[i] = k
	}
	return &vector, nil
}


type BlockLocationAnalysisResolver struct {
	Location models.BlockLocationAnalysis
}

func (s *BlockLocationAnalysisResolver) Instructor(ctx context.Context) (*BlockInstructorLocationResolver, error) {
	return &BlockInstructorLocationResolver{Instructor: s.Location.Instructor}, nil
}

func (s *BlockLocationAnalysisResolver) Student(ctx context.Context) (*BlockStudentLocationResolver, error) {
	return &BlockStudentLocationResolver{Student: s.Location.Student}, nil
}

type BlockInstructorLocationResolver struct {
	Instructor models.BlockInstructorLocation
}

func (s *BlockInstructorLocationResolver) TotalBoardFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.TotalBoardFraction, nil
}

func (s *BlockInstructorLocationResolver) LongestBoardFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.LongestBoardFraction, nil
}

func (s *BlockInstructorLocationResolver) TotalPodiumFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.TotalPodiumFraction, nil
}

func (s *BlockInstructorLocationResolver) LongestPodiumFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.LongestPodiumFraction, nil
}

func (s *BlockInstructorLocationResolver) TotalMovingFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.TotalMovingFraction, nil
}

func (s *BlockInstructorLocationResolver) LongestMovingFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.LongestMovingFraction, nil
}

func (s *BlockInstructorLocationResolver) LocationCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Instructor.LocationCategory))
	for i, k := range s.Instructor.LocationCategory {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockInstructorLocationResolver) CategoryFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.CategoryFraction))
	for i, k := range s.Instructor.CategoryFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockInstructorLocationResolver) LongestCategoryFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.LongestCategoryFraction))
	for i, k := range s.Instructor.LongestCategoryFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockInstructorLocationResolver) StayAtLocation(ctx context.Context) (*[][]*int32, error) {
	matrix := s.Instructor.StayAtLocation
	vector := make([][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockInstructorLocationResolver) StayAtLocationTimes(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Instructor.StayAtLocationTimes
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockInstructorLocationResolver) LongestStayFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.LongestStayFraction, nil
}

func (s *BlockInstructorLocationResolver) PrincipalMovement(ctx context.Context) (*PrincipalMovementResolver, error) {
	return &PrincipalMovementResolver{PrincipalMovement: s.Instructor.PrincipalMovement}, nil
}

type PrincipalMovementResolver struct {
	PrincipalMovement models.PrincipalMovement
}

func (s *PrincipalMovementResolver) DirectionMean(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.PrincipalMovement.DirectionMean))
	for i, k := range s.PrincipalMovement.DirectionMean {
		vector[i] = k
	}
	return &vector, nil
}

func (s *PrincipalMovementResolver) DirectionVariation(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.PrincipalMovement.DirectionVariation))
	for i, k := range s.PrincipalMovement.DirectionVariation {
		vector[i] = k
	}
	return &vector, nil
}

func (s *PrincipalMovementResolver) DirectionComps(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.PrincipalMovement.DirectionComps))
	for i, k := range s.PrincipalMovement.DirectionComps {
		vector[i] = k
	}
	return &vector, nil
}

type BlockStudentLocationResolver struct {
	Student models.BlockStudentLocation
}

func (s *BlockStudentLocationResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) NumOccurrencesInBlock(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.NumOccurrencesInBlock))
	for i, k := range s.Student.NumOccurrencesInBlock {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) IsSettled(ctx context.Context) (*[]*bool, error) {
	vector := make([]*bool, len(s.Student.IsSettled))
	for i, k := range s.Student.IsSettled {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) MeanBodyEntropy(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.MeanBodyEntropy))
	for i, k := range s.Student.MeanBodyEntropy {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) MaxBodyEntropy(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.MaxBodyEntropy))
	for i, k := range s.Student.MaxBodyEntropy {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) VarBodyEntropy(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.VarBodyEntropy))
	for i, k := range s.Student.VarBodyEntropy {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) MeanHeadEntropy(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.MeanHeadEntropy))
	for i, k := range s.Student.MeanHeadEntropy {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) MaxHeadEntropy(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.MaxHeadEntropy))
	for i, k := range s.Student.MaxHeadEntropy {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) VarHeadEntropy(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.VarHeadEntropy))
	for i, k := range s.Student.VarHeadEntropy {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) StayCoordinates(ctx context.Context) (*[][]*int32, error) {
	matrix := s.Student.StayCoordinates
	vector := make([][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) ClusterCount(ctx context.Context) (*int32, error) {
	return s.Student.ClusterCount, nil
}

func (s *BlockStudentLocationResolver) ClusterCenters(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.ClusterCenters
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) ClusterStudentIds(ctx context.Context) (*[][]*int32, error) {
	matrix := s.Student.ClusterStudentIds
	vector := make([][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentLocationResolver) SeatingArrangement(ctx context.Context) (*string, error) {
	return &s.Student.SeatingArrangement, nil
}


type BlockPostureAnalysisResolver struct {
	Posture models.BlockPostureAnalysis
}

func (s *BlockPostureAnalysisResolver) Instructor(ctx context.Context) (*BlockInstructorPostureResolver, error) {
	return &BlockInstructorPostureResolver{Instructor: s.Posture.Instructor}, nil
}

func (s *BlockPostureAnalysisResolver) Student(ctx context.Context) (*BlockStudentPostureResolver, error) {
	return &BlockStudentPostureResolver{Student: s.Posture.Student}, nil
}

type BlockInstructorPostureResolver struct {
	Instructor models.BlockInstructorPosture
}

func (s *BlockInstructorPostureResolver) StandingFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.StandingFraction, nil
}

func (s *BlockInstructorPostureResolver) HandPostureCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Instructor.HandPostureCategory))
	for i, k := range s.Instructor.HandPostureCategory {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *BlockInstructorPostureResolver) HandPostureCategoryFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.HandPostureCategoryFraction))
	for i, k := range s.Instructor.HandPostureCategoryFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockInstructorPostureResolver) HeadPostureCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Instructor.HeadPostureCategory))
	for i, k := range s.Instructor.HeadPostureCategory {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *BlockInstructorPostureResolver) HeadPostureCategoryFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.HeadPostureCategoryFraction))
	for i, k := range s.Instructor.HeadPostureCategoryFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockInstructorPostureResolver) MeanCentroidFaceDistance(ctx context.Context) (*float64, error) {
	return s.Instructor.MeanCentroidFaceDistance, nil
}

func (s *BlockInstructorPostureResolver) VarCentroidFaceDistance(ctx context.Context) (*float64, error) {
	return s.Instructor.VarCentroidFaceDistance, nil
}

type BlockStudentPostureResolver struct {
	Student models.BlockStudentPosture
}

func (s *BlockStudentPostureResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentPostureResolver) NumOccurrencesInBlock(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.NumOccurrencesInBlock))
	for i, k := range s.Student.NumOccurrencesInBlock {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentPostureResolver) IsStandingFraction(ctx context.Context) (*[]*bool, error) {
	vector := make([]*bool, len(s.Student.IsStandingFraction))
	for i, k := range s.Student.IsStandingFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *BlockStudentPostureResolver) BodyPostureCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.BodyPostureCategory))
	for i, k := range s.Student.BodyPostureCategory {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *BlockStudentPostureResolver) BodyPostureCategoryFraction(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.BodyPostureCategoryFraction
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentPostureResolver) HeadPostureCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.HeadPostureCategory))
	for i, k := range s.Student.HeadPostureCategory {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *BlockStudentPostureResolver) HeadPostureCategoryFraction(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.HeadPostureCategoryFraction
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *BlockStudentPostureResolver) HandPostureCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.HandPostureCategory))
	for i, k := range s.Student.HandPostureCategory {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *BlockStudentPostureResolver) HandPostureCategoryFraction(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.HandPostureCategoryFraction
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}



type SessionLevelResolver struct {
	SessionLevel models.SessionLevel
}

func (s *SessionLevelResolver) SessionInfo(ctx context.Context) (*SessionInfoResolver, error) {
	return &SessionInfoResolver{SessionInfo: s.SessionLevel.SessionInfo} , nil
}

func (s *SessionLevelResolver) Audio(ctx context.Context) (*SessionAudioAnalysisResolver, error) {
	return &SessionAudioAnalysisResolver{Audio: s.SessionLevel.Audio} , nil
}

func (s *SessionLevelResolver) Gaze(ctx context.Context) (*SessionGazeAnalysisResolver, error) {
	return &SessionGazeAnalysisResolver{Gaze: s.SessionLevel.Gaze} , nil
}

func (s *SessionLevelResolver) Location(ctx context.Context) (*SessionLocationAnalysisResolver, error) {
	return &SessionLocationAnalysisResolver{Location: s.SessionLevel.Location} , nil
}

func (s *SessionLevelResolver) Posture(ctx context.Context) (*SessionPostureAnalysisResolver, error) {
	return &SessionPostureAnalysisResolver{Posture: s.SessionLevel.Posture} , nil
}

func (s *SessionLevelResolver) CrossModal(ctx context.Context) (*string, error) {
	return &s.SessionLevel.CrossModal , nil
}

type SessionInfoResolver struct {
	SessionInfo models.SessionInfo
}

func (s *SessionInfoResolver) UnixStartSeconds(ctx context.Context) (int32, error) {
	return *s.SessionInfo.UnixStartSeconds, nil
}

func (s *SessionInfoResolver) SessionLength(ctx context.Context) (int32, error) {
	return *s.SessionInfo.SessionLength, nil
}

type SessionAudioAnalysisResolver struct {
	Audio models.SessionAudioAnalysis
}

func (s *SessionAudioAnalysisResolver) AudioBasedActivityType(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Audio.AudioBasedActivityType))
	for i, k := range s.Audio.AudioBasedActivityType {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *SessionAudioAnalysisResolver) AudioBasedActivityFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Audio.AudioBasedActivityFraction))
	for i, k := range s.Audio.AudioBasedActivityFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionAudioAnalysisResolver) AudioBasedActivityBlocks(ctx context.Context) (*[][][]*int32, error) {
	matrix := s.Audio.AudioBasedActivityBlocks
	vector := make([][][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([][]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = make([]*int32, len(matrix[i][j]))
			for k := range matrix[i][j]{
				vector[i][j][k] = matrix[i][j][k]
			}
		}
	}
	return &vector, nil
}

type SessionGazeAnalysisResolver struct {
	Gaze models.SessionGazeAnalysis
}

func (s *SessionGazeAnalysisResolver) Instructor(ctx context.Context) (*SessionInstructorGazeResolver, error) {
	return &SessionInstructorGazeResolver{Instructor: s.Gaze.Instructor}, nil
}

func (s *SessionGazeAnalysisResolver) Student(ctx context.Context) (*SessionStudentGazeResolver, error) {
	return &SessionStudentGazeResolver{Student: s.Gaze.Student}, nil
}

type SessionInstructorGazeResolver struct {
	Instructor models.SessionInstructorGaze
}

func (s *SessionInstructorGazeResolver) GazePreference(ctx context.Context) (*string, error) {
	return &s.Instructor.GazePreference , nil
}


func (s *SessionInstructorGazeResolver) TopLocations(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Instructor.TopLocations
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *SessionInstructorGazeResolver) TopLocationsGazeLeftFraction(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Instructor.TopLocationsGazeLeftFraction
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *SessionInstructorGazeResolver) ObjectCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Instructor.ObjectCategory))
	for i, k := range s.Instructor.ObjectCategory {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *SessionInstructorGazeResolver) LookingAtObjectFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.LookingAtObjectFraction))
	for i, k := range s.Instructor.LookingAtObjectFraction {
		vector[i] = k
	}
	return &vector, nil
}


type SessionStudentGazeResolver struct {
	Student models.SessionStudentGaze
}

func (s *SessionStudentGazeResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionStudentGazeResolver) GazeCategory(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.GazeCategory))
	for i, k := range s.Student.GazeCategory {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *SessionStudentGazeResolver) GazeCategoryFraction(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.GazeCategoryFraction
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}


type SessionLocationAnalysisResolver struct {
	Location models.SessionLocationAnalysis
}

func (s *SessionLocationAnalysisResolver) Instructor(ctx context.Context) (*SessionInstructorLocationResolver, error) {
	return &SessionInstructorLocationResolver{Instructor: s.Location.Instructor}, nil
}

func (s *SessionLocationAnalysisResolver) Student(ctx context.Context) (*SessionStudentLocationResolver, error) {
	return &SessionStudentLocationResolver{Student: s.Location.Student}, nil
}

type SessionInstructorLocationResolver struct {
	Instructor models.SessionInstructorLocation
}

func (s *SessionInstructorLocationResolver) LocationBasedActivityType(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Instructor.LocationBasedActivityType))
	for i, k := range s.Instructor.LocationBasedActivityType {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *SessionInstructorLocationResolver) LocationBasedActivityFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.LocationBasedActivityFraction))
	for i, k := range s.Instructor.LocationBasedActivityFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionInstructorLocationResolver) LocationBasedActivityBlocks(ctx context.Context) (*[][][]*int32, error) {
	matrix := s.Instructor.LocationBasedActivityBlocks
	vector := make([][][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([][]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = make([]*int32, len(matrix[i][j]))
			for k := range matrix[i][j]{
				vector[i][j][k] = matrix[i][j][k]
			}
		}
	}
	return &vector, nil
}

func (s *SessionInstructorLocationResolver) LocationClusterCount(ctx context.Context) (*int32, error) {
	return s.Instructor.LocationClusterCount, nil
}

func (s *SessionInstructorLocationResolver) LocationClusterCenter(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Instructor.LocationClusterCenter
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *SessionInstructorLocationResolver) LocationClusterSize(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Instructor.LocationClusterSize))
	for i, k := range s.Instructor.LocationClusterSize {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionInstructorLocationResolver) TotalBoardFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.TotalBoardFraction, nil
}

func (s *SessionInstructorLocationResolver) LongestBoardFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.LongestBoardFraction, nil
}

func (s *SessionInstructorLocationResolver) TotalPodiumFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.TotalPodiumFraction, nil
}

func (s *SessionInstructorLocationResolver) LongestPodiumFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.LongestPodiumFraction, nil
}

func (s *SessionInstructorLocationResolver) TotalMovingFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.TotalMovingFraction, nil
}

func (s *SessionInstructorLocationResolver) LongestMovingFraction(ctx context.Context) (*float64, error) {
	return s.Instructor.LongestMovingFraction, nil
}

func (s *SessionInstructorLocationResolver) LocationCategory(ctx context.Context) (*string, error) {
	return s.Instructor.LocationCategory, nil
}

func (s *SessionInstructorLocationResolver) CategoryFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.CategoryFraction))
	for i, k := range s.Instructor.CategoryFraction {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionInstructorLocationResolver) LongestCategoryFraction(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Instructor.LongestCategoryFraction))
	for i, k := range s.Instructor.LongestCategoryFraction {
		vector[i] = k
	}
	return &vector, nil
}


type SessionStudentLocationResolver struct {
	Student models.SessionStudentLocation
}

func (s *SessionStudentLocationResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionStudentLocationResolver) SettleDownTime(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.SettleDownTime))
	for i, k := range s.Student.SettleDownTime {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionStudentLocationResolver) EntryTime(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.EntryTime))
	for i, k := range s.Student.EntryTime {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionStudentLocationResolver) EntryLocation(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.EntryLocation
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *SessionStudentLocationResolver) ExitTime(ctx context.Context) (*[]*float64, error) {
	vector := make([]*float64, len(s.Student.ExitTime))
	for i, k := range s.Student.EntryTime {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionStudentLocationResolver) ExitLocation(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Student.ExitLocation
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *SessionStudentLocationResolver) SeatingCategories(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.SeatingCategories))
	for i, k := range s.Student.SeatingCategories {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *SessionStudentLocationResolver) SeatingCategoryBlocks(ctx context.Context) (*[][]*int32, error) {
	matrix := s.Student.SeatingCategoryBlocks
	vector := make([][]*int32, len(matrix))
	for i := range matrix {
		vector[i] = make([]*int32, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}


type SessionPostureAnalysisResolver struct {
	Posture models.SessionPostureAnalysis
}

func (s *SessionPostureAnalysisResolver) Instructor(ctx context.Context) (*SessionInstructorPostureResolver, error) {
	return &SessionInstructorPostureResolver{Instructor: s.Posture.Instructor}, nil
}

func (s *SessionPostureAnalysisResolver) Student(ctx context.Context) (*SessionStudentPostureResolver, error) {
	return &SessionStudentPostureResolver{Student: s.Posture.Student}, nil
}

type SessionInstructorPostureResolver struct {
	Instructor models.SessionInstructorPosture
}

func (s *SessionInstructorPostureResolver) BodyPosturePreference(ctx context.Context) (*string, error) {
	return &s.Instructor.BodyPosturePreference, nil
}

func (s *SessionInstructorPostureResolver) PointingClusterCount(ctx context.Context) (*int32, error) {
	return s.Instructor.PointingClusterCount, nil
}

func (s *SessionInstructorPostureResolver) PointingClusterCenter(ctx context.Context) (*[][]*float64, error) {
	matrix := s.Instructor.PointingClusterCenter
	vector := make([][]*float64, len(matrix))
	for i := range matrix {
		vector[i] = make([]*float64, len(matrix[i]))
		for j := range matrix[i]{
			vector[i][j] = matrix[i][j]
		}
	}
	return &vector, nil
}

func (s *SessionInstructorPostureResolver) PointingClusterSize(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Instructor.PointingClusterSize))
	for i, k := range s.Instructor.PointingClusterSize {
		vector[i] = k
	}
	return &vector, nil
}

type SessionStudentPostureResolver struct {
	Student models.SessionStudentPosture
}

func (s *SessionStudentPostureResolver) Id(ctx context.Context) (*[]*int32, error) {
	vector := make([]*int32, len(s.Student.Id))
	for i, k := range s.Student.Id {
		vector[i] = k
	}
	return &vector, nil
}

func (s *SessionStudentPostureResolver) HandPosturePreference(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.HandPosturePreference))
	for i, k := range s.Student.HandPosturePreference {
		vector[i] = &k
	}
	return &vector, nil
}

func (s *SessionStudentPostureResolver) HeadPosturePreference(ctx context.Context) (*[]*string, error) {
	vector := make([]*string, len(s.Student.HeadPosturePreference))
	for i, k := range s.Student.HeadPosturePreference {
		vector[i] = &k
	}
	return &vector, nil
}
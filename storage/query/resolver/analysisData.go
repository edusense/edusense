package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

type AnalysisDataResolver struct {
	AnalysisData models.AnalysisData
}

func (d *AnalysisDataResolver) Students(ctx context.Context) (*[]*PersonAnalysisResolver, error) {
	resolvers := make([]*PersonAnalysisResolver, len(d.AnalysisData.Students))
	for i, p := range d.AnalysisData.Students {
		resolvers[i] = &PersonAnalysisResolver{PersonAnalysis: p}
	}

	return &resolvers, nil
}

func (d *AnalysisDataResolver) Instructors(ctx context.Context) (*[]*PersonAnalysisResolver, error) {
	resolvers := make([]*PersonAnalysisResolver, len(d.AnalysisData.Instructors))
	for i, p := range d.AnalysisData.Instructors {
		resolvers[i] = &PersonAnalysisResolver{PersonAnalysis: p}
	}

	return &resolvers, nil
}
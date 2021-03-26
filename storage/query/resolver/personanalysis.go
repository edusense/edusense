package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

type PersonAnalysisResolver struct {
	PersonAnalysis models.PersonAnalysis
}

func (p *PersonAnalysisResolver) Posture(ctx context.Context) (*PostureAnalysisResolver, error) {
	return &PostureAnalysisResolver{PostureAnalysis: p.PersonAnalysis.Posture}, nil
}

func (p *PersonAnalysisResolver) Face(ctx context.Context) (*FaceAnalysisResolver, error) {
	return &FaceAnalysisResolver{FaceAnalysis: p.PersonAnalysis.Face}, nil
}
package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

type PostureAnalysisResolver struct {
	PostureAnalysis models.PostureAnalysis
}

func (p *PostureAnalysisResolver) Upright(ctx context.Context) (bool, error) {
	return bool(p.PostureAnalysis.Upright), nil
}

func (p *PostureAnalysisResolver) Attention(ctx context.Context) (float64, error) {
	return float64(p.PostureAnalysis.Attention), nil
}
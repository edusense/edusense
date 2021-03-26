package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

type FaceAnalysisResolver struct {
	FaceAnalysis models.FaceAnalysis
}

func (f *FaceAnalysisResolver) Emotion(ctx context.Context) (float64, error) {
	return float64(f.FaceAnalysis.Emotion), nil
}

func (f *FaceAnalysisResolver) Gaze(ctx context.Context) (float64, error) {
	return float64(f.FaceAnalysis.Gaze), nil
}

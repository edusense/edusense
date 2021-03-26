package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

// AnalysisFrameResolver resolves query-agnostic AnalysisFrame.
type AnalysisFrameResolver struct {
	Frame models.AnalysisFrame
}

// FrameNumber extracts FrameNumber field from given AnalysisFrame resolver.
func (f *AnalysisFrameResolver) FrameNumber(ctx context.Context) (int32, error) {
	return int32(f.Frame.FrameNumber), nil
}

// Timestamp extracts Timestamp field from given AnalysisFrame resolver.
func (f *AnalysisFrameResolver) Timestamp(ctx context.Context) (*TimeResolver, error) {
	return &TimeResolver{Time: f.Frame.Timestamp}, nil
}

// Channel extracts Channel field from given AnalysisFrame resolver.
func (f *AnalysisFrameResolver) Channel(ctx context.Context) (string, error) {
	return f.Frame.Channel, nil
}

func (f *AnalysisFrameResolver) AnalysisData(ctx context.Context) (*AnalysisDataResolver, error) {
	return &AnalysisDataResolver{AnalysisData: f.Frame.AnalysisData}, nil
}


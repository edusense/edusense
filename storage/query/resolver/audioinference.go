package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

// AudioInferenceResolver resolves query-agnostic AudioInference model.
type AudioInferenceResolver struct {
	Inference models.AudioInference
}

// Speech extracts Speech field from given AudioInference resolver.
func (ai *AudioInferenceResolver) Speech(ctx context.Context) (*SpeechResolver, error) {
	return &SpeechResolver{Speech: ai.Inference.Speech}, nil
}

// SpeechResolver resolves query-agnostic Speech model.
type SpeechResolver struct {
	Speech models.Speech
}

// Confidence extracts confidence score field from given Speech resolver.
func (s *SpeechResolver) Confidence(ctx context.Context) (float64, error) {
	return float64(s.Speech.Confidence), nil
}

// Speaker extracts speaker field from given Speech resolver.
func (s *SpeechResolver) Speaker(ctx context.Context) (string, error) {
	return s.Speech.Speaker, nil
}

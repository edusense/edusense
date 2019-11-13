// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

// AudioResolver resolves query-agnostic Audio model.
type AudioResolver struct {
	Audio models.Audio
}

// Amplitude extracts Amplitude field from given Audio resolver.
func (a *AudioResolver) Amplitude(ctx context.Context) (float64, error) {
	return float64(a.Audio.Amplitude), nil
}

// MelFrequency extracts MelFrequency field from given Audio resolver.
func (a *AudioResolver) MelFrequency(ctx context.Context) ([][]float64, error) {
	if len(a.Audio.MelFrequency) == 0 {
		return [][]float64{}, nil
	}

	freqs := make([][]float64, len(a.Audio.MelFrequency))
	for i, m := range a.Audio.MelFrequency {
		arr := make([]float64, len(m))
		for j, k := range m {
			arr[j] = float64(k)
		}
		freqs[i] = arr
	}

	return freqs, nil
}

// Inference extracts inference object field from given Audio resolver.
func (a *AudioResolver) Inference(ctx context.Context) (*AudioInferenceResolver, error) {
	return &AudioInferenceResolver{Inference: a.Audio.Inference}, nil
}

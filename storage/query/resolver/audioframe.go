// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

// AudioFrameResolver resolves query-agnostic AudioFrame.
type AudioFrameResolver struct {
	Frame models.AudioFrame
}

// FrameNumber extracts FrameNumber field from given AudioFrame resolver.
func (f *AudioFrameResolver) FrameNumber(ctx context.Context) (int32, error) {
	return int32(f.Frame.FrameNumber), nil
}

// Timestamp extracts Timestamp field from given AudioFrame resolver.
func (f *AudioFrameResolver) Timestamp(ctx context.Context) (*TimeResolver, error) {
	return &TimeResolver{Time: f.Frame.Timestamp}, nil
}

// Audio extracts Audio field from given AudioFrame resolver.
func (f *AudioFrameResolver) Audio(ctx context.Context) (*AudioResolver, error) {
	return &AudioResolver{Audio: f.Frame.Audio}, nil
}

// Channel extracts Channel field from given AudioFrame resolver.
func (f *AudioFrameResolver) Channel(ctx context.Context) (string, error) {
	return f.Frame.Channel, nil
}

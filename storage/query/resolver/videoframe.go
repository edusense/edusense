// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

// VideoFrameResolver resolves query-agnostic VideoFrame model.
type VideoFrameResolver struct {
	Frame models.VideoFrame
}

// FrameNumber extracts frame number from given VideoFrame resolver.
func (f *VideoFrameResolver) FrameNumber() (int32, error) {
	return int32(f.Frame.FrameNumber), nil
}

// Timestamp extracts timestamp from given VideoFrame resolver.
func (f *VideoFrameResolver) Timestamp() (*TimeResolver, error) {
	return &TimeResolver{Time: f.Frame.Timestamp}, nil
}

// Thumbnail extracts thumbnail from given VideoFrame resolver.
func (f *VideoFrameResolver) Thumbnail(ctx context.Context) (*ThumbnailResolver, error) {
	return &ThumbnailResolver{Thumbnail: f.Frame.Thumbnail}, nil
}

// People extracts list of Person resolvers from given VideoFrame resolver.
func (f *VideoFrameResolver) People(ctx context.Context) (*[]*PersonResolver, error) {
	resolvers := make([]*PersonResolver, len(f.Frame.People))
	for i, p := range f.Frame.People {
		resolvers[i] = &PersonResolver{Person: p}
	}

	return &resolvers, nil
}

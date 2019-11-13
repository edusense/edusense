// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

// PersonResolver resolves query-agnostic Person model.
type PersonResolver struct {
	Person models.Person
}

// Body extracts body keypoint array from given Person resolver.
func (p *PersonResolver) Body(ctx context.Context) (*[]int32, error) {
	if len(p.Person.Body) == 0 {
		return nil, nil
	}

	body := make([]int32, len(p.Person.Body))
	for i, k := range p.Person.Body {
		body[i] = int32(k)
	}
	return &body, nil
}

// Face extracts face keypoint array from given Person resolver.
func (p *PersonResolver) Face(ctx context.Context) (*[]int32, error) {
	if len(p.Person.Face) == 0 {
		return nil, nil
	}

	face := make([]int32, len(p.Person.Face))
	for i, k := range p.Person.Face {
		face[i] = int32(k)
	}
	return &face, nil
}

// Hand extracts hand keypoint array from given Person resolver.
func (p *PersonResolver) Hand(ctx context.Context) (*[]int32, error) {
	if len(p.Person.Hand) == 0 {
		return nil, nil
	}

	hand := make([]int32, len(p.Person.Hand))
	for i, k := range p.Person.Hand {
		hand[i] = int32(k)
	}
	return &hand, nil
}

// OpenposeID extracts source openpose ID from given Person resolver.
func (p *PersonResolver) OpenposeID(ctx context.Context) (*int32, error) {
	id := int32(p.Person.OpenposeID)
	if id < 0 {
		return nil, nil
	}
	return &id, nil
}

// Inference extracts inference object from given Person resolver.
func (p *PersonResolver) Inference(ctx context.Context) (*PersonInferenceResolver, error) {
	return &PersonInferenceResolver{Inference: p.Person.Inference}, nil
}

// Copyright (c) 2017-2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

type BackfillMetaDataArgs struct {
	CourseNumber *string
}

func (q QueryResolver) BackfillMetaData (ctx context.Context, args BackfillMetaDataArgs) ([]*BackfillMetaDataResolver, error) {
	if args.CourseNumber != nil{
		selected_metadata, err := q.Driver.GetBackfillMetaDataFilter(*args.CourseNumber)

		if err != nil {
			return []*BackfillMetaDataResolver{}, err
		}

		resolvers := make([]*BackfillMetaDataResolver, len(selected_metadata))

		for i, f := range selected_metadata {
			resolvers[i] = &BackfillMetaDataResolver{BackfillMetaData : f}
		}
		return resolvers, nil
	}
	
	
	all_metadata, err := q.Driver.GetBackfillMetaData()
	if err != nil {
		return []*BackfillMetaDataResolver{}, err
	}
	resolvers := make([]*BackfillMetaDataResolver, len(all_metadata))

	for i, f := range all_metadata {
		resolvers[i] = &BackfillMetaDataResolver{BackfillMetaData : f}
	}

	return resolvers, nil
}

type BackfillMetaDataResolver struct {
	BackfillMetaData models.BackfillMetaData
}

func (b *BackfillMetaDataResolver) CourseNumber(ctx context.Context) (string, error) {
	return b.BackfillMetaData.CourseNumber, nil
}

func (b *BackfillMetaDataResolver) Sessions(ctx context.Context) ([]*BackfillSessionResolver, error) {
	vector := make([]*BackfillSessionResolver, len(b.BackfillMetaData.Sessions))
	for i, k := range b.BackfillMetaData.Sessions {
		vector[i] = &BackfillSessionResolver{BackfillSession: k}
	}
	return vector, nil
}


type BackfillSessionResolver struct {
	BackfillSession models.BackfillSession
}

func (b *BackfillSessionResolver) Id(ctx context.Context) (*string, error) {
	return b.BackfillSession.Id, nil
}

func (b *BackfillSessionResolver) Keyword(ctx context.Context) (*string, error) {
	return b.BackfillSession.Keyword, nil
}

func (b *BackfillSessionResolver) Name(ctx context.Context) (*string, error) {
	return b.BackfillSession.Name, nil
}

func (b *BackfillSessionResolver) DebugInfo(ctx context.Context) (*string, error) {
	return b.BackfillSession.DebugInfo, nil
}

func (b *BackfillSessionResolver) CommitId(ctx context.Context) (*string, error) {
	return b.BackfillSession.CommitId, nil
}

func (b *BackfillSessionResolver) AnalyticsCommitId(ctx context.Context) (*string, error) {
	return b.BackfillSession.AnalyticsCommitId, nil
}

func (b *BackfillSessionResolver) StartTime() (*TimeResolver, error) {
	return &TimeResolver{Time: b.BackfillSession.StartTime}, nil
}

func (b *BackfillSessionResolver) Runtime(ctx context.Context) (*float64, error) {
	return b.BackfillSession.Runtime, nil
}

func (b *BackfillSessionResolver) Status(ctx context.Context) (*string, error) {
	return b.BackfillSession.Status, nil
}

func (b *BackfillSessionResolver) PipelineVersion(ctx context.Context) (*string, error) {
	return b.BackfillSession.PipelineVersion, nil
}

func (b *BackfillSessionResolver) AnalysisStartTime(ctx context.Context) (*TimeResolver, error) {
	return &TimeResolver{Time: b.BackfillSession.AnalysisStartTime}, nil
}

func (b *BackfillSessionResolver) AnalysisRuntime(ctx context.Context) (*float64, error) {
	return b.BackfillSession.AnalysisRuntime, nil
}

func (b *BackfillSessionResolver) AnalysisComplete(ctx context.Context) (*bool, error) {
	return b.BackfillSession.AnalysisComplete, nil
}
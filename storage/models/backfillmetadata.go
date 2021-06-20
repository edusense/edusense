// Copyright (c) 2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package models

import (
	"time"
)

type BackfillMetaData struct {
	CourseNumber string `json:"courseNumber" bson:"courseNumber"`
	Sessions []BackfillSession `json:"backfillSession" bson:"backfillSession"`
}

type BackfillSession struct {
	Id *string `json:"id,omitempty" bson:"id"`
	Keyword *string `json:"keyword,omitempty" bson:"keyword"`
	Name *string `json:"name,omitempty" bson:"name"`
	DebugInfo *string `json:"debugInfo,omitempty" bson:"debugInfo"`
	CommitId *string `json:"commitId,omitempty" bson:"commitId"`
	AnalyticsCommitId *string `json:"analyticsCommitId,omitempty" bson:"analyticsCommitId"`
	StartTime time.Time `json:"startTime,omitempty" bson:"startTime"`
	Runtime *float64 `json:"runtime,omitempty" bson:"runtime"`
	Status *string `json:"status,omitempty" bson:"status"`
	PipelineVersion *string `json:"pipelineVersion,omitempty" bson:"pipelineVersion"`
	AnalysisStartTime time.Time `json:"analysisStartTime,omitempty" bson:"analysisStartTime"`
	AnalysisRuntime *float64 `json:"analysisRuntime,omitempty" bson:"analysisRuntime"`
	AnalysisComplete *bool `json:"analysisComplete,omitempty" bson:"analysisComplete"`
}
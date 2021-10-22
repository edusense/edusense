// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package dbhandler

import (
	models "go.edusense.io/storage/models"
)

// DatabaseDriver interfaces database operations (CRUD). This interface
// provides rough an abstraction on top of underlying database systems.
type DatabaseDriver interface {
	// InsertSession inserts a new frame. It returns error if identical session
	/// exists
	InsertSession(developer, version, keyword, overwrite string, metadata interface{}) (*models.Session, error)
	// UpdateSession updates frame with given session ID. It returns error if
	// there is no session
	UpdateSession(sessID string, metadata interface{}) (*models.Session, error)
	// Getsession retrieves a session data by given session ID.
	GetSession(sessID string) (*models.Session, error)
	// FindSession returns list of sessions by a session filter.
	FindSession(filter *models.SessionFilter) ([]models.Session, error)

	// InsertFrame inserts a free-form frame. These frams cannot be retrieved by
	// GraphQL.
	InsertFrame(sessID, schema, channel string, frame interface{}) error
	// InsertQueriableVideoFrame inserts a GraphQL-queriable video frame.
	InsertQueriableVideoFrame(sessID, schema, channel string, frame models.VideoFrame) error
	// InsertQueriableAudioFrame inserts a GraphQL-queriable audio frame.
	InsertQueriableAudioFrame(sessID, schema, channel string, frame models.AudioFrame) error

	//Inserting db handler functions for classroom collection
	InsertClassroomCollection (classroom models.Classroom) error
	GetClassroom(filter *models.SessionFilter) ([]models.Classroom, error)

	//Inserting db handler functions for classroom collection
	InsertCourseCollection (course models.Course) error
	GetCourse(filter *models.SessionFilter) ([]models.Course, error)

	// Analytics db handler functions
	InsertAnalytics(analytics models.Analytics) error
	GetAnalyticsFilter(sessIDPtr *string, keywordPtr *string) ([]models.Analytics, error)

	// Backfill Metadata db handler functions
	InsertBackfillMetaData(metaData models.BackfillMetaData) error
	GetBackfillMetaDataFilter(courseNumber string) ([]models.BackfillMetaData, error)

	// Get frames by filter
	// GetFrameByFilter returns list of frames by given frame filters.
	GetFrameByFilter(sessID, schema, channel string, numberFilters []models.FrameNumberFilter, timestampFilters []models.TimestampFilter) ([]interface{}, error)
	// GetQueriableVideoFrameByFilter returns list of graphQL-queriable video
	// frames by given frame filters.
	GetQueriableVideoFrameByFilter(sessID, schema, channel string, numberFilters []models.FrameNumberFilter, timestampFilters []models.TimestampFilter) ([]models.VideoFrame, error)
	// GetQueriableAudioFrameByFilter returns list of graphQL-queriable audio
	// frames by given frame filters.
	GetQueriableAudioFrameByFilter(sessID, schema, channel string, numberFilters []models.FrameNumberFilter, timestampFilters []models.TimestampFilter) ([]models.AudioFrame, error)

	// GetFrameByFrameNumber returns a free-form frame by given frame number.
	GetFrameByFrameNumber(sessID, schema, channel string, frameNumber uint32) ([]interface{}, error)
	// GetQueriableVideoFrameByFrameNumber returns a graphQL-queriable video
	// frame by given frame number.
	GetQueriableVideoFrameByFrameNumber(sessID, schema, channel string, frameNumber uint32) ([]models.VideoFrame, error)
	// GetQueriableAudioFrameByFrameNumber returns a graphQL-queriable audio
	// frame by given frame number.
	GetQueriableAudioFrameByFrameNumber(sessID, schema, channel string, frameNumber uint32) ([]models.AudioFrame, error)

	// GetMostRecentFrame returns a list of the most recent free-form frames.
	GetMostRecentFrame(sessID, schema, channel string) ([]interface{}, error)
	// GetMostRecentQueriableVideoFrame returns a list of the most recent
	// graphQL-queriable video frames.
	GetMostRecentQueriableVideoFrame(sessID, schema, channel string) ([]models.VideoFrame, error)
	// GetMostRecentQueriableAudioFrame returns a list of the most recent
	// graphQL-queriable audio frames.
	GetMostRecentQueriableAudioFrame(sessID, schema, channel string) ([]models.AudioFrame, error)
}

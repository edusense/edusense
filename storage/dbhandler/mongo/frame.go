// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package mongo

import (
	"errors"

	bson "github.com/globalsign/mgo/bson"

	models "go.edusense.io/storage/models"
)

// InsertFrame inserts a free-form frame.
func (m *Driver) InsertFrame(sessID, schema, channel string, frame interface{}) error {
	// setup DB-specific frame struct
	// identically defined, insert frame

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return errors.New("invalid session id")
	}

	// type-cast to object id from string
	mID := bson.ObjectIdHex(sessID)

	// get collection name for frames
	frameCol := formatSessionCollection(mID, schema)

	// insert frame
	err := m.DB.C(frameCol).Insert(&frame)
	if err != nil {
		return err
	}

	return nil
}

// InsertQueriableVideoFrame inserts a graphQL-queriable video frame.
func (m *Driver) InsertQueriableVideoFrame(sessID, schema, channel string, frame models.VideoFrame) error {
	// setup DB-specific frame struct
	// identically defined, insert frame

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return errors.New("invalid session id")
	}

	// type-cast to object id from string
	mID := bson.ObjectIdHex(sessID)

	// get collection name for frames
	frameCol := formatSessionCollection(mID, schema)

	// insert frame
	err := m.DB.C(frameCol).Insert(&frame)
	if err != nil {
		return err
	}

	return nil
}

// InsertQueriableAudioFrame inserts a graphQL-queriable audio frame.
func (m *Driver) InsertQueriableAudioFrame(sessID, schema, channel string, frame models.AudioFrame) error {
	// setup DB-specific frame struct
	// identically defined, insert frame

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return errors.New("invalid session id")
	}

	// type-cast to object id from string
	mID := bson.ObjectIdHex(sessID)

	// get collection name for frames
	frameCol := formatSessionCollection(mID, schema)

	// insert frame
	err := m.DB.C(frameCol).Insert(&frame)
	if err != nil {
		return err
	}

	return nil
}

// InsertQueriableSAnalysisFrame inserts a graphQL-queriable video frame.
func (m *Driver) InsertQueriableAnalysisFrame(sessID, schema, channel string, frame models.AnalysisFrame) error {
	// setup DB-specific frame struct
	// identically defined, insert frame

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return errors.New("invalid session id")
	}

	// type-cast to object id from string
	mID := bson.ObjectIdHex(sessID)

	// get collection name for frames
	frameCol := formatSessionCollection(mID, schema)

	// insert frame
	err := m.DB.C(frameCol).Insert(&frame)
	if err != nil {
		return err
	}

	return nil
}

// GetFrameByFilter returns list of free-form frames by given frame filter.
// TODO(DohyunKimOfficial): This function has been discarded when moving to
// GraphQL. This should be properly implemented again in future.
func (m *Driver) GetFrameByFilter(sessID, schema, channel string, numberFilters []models.FrameNumberFilter, timstampFilters []models.TimestampFilter) ([]interface{}, error) {
	return nil, errors.New("NotImplemented")
}

// GetQueriableVideoFrameByFilter returns list of graphQL-queriable video
// frames by given frame filters.
func (m *Driver) GetQueriableVideoFrameByFilter(sessID, schema, channel string, numberFilters []models.FrameNumberFilter, timestampFilters []models.TimestampFilter) ([]models.VideoFrame, error) {
	// DB-specific constructs
	var mFrames []models.VideoFrame
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	bsonQueries := []bson.M{}
	for _, f := range numberFilters {
		bsonOp, err := opToBsonOp(f.Operator)
		if err != nil {
			return []models.VideoFrame{}, err
		}

		bsonQueries = append(bsonQueries, bson.M{"frameNumber": bson.M{bsonOp: f.FrameNumber}})
	}

	for _, f := range timestampFilters {
		bsonOp, err := opToBsonOp(f.Operator)
		if err != nil {
			return []models.VideoFrame{}, err
		}

		bsonQueries = append(bsonQueries, bson.M{"timestamp": bson.M{bsonOp: f.Timestamp}})
	}

	bsonQueries = append(bsonQueries, bson.M{"channel": channel})

	err = m.DB.C(frameCol).Find(
		bson.M{"$and": bsonQueries}).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct
	return mFrames, nil
}

// GetQueriableAudioFrameByFilter returns list of graphQL-queriable audio
// frames by given frame filters.
func (m *Driver) GetQueriableAudioFrameByFilter(sessID, schema, channel string, numberFilters []models.FrameNumberFilter, timestampFilters []models.TimestampFilter) ([]models.AudioFrame, error) {
	// DB-specific constructs
	var mFrames []models.AudioFrame
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	bsonQueries := []bson.M{}
	for _, f := range numberFilters {
		bsonOp, err := opToBsonOp(f.Operator)
		if err != nil {
			return []models.AudioFrame{}, err
		}

		bsonQueries = append(bsonQueries, bson.M{"frameNumber": bson.M{bsonOp: f.FrameNumber}})
	}

	for _, f := range timestampFilters {
		bsonOp, err := opToBsonOp(f.Operator)
		if err != nil {
			return []models.AudioFrame{}, err
		}

		bsonQueries = append(bsonQueries, bson.M{"frameNumber": bson.M{bsonOp: f.Timestamp}})
	}

	bsonQueries = append(bsonQueries, bson.M{"channel": channel})

	err = m.DB.C(frameCol).Find(
		bson.M{"$and": bsonQueries}).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct
	return mFrames, nil
}

// GetFrameByFrameNumber returns list of free-form frames by frame number.
func (m *Driver) GetFrameByFrameNumber(sessID, schema, channel string, frameNumber uint32) ([]interface{}, error) {
	// DB-specific constructs
	var mFrames []interface{}
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	err = m.DB.C(frameCol).Find(
		bson.M{"$and": []bson.M{
			bson.M{"frameNumber": frameNumber},
			bson.M{"channel": channel}}}).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct

	return mFrames, nil
}

// GetQueriableVideoFrameByFrameNumber returns list of graphQL-queriable video
// framss by given frame number.
func (m *Driver) GetQueriableVideoFrameByFrameNumber(sessID, schema, channel string, frameNumber uint32) ([]models.VideoFrame, error) {
	// DB-specific constructs
	var mFrames []models.VideoFrame
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	err = m.DB.C(frameCol).Find(
		bson.M{"$and": []bson.M{
			bson.M{"frameNumber": frameNumber},
			bson.M{"channel": channel}}}).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct

	return mFrames, nil
}

// GetQueriableAudioFrameByFrameNumber returns list of graphQL-queriable audio
// frames by given fraem number.
func (m *Driver) GetQueriableAudioFrameByFrameNumber(sessID, schema, channel string, frameNumber uint32) ([]models.AudioFrame, error) {
	// DB-specific constructs
	var mFrames []models.AudioFrame
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	err = m.DB.C(frameCol).Find(
		bson.M{"$and": []bson.M{
			bson.M{"frameNumber": frameNumber},
			bson.M{"channel": channel}}}).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct

	return mFrames, nil
}

// GetQueriableAnalysisFrameByFrameNumber returns list of graphQL-queriable analysis
// framss by given frame number.
func (m *Driver) GetQueriableAnalysisFrameByFrameNumber(sessID, schema, channel string, frameNumber uint32) ([]models.AnalysisFrame, error) {
	// DB-specific constructs
	var mFrames []models.AnalysisFrame
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	err = m.DB.C(frameCol).Find(
		bson.M{"$and": []bson.M{
			bson.M{"frameNumber": frameNumber},
			bson.M{"channel": channel}}}).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct

	return mFrames, nil
}

// GetMostRecentFrame returns a list of the most recent free-frorm frames.
func (m *Driver) GetMostRecentFrame(sessID, schema, channel string) ([]interface{}, error) {
	// DB-specific constructs
	var mFrames []interface{}
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	err = m.DB.C(frameCol).Find(bson.M{"channel": channel}).Sort("-frameNumber").Limit(1).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct

	return mFrames, nil
}

// GetMostRecentQueriableVideoFrame returns a list of the most recent
// graphQL-queriable video frames.
func (m *Driver) GetMostRecentQueriableVideoFrame(sessID, schema, channel string) ([]models.VideoFrame, error) {
	// DB-specific constructs
	var mFrames []models.VideoFrame
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	err = m.DB.C(frameCol).Find(bson.M{"channel": channel}).Sort("-frameNumber").Limit(1).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct

	return mFrames, nil
}

// GetMostRecentQueriableAudioFrame returns a list of the most recent
// graphQL-queriable audio frames.
func (m *Driver) GetMostRecentQueriableAudioFrame(sessID, schema, channel string) ([]models.AudioFrame, error) {
	// DB-specific constructs
	var mFrames []models.AudioFrame
	var err error

	// check whether valid session ID, does not check whether the session is
	// already registered in sessions collection
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// type-cast to objectid from string
	mID := bson.ObjectIdHex(sessID)

	// get collection that contains the sessions
	frameCol := formatSessionCollection(mID, schema)
	err = m.DB.C(frameCol).Find(bson.M{"channel": channel}).Sort("-frameNumber").Limit(1).All(&mFrames)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral construct

	return mFrames, nil
}

func opToBsonOp(op string) (string, error) {
	switch op {
	case "gte":
		return "$gte", nil
	case "gt":
		return "$gt", nil
	case "eq":
		return "$eq", nil
	case "lt":
		return "$lt", nil
	case "lte":
		return "$lte", nil
	default:
		return "", errors.New("unknown filter operator")
	}
}

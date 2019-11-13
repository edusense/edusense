// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package mongo

import (
	"errors"
	"fmt"

	bson "github.com/globalsign/mgo/bson"

	models "go.edusense.io/storage/models"
)

const sessCol string = "sessions"

// InsertSession inserts a new session.
func (m *Driver) InsertSession(keyword string, metadata interface{}) (*models.Session, error) {
	// construct mongo specific constructs
	mID := bson.NewObjectId()
	mSess := &Session{
		ID:       mID,
		Keyword:  keyword,
		Metadata: metadata,
	}

	// insert
	err := m.DB.C("sessions").Insert(mSess)
	if err != nil {
		return nil, err
	}

	// transform into DB-neutral representation
	sess := &models.Session{
		ID:        mID.Hex(),
		Timestamp: mID.Time(),
		Keyword:   keyword,
		Schemas:   []string{},
		Metadata:  metadata,
	}

	return sess, nil
}

// UpdateSession updates frame with given session ID.
func (m *Driver) UpdateSession(sessID string, metadata interface{}) (*models.Session, error) {
	return nil, errors.New("not implemented")
}

// GetSession retrives a session data by given session filter.
func (m *Driver) GetSession(sessID string) (*models.Session, error) {
	// DB-specific session struct
	var mSess Session

	// check whether valid session ID
	if !bson.IsObjectIdHex(sessID) {
		return nil, errors.New("invalid session id")
	}

	// lookup the database
	err := m.DB.C(sessCol).Find(bson.M{"_id": bson.ObjectIdHex(sessID)}).One(&mSess)
	if err != nil {
		return nil, err
	}

	sess := &models.Session{
		ID:        mSess.ID.Hex(),
		Keyword:   mSess.Keyword,
		Timestamp: mSess.ID.Time(),
		Schemas:   mSess.Schemas,
		Metadata:  mSess.Metadata,
	}

	return sess, nil
}

// FindSession retrieves list of sessions by given session filter.
func (m *Driver) FindSession(filter *models.SessionFilter) ([]models.Session, error) {
	// DB-specific session struct
	var mSesses []Session

	expression := `^` + filter.Keyword

	objectIDStart := bson.NewObjectIdWithTime(filter.TimestampStart)
	objectIDEnd := bson.NewObjectIdWithTime(filter.TimestampEnd)

	// check whether valid session
	err := m.DB.C("sessions").Find(
		bson.M{"$and": []bson.M{
			bson.M{"keyword": bson.M{"$regex": bson.RegEx{Pattern: expression, Options: ""}}},
			bson.M{"_id": bson.M{"$gte": objectIDStart}},
			bson.M{"_id": bson.M{"$lte": objectIDEnd}}}}).All(&mSesses)

	if err != nil {
		return nil, err
	}

	// transform into DB-neural struct
	sesses := make([]models.Session, len(mSesses))
	for i, s := range mSesses {
		sesses[i] = models.Session{
			ID:        s.ID.Hex(),
			Keyword:   s.Keyword,
			Timestamp: s.ID.Time(),
			Schemas:   s.Schemas,
			Metadata:  s.Metadata,
		}
	}

	return sesses, nil
}

func formatSessionCollection(sessionID bson.ObjectId, schema string) string {
	return fmt.Sprintf("session-%s-%s", sessionID.Hex(), schema)
}

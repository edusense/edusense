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
func (m *Driver) InsertSession(developer, version, keyword, overwrite string, metadata interface{}) (*models.Session, error) {
	if overwrite == "True" {
		//If overwrite == True, deletes the last session with the same keyword

		//get earlier sessions with same keyword
		var prevSess []Session
		err := m.DB.C(sessCol).Find(bson.M{"keyword": keyword}).All(&prevSess)
		if err != nil {
			return nil, err
		}

		if (len(prevSess) > 0) {
			s := prevSess[len(prevSess)-1]

			//delete document from sessions
			err_doc := m.DB.C(sessCol).Remove(bson.M{"_id": s.ID})
			if err_doc != nil {
				return nil, err_doc
			}

			//delete previous audio collection with same keyword
			audioCol := "session-" + s.ID.Hex() + "-classinsight-graphql-audio"
			err_aud := m.DB.C(audioCol).DropCollection()
			if err_aud != nil {
				return nil, err_aud
			}

			//delete previous video collection with same keyword
			videoCol := "session-" + s.ID.Hex() + "-classinsight-graphql-video"
			err_vid := m.DB.C(videoCol).DropCollection()
			if err_vid != nil {
				return nil, err_vid
			}
		}
	}

	// construct mongo specific constructs
	mID := bson.NewObjectId()
	mSess := &Session{
		ID:        mID,
		Timestamp: mID.Time(),
		Keyword:   keyword,
		Version:   version,
		Developer: developer,
		Metadata:  metadata,
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
		Version:   version,
		Developer: developer,
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
		Version:   mSess.Version,
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
			Version:   s.Version,
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

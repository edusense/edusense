// Copyright (c) 2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package mongo

import (
	"errors"
	"fmt"
	bson "github.com/globalsign/mgo/bson"
	models "go.edusense.io/storage/models"
)


func (m *Driver) InsertAnalytics(analytics models.Analytics) error {
	// insert
	if analytics.Id == "" {
		return errors.New("Must include id in schema, look at Analytics Model")
	}
	collectionName := fmt.Sprintf("analytics-session-%s", analytics.Id)
	err := m.DB.C(collectionName).Insert(&analytics)
	if err != nil {
		return err
	}

	return nil
}

func (m *Driver) GetAnalyticsFilter(sessIDPtr *string, keywordPtr *string) ([]models.Analytics, error) {
    var mAnalytics []models.Analytics
	
	// Prioritze sessionID if available. Only use keyword if no sessionID available.
	err := errors.New("sessionID and keyword are nil")

	if sessIDPtr != nil {
		sessID := *sessIDPtr
		collectionName := fmt.Sprintf("analytics-session-%s", sessID)
		err = m.DB.C(collectionName).Find(
			bson.M{"$and": []bson.M{
				bson.M{"id": sessID}}}).All(&mAnalytics)
	} else if keywordPtr != nil {
		// Try to find keyword in general collection if no sessionId specified.
		keyword := *keywordPtr
		err = m.DB.C("analytics").Find(
			bson.M{"$and": []bson.M{
				bson.M{"keyword": keyword}}}).All(&mAnalytics)
	}
	
	if err != nil {
		return nil, err
	}

	return mAnalytics, nil
}
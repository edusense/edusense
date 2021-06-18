// Copyright (c) 2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package mongo

import (
	"errors"
	bson "github.com/globalsign/mgo/bson"
	models "go.edusense.io/storage/models"
)


func (m *Driver) InsertAnalytics(analytics models.Analytics) error {
	// insert
	err := m.DB.C("analytics").Insert(&analytics)
	if err != nil {
		return err
	}

	return nil
}

func (m *Driver) GetAnalytics() ([]models.Analytics, error) {
    var mAnalytics []models.Analytics

	err := m.DB.C("analytics").Find(bson.M{}).All(&mAnalytics)

	if err != nil {
		return nil, err
	}

	return mAnalytics, nil
}

func (m *Driver) GetAnalyticsFilter(sessIDPtr *string, keywordPtr *string) ([]models.Analytics, error) {
    var mAnalytics []models.Analytics
	
	// Prioritze sessionID if available. Only use keyword if no sessionID available.
	err := errors.New("sessionID and keyword are nil")
	if sessIDPtr != nil {
		sessID := *sessIDPtr
		err = m.DB.C("analytics").Find(
			bson.M{"$and": []bson.M{
				bson.M{"id": sessID}}}).All(&mAnalytics)
	} else if keywordPtr != nil {
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
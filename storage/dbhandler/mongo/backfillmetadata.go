// Copyright (c) 2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package mongo

import (
	bson "github.com/globalsign/mgo/bson"
	models "go.edusense.io/storage/models"
)

func (m *Driver) InsertBackfillMetaData(metaData models.BackfillMetaData) error {
	// insert
	err := m.DB.C("backfillMetaData").Insert(&metaData)
	if err != nil {
		return err
	}

	return nil
}

func (m *Driver) GetBackfillMetaData() ([]models.BackfillMetaData, error) {
    var metaData []models.BackfillMetaData

	err := m.DB.C("backfillMetaData").Find(bson.M{}).All(&metaData)

	if err != nil {
		return nil, err
	}

	return metaData, nil
}

func (m *Driver) GetBackfillMetaDataFilter(courseNumber string) ([]models.BackfillMetaData, error) {
    var metaData []models.BackfillMetaData

	err := m.DB.C("backfillMetaData").Find(
		bson.M{"$and": []bson.M{
			bson.M{"courseNumber": courseNumber}}}).All(&metaData)
	
	if err != nil {
		return nil, err
	}

	return metaData, nil
}
// Copyright (c) 2021 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package mongo

import (
	"fmt"
	"errors"
	bson "github.com/globalsign/mgo/bson"
	models "go.edusense.io/storage/models"
)

func (m *Driver) InsertBackfillMetaData(metaData models.BackfillMetaData) error {
	if metaData.CourseNumber == "" {
		return errors.New("Must include courseNumber in schema, look at BackfillMetaData Model")
	}
	// insert
	collectionName := fmt.Sprintf("backfill-course-%s", metaData.CourseNumber)
	err := m.DB.C(collectionName).Insert(&metaData)
	if err != nil {
		return err
	}

	return nil
}

func (m *Driver) GetBackfillMetaDataFilter(courseNumber string) ([]models.BackfillMetaData, error) {
    var metaData []models.BackfillMetaData

	collectionName := fmt.Sprintf("backfill-course-%s", courseNumber)
	err := m.DB.C(collectionName).Find(
		bson.M{"$and": []bson.M{
			bson.M{"courseNumber": courseNumber}}}).All(&metaData)
	
	if err != nil {
		return nil, err
	}

	return metaData, nil
}
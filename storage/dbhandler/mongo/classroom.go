// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package mongo

import ("fmt"
	//"errors"

	bson "github.com/globalsign/mgo/bson"
	models "go.edusense.io/storage/models"
)


func (m *Driver) InsertClassroomCollection (classroom models.Classroom) error {
	fmt.Println("Adding classroom....")
	// insert
	err := m.DB.C("classroom").Insert(&classroom)
	if err != nil {
		return err
	}

	return nil
}

func (m *Driver) GetClassroom (filter *models.SessionFilter) ([]models.Classroom, error) {
        var mSesses []models.Classroom


	objectIDStart := bson.NewObjectIdWithTime(filter.TimestampStart)
	objectIDEnd := bson.NewObjectIdWithTime(filter.TimestampEnd)

        // check whether valid session
	err := m.DB.C("classroom").Find(
		bson.M{"$and": []bson.M{
			bson.M{"_id": bson.M{"$gte": objectIDStart}},
			bson.M{"_id": bson.M{"$lte": objectIDEnd}}}}).All(&mSesses)

	if err != nil {
		return nil, err
	}

	return mSesses, nil
}

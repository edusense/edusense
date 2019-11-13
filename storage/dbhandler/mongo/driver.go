// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package mongo

import (
	mgo "github.com/globalsign/mgo"
)

// Driver implements DatabaseDriver interface for MongoDB  database backend.
type Driver struct {
	DB *mgo.Database
}

// NewMongoDriver creates a new mongoDB driver by host/port and database
// of mongoDB.
func NewMongoDriver(hostPort, database string) (*Driver, error) {
	sess, err := mgo.Dial(hostPort)
	if err != nil {
		return nil, err
	}

	return &Driver{DB: sess.DB(database)}, nil
}

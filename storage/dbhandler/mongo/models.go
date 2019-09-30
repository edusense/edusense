package mongo

import (
	"time"

	bson "github.com/globalsign/mgo/bson"
)

// Session specifies bson-specific formatting of session object.
type Session struct {
	ID       bson.ObjectId `bson:"_id"`
	Keyword  string        `bson:"keyword"`
	Schemas  []string      `bson:"schemas"`
	Metadata interface{}   `bson:"metadata"`
}

// Frame specifies bson-specific formatting of freeframe object.
type Frame struct {
	FrameNumber uint32      `bson:"frame_number"`
	Timestamp   time.Time   `bson:"timestamp"`
	Data        interface{} `bson:"data"`
}

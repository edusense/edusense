package models

import (
	"time"
)

// Session specification
type Session struct {
	ID        string      `json:"id,omitempty" bson:"id"`
	Keyword   string      `json:"keyword,omitempty" bson:"keyword"`
	Schemas   []string    `json:"schemas,omitempty" bson:"schemas"`
	Timestamp time.Time   `json:"timestamp,omitempty" bson:"timestamp"`
	Metadata  interface{} `json:"metadata,omitempty" bson:"metadata"`
}

// Session filter specifications for range search
type SessionFilter struct {
	TimestampStart time.Time `json:"startTimeAfter,omitempty"`
	TimestampEnd   time.Time `json:"startTimeBefore,omitempty"`
	Keyword        string    `json:"keyword,omitempty"`
}

// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

// FrameArgs defines arguments for frame queries.
type FrameArgs struct {
	Schema      string
	Channel     string
	FrameNumber *FrameNumberQuery
	Timestamp   *TimestampQuery
}

// FrameNumberQuery defines aggregated frame number query.
type FrameNumberQuery struct {
	Filters *[]FrameNumberQueryFilter
}

// FrameNumberQueryFilter defines filter operator for frame number query.
type FrameNumberQueryFilter struct {
	Op     string
	Number int32
}

// TimestampQuery defines aggregated timestamp query.
type TimestampQuery struct {
	Filters *[]TimestampQueryFilter
}

// TimestampQueryFilter defines filter operator for timestamp query.
type TimestampQueryFilter struct {
	Op        string
	Format    string
	Timestamp TimestampInput
}

// TimestampInput defines timestamp input format.
type TimestampInput struct {
	RFC3339         *string
	UnixSeconds     *int32
	UnixNanoseconds *int32
}

// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package resolver

import (
	"context"
	"errors"
	"time"

	graphql "github.com/graph-gophers/graphql-go"
	dbhandler "go.edusense.io/storage/dbhandler"
	models "go.edusense.io/storage/models"
)

// SessionResolver queries database and resolves query-agnostic Session model.
type SessionResolver struct {
	Session    *models.Session
	FrameQuery bool
	Driver     dbhandler.DatabaseDriver
}

// SessionArgs defines parameters for session queries.
type SessionArgs struct {
	SessionID *string
	Keyword   *string
}

// Sessions returns list of session resolvers from underlying database.
func (q QueryResolver) Sessions(ctx context.Context, args SessionArgs) ([]*SessionResolver, error) {
	// if session id is specified, grab the session
	if args.SessionID != nil {
		session, err := q.Driver.GetSession(*args.SessionID)

		if err != nil {
			return []*SessionResolver{}, err
		}

		resolvers := []*SessionResolver{&SessionResolver{Driver: q.Driver, FrameQuery: true, Session: session}}
		return resolvers, nil
	}

	keyword := ""
	if args.Keyword != nil {
		keyword = *args.Keyword
	}

	filter := &models.SessionFilter{
		TimestampStart: time.Unix(0, 0),
		TimestampEnd:   time.Now(),
		Keyword:        keyword,
	}

	sessions, err := q.Driver.FindSession(filter)
	if err != nil {
		return []*SessionResolver{}, err
	}

	resolvers := make([]*SessionResolver, len(sessions))
	for i := range sessions {
		resolvers[i] = &SessionResolver{Driver: q.Driver, FrameQuery: false, Session: &sessions[i]}
	}

	return resolvers, nil
}

// ID extracts Session ID from given Session resolver.
func (s *SessionResolver) ID(ctx context.Context) (graphql.ID, error) {
	return graphql.ID(s.Session.ID), nil
}

// Keyword extracts keyword from given Session resolver.
func (s *SessionResolver) Keyword(ctx context.Context) (string, error) {
	return s.Session.Keyword, nil
}

func (s *SessionResolver) Version(ctx context.Context) (string, error) {
	        return s.Session.Version, nil
}

// Schemas extracts schemas from given Session resolver.
// TODO(DohyunKimOfficial): Currently returning empty list. After plumbing
// schemas to query and storage infrastructure, we can add schema resolving
// logic here.
func (s *SessionResolver) Schemas(ctx context.Context) ([]string, error) {
	return []string{}, nil
}

// CreatedAt extracts when this session is created at from given Session
// resolver.
func (s *SessionResolver) CreatedAt(ctx context.Context) (*TimeResolver, error) {
	return &TimeResolver{Time: s.Session.Timestamp}, nil
}

// VideoFrames extracts list of video frame resolvers from given Session
// resolver.
func (s *SessionResolver) VideoFrames(ctx context.Context, args FrameArgs) ([]*VideoFrameResolver, error) {
	if !s.FrameQuery {
		return []*VideoFrameResolver{}, errors.New("cannot query frames while querying sessions")
	}

	numberFilters := []models.FrameNumberFilter{}
	if args.FrameNumber != nil && args.FrameNumber.Filters != nil {
		numberFilters = make([]models.FrameNumberFilter, len(*args.FrameNumber.Filters))
		for i, f := range *args.FrameNumber.Filters {
			parsedFilter, _ := parseFrameNumberFilter(&f)
			numberFilters[i] = parsedFilter
		}
	}

	timestampFilters := []models.TimestampFilter{}
	if args.Timestamp != nil && args.Timestamp.Filters != nil {
		timestampFilters = make([]models.TimestampFilter, len(*args.Timestamp.Filters))
		for i, f := range *args.Timestamp.Filters {
			parsedFilter, err := parseTimestampFilter(&f)
			timestampFilters[i] = parsedFilter
			if err != nil {
				return []*VideoFrameResolver{}, err
			}
		}
	}

	frames, err := s.Driver.GetQueriableVideoFrameByFilter(s.Session.ID, args.Schema+"-video", args.Channel, numberFilters, timestampFilters)

	if err != nil {
		return []*VideoFrameResolver{}, err
	}

	resolvers := make([]*VideoFrameResolver, len(frames))
	for i, f := range frames {
		resolvers[i] = &VideoFrameResolver{Frame: f}
	}

	return resolvers, nil
}

// AudioFrames extracts list of audio frame resolvers from given Session
// resolver.
func (s *SessionResolver) AudioFrames(ctx context.Context, args FrameArgs) ([]*AudioFrameResolver, error) {
	if !s.FrameQuery {
		return []*AudioFrameResolver{}, errors.New("cannot query frames while querying sessions")
	}

	numberFilters := []models.FrameNumberFilter{}
	if args.FrameNumber != nil && args.FrameNumber.Filters != nil {
		numberFilters = make([]models.FrameNumberFilter, len(*args.FrameNumber.Filters))
		for i, f := range *args.FrameNumber.Filters {
			numberFilters[i], _ = parseFrameNumberFilter(&f)
		}
	}

	timestampFilters := []models.TimestampFilter{}
	if args.Timestamp != nil && args.Timestamp.Filters != nil {
		timestampFilters = make([]models.TimestampFilter, len(*args.Timestamp.Filters))
		for i, f := range *args.Timestamp.Filters {
			parsedFilter, err := parseTimestampFilter(&f)
			timestampFilters[i] = parsedFilter

			if err != nil {
				return []*AudioFrameResolver{}, err
			}
		}
	}

	frames, err := s.Driver.GetQueriableAudioFrameByFilter(s.Session.ID, args.Schema+"-audio", args.Channel, numberFilters, timestampFilters)

	if err != nil {
		return []*AudioFrameResolver{}, nil
	}

	resolvers := make([]*AudioFrameResolver, len(frames))
	for i, f := range frames {
		resolvers[i] = &AudioFrameResolver{Frame: f}
	}

	return resolvers, nil
}

func parseTimestampFilter(f *TimestampQueryFilter) (models.TimestampFilter, error) {
	switch f.Format {
	case "RFC3339":
		if f.Timestamp.RFC3339 == nil {
			return models.TimestampFilter{}, errors.New("RFC3339 timestamp not found")
		}

		t, err := time.Parse(time.RFC3339, *f.Timestamp.RFC3339)
		if err == nil {
			return models.TimestampFilter{Operator: f.Op, Timestamp: t}, nil
		}

		return models.TimestampFilter{}, err
	case "unixTimestamp":
		if f.Timestamp.UnixSeconds == nil {
			return models.TimestampFilter{}, errors.New("unix timestamp not found")
		} else if f.Timestamp.UnixNanoseconds == nil {
			return models.TimestampFilter{Operator: f.Op, Timestamp: time.Unix(int64(*f.Timestamp.UnixSeconds), 0)}, nil
		}

		return models.TimestampFilter{Operator: f.Op, Timestamp: time.Unix(int64(*f.Timestamp.UnixNanoseconds), 0)}, nil
	default:
		return models.TimestampFilter{}, errors.New("timestamp resolution error")
	}
}

func parseFrameNumberFilter(f *FrameNumberQueryFilter) (models.FrameNumberFilter, error) {
	return models.FrameNumberFilter{Operator: f.Op, FrameNumber: uint32(f.Number)}, nil
}

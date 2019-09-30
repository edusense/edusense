package resolver

import (
	"context"
	"time"
)

// TimeResolver resolves query-agnostic Time variable.
type TimeResolver struct {
	Time time.Time
}

// RFC3339 returns time in RFC3339 format to clients.
func (t *TimeResolver) RFC3339(ctx context.Context) (string, error) {
	return t.Time.Format(time.RFC3339), nil
}

// UnixSeconds returns time in unix seconds format to clients.
func (t *TimeResolver) UnixSeconds(ctx context.Context) (int32, error) {
	return int32(t.Time.Unix()), nil
}

// UnixNanoseconds returns time in nanosecond offset from UnixSeconds to
// clients.
func (t *TimeResolver) UnixNanoseconds(ctx context.Context) (int32, error) {
	return int32(t.Time.Nanosecond()), nil
}

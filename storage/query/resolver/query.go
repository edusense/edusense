package resolver

import (
	"errors"

	dbhandler "go.edusense.io/storage/dbhandler"
)

// QueryResolver resolves given GraphQL query.
type QueryResolver struct {
	Driver dbhandler.DatabaseDriver
}

// NewQueryRoot resolves database handler.
func NewQueryRoot(driver dbhandler.DatabaseDriver) (*QueryResolver, error) {
	if driver == nil {
		return nil, errors.New("Unable to Parse GraphQL")
	}

	return &QueryResolver{Driver: driver}, nil
}

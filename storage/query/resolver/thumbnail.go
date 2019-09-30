package resolver

import (
	"context"
	"encoding/base64"

	models "go.edusense.io/storage/models"
)

// ThumbnailResolver resolves query-agnostic Thumbnail model.
type ThumbnailResolver struct {
	Thumbnail models.Thumbnail
}

// OriginalRows returns the original height of the source image (Rows).
func (t *ThumbnailResolver) OriginalRows(ctx context.Context) (int32, error) {
	return int32(t.Thumbnail.Rows), nil
}

// OriginalCols returns the original weith of the source image (Cols).
func (t *ThumbnailResolver) OriginalCols(ctx context.Context) (int32, error) {
	return int32(t.Thumbnail.Cols), nil
}

// Binary returns the base64 encoding of the thumbnail.
func (t *ThumbnailResolver) Binary(ctx context.Context) (string, error) {
	return base64.StdEncoding.EncodeToString(t.Thumbnail.Binary), nil
}

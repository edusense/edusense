package resolver

import (
	"context"

	models "go.edusense.io/storage/models"
)

// PersonInferenceResolver resolves query-agnostic PersonInference model.
type PersonInferenceResolver struct {
	Inference models.PersonInference
}

// Posture extracts collection of posture inferences from given PersonInference
// resolver.
func (vi *PersonInferenceResolver) Posture(ctx context.Context) (*PostureResolver, error) {
	return &PostureResolver{Posture: vi.Inference.Posture}, nil
}

// Face extacts collection of face inferences from given PersonInference
// resolver.
func (vi *PersonInferenceResolver) Face(ctx context.Context) (*FaceResolver, error) {
	return &FaceResolver{Face: vi.Inference.Face}, nil
}

// Head extracts collection of head inferences from given PersonInference
// resolver.
func (vi *PersonInferenceResolver) Head(ctx context.Context) (*HeadResolver, error) {
	return &HeadResolver{Head: vi.Inference.Head}, nil
}

// TrackingID extracts tracking id field from given PersonInference
// resolver.
func (vi *PersonInferenceResolver) TrackingID(ctx context.Context) (*int32, error) {
	id := int32(vi.Inference.TrackingID)
	if vi.Inference.TrackingID <= 0 {
		return nil, nil
	}

	return &id, nil
}

// PostureResolver resolves query-agnostic Posture model.
type PostureResolver struct {
	Posture models.Posture
}

// ArmPose extracts arm pose (a.k.a. upper body pose) field from
// given Posture resolver.
func (p *PostureResolver) ArmPose(ctx context.Context) (*string, error) {
	if p.Posture.ArmPose == "" {
		return nil, nil
	}
	return &p.Posture.ArmPose, nil
}

// SitStand extracts sit vs. stand field from given Posture resolver.
func (p *PostureResolver) SitStand(ctx context.Context) (*string, error) {
	if p.Posture.SitStand == "" {
		return nil, nil
	}

	return &p.Posture.SitStand, nil
}

// CentroidDelta extracts centroid delta field from given Posture resolver.
func (p *PostureResolver) CentroidDelta(ctx context.Context) (*[]int32, error) {
	if len(p.Posture.CentroidDelta) == 0 {
		return nil, nil
	}

	vector := make([]int32, len(p.Posture.CentroidDelta))
	for i, k := range p.Posture.CentroidDelta {
		vector[i] = int32(k)
	}

	return &vector, nil
}

// ArmDelta extracts arm keypoint delta field from given Posture resolver.
func (p *PostureResolver) ArmDelta(ctx context.Context) (*[][]int32, error) {
	if len(p.Posture.ArmDelta) == 0 {
		return nil, nil
	}

	vector := make([][]int32, len(p.Posture.ArmDelta))
	for i, v := range p.Posture.ArmDelta {
		newPoint := make([]int32, len(v))
		for j, k := range v {
			newPoint[j] = int32(k)
		}
		vector[i] = newPoint
	}
	return &vector, nil
}

// FaceResolver resolves query-agnostic Face model.
type FaceResolver struct {
	Face models.Face
}

// BoundingBox extracts bounding box of face from given Face resolver.
func (f *FaceResolver) BoundingBox(ctx context.Context) (*[][]int32, error) {
	if len(f.Face.BoundingBox) == 0 {
		return nil, nil
	}

	vector := make([][]int32, len(f.Face.BoundingBox))
	for i, p := range f.Face.BoundingBox {
		newPoint := make([]int32, len(p))
		for j, k := range p {
			newPoint[j] = int32(k)
		}
		vector[i] = newPoint
	}
	return &vector, nil
}

// MouthOpen extracts mouth open/close inference from given Face resolver.
func (f *FaceResolver) MouthOpen(ctx context.Context) (*string, error) {
	if f.Face.MouthOpen == "" {
		return nil, nil
	}

	return &f.Face.MouthOpen, nil
}

// MouthSmile extracts smile/no-smile inference from given Face resolver.
func (f *FaceResolver) MouthSmile(ctx context.Context) (*string, error) {
	if f.Face.MouthSmile == "" {
		return nil, nil
	}

	return &f.Face.MouthSmile, nil
}

// Orientation extracts face orientation front/back inference from given Face
// resolver.
func (f *FaceResolver) Orientation(Ctx context.Context) (*string, error) {
	if f.Face.Orientation == "" {
		return nil, nil
	}

	return &f.Face.Orientation, nil
}

// HeadResolver resolves query-agnostic Head model.
type HeadResolver struct {
	Head models.Head
}

// Roll extracts roll of head from given Head resolver.
func (h *HeadResolver) Roll(ctx context.Context) (float64, error) {
	return float64(h.Head.Roll), nil
}

// Pitch extracts pitch of head from given Head resolver.
func (h *HeadResolver) Pitch(ctx context.Context) (float64, error) {
	return float64(h.Head.Pitch), nil
}

// Yaw extracts yaw of head from given Head resolver.
func (h *HeadResolver) Yaw(ctx context.Context) (float64, error) {
	return float64(h.Head.Yaw), nil
}

// TranslationVector extracts translation vector from given Head resolver.
func (h *HeadResolver) TranslationVector(ctx context.Context) (*[]float64, error) {
	if len(h.Head.TranslationVector) == 0 {
		return nil, nil
	}

	vector := make([]float64, len(h.Head.TranslationVector))
	for i, k := range h.Head.TranslationVector {
		vector[i] = float64(k)
	}

	return &vector, nil
}

// GazeVector extracts gaze vector from given Head resolver.
func (h *HeadResolver) GazeVector(ctx context.Context) (*[][]int32, error) {
	if len(h.Head.GazeVector) == 0 {
		return nil, nil
	}

	vector := make([][]int32, len(h.Head.GazeVector))
	for i, p := range h.Head.GazeVector {
		newPoint := make([]int32, len(p))
		for j, k := range p {
			newPoint[j] = int32(k)
		}
		vector[i] = newPoint
	}
	return &vector, nil
}

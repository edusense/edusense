// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package main

import (
	models "go.edusense.io/storage/models"
)

// AuthErrorResponse defines authentication error response to clients.
type AuthErrorResponse struct {
	Error string `json:"error"`
}

// InsertSessionRequest defines request format for insert session requests.
type InsertSessionRequest struct {
	Keyword    string      `json:"keyword,omitempty"`
	Developer  string      `json:"developer,omitempty"`
	Version    string      `json:"version,omitempty"`
	Overwrite  string      `json:"overwrite,omitempty"`
	Metadata   interface{} `json:"metadata,omitempty"`
}

// InsertSessionResponse defines response format for insert session requests.
type InsertSessionResponse struct {
	Success   bool   `json:"success"`
	SessionID string `json:"session_id,omitempty"`
	Error     string `json:"error,omitempty"`
	ErrorCode uint32 `json:"errorCode,omitempty"`
}

type InsertClassroomRequest struct {
	NewClass        models.Classroom        `json:"newClass,omitempty"`
}

type InsertClassroomResponse struct {
	Success   bool   `json:"success"`
	Error     string `json:"error,omitempty"`
	ErrorCode uint32 `json:"errorCode,omitempty"`
}


// InsertFrameRequest defines request format for insert free-form frame
// requests.
type InsertFrameRequest struct {
	Frames []interface{} `json:"frames,omitempty"`
}

// InsertQueriableVideoFrameRequest defines request format for insert video
// frame requests. Formatting the request into this format is important to make
// inserted frame compatible to GraphQL query schema.
type InsertQueriableVideoFrameRequest struct {
	Frames []models.VideoFrame `json:"frames,omitempty"`
}

// InsertQueriableAudioFrameRequest defines request format for insert audio
// frame requests. Formatting the request info this format is important to make
// inserted frame compatible to GraphQL query schema.
type InsertQueriableAudioFrameRequest struct {
	Frames []models.AudioFrame `json:"frames,omitempty"`
}

// InsertFrameResponse defines response format for insert frame requests.
type InsertFrameResponse struct {
	Success   bool   `json:"success"`
	Error     string `json:"error,omitempty"`
	ErrorCode uint32 `json:"errorCode,omitempty"`
}

// GetFramesQueryRequest defines request format for GraphQL queries.
type GetFramesQueryRequest struct {
	Query         string                 `json:"query"`
	OperationName string                 `json:"operationName"`
	Variables     map[string]interface{} `json:"variables"`
}

// GetFramesQueryResponse defines response format for GraphQL queries.
type GetFramesQueryResponse struct {
	Success   bool   `json:"success"`
	Response  string `json:"response"`
	Error     string `json:"error,omitempty"`
	ErrorCode uint32 `json:"errorCode,omitempty"`
}

// GetCameraStatusResponse defines response format for get camera status
// requests.
type GetCameraStatusResponse struct {
	Success    bool           `json:"success"`
	StatusList []cameraStatus `json:"camera_list"`
	Error      string         `json:"error,omitempty"`
	ErrorCode  uint32         `json:"errorCode,omitempty"`
}

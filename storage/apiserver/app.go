// Copyright (c) 2017-2019 Carnegie Mellon University. All rights reserved.
// Use of this source code is governed by BSD 3-clause license.

package main // import "go.edusense.io/storage/apiserver"

import (//"fmt"
	"crypto/tls"
	"encoding/json"
	"flag"
	"log"
	"net"
	"net/http"
	"os"

	mux "github.com/gorilla/mux"

	graphql "github.com/graph-gophers/graphql-go"

	dbhandler "go.edusense.io/storage/dbhandler"
	mongo "go.edusense.io/storage/dbhandler/mongo"
	query "go.edusense.io/storage/query"
)

var driver dbhandler.DatabaseDriver
var querySchema *graphql.Schema

func respondWithError(w http.ResponseWriter, code int, msg string) {
	respondWithJSON(w, code, map[string]string{"error": msg})
}

func respondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	response, _ := json.Marshal(payload)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(response)
}

// Endpoint to insert a Classroom. Could combine classroom and course endpoint as metadata endpoint
func InsertClassroomEndpoint(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	var req InsertClassroomRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	err := driver.InsertClassroomCollection(req.NewClass)
	if err != nil {
		resp := &InsertClassroomResponse{
			Success:   false,
			Error:     err.Error(),
			ErrorCode: 1,
		}
		respondWithJSON(w, http.StatusOK, resp)
		return
	}

	resp := &InsertClassroomResponse{
		Success:   true,
	}

	respondWithJSON(w, http.StatusOK, resp)
}


// Endpoint to insert a course. Could combine classroom and course endpoint as metadata endpoint
func InsertCourseEndpoint(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	var req InsertCourseRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	err := driver.InsertCourseCollection(req.NewCourse)
	if err != nil {
		resp := &InsertClassroomResponse{
			Success:   false,
			Error:     err.Error(),
			ErrorCode: 1,
		}
		respondWithJSON(w, http.StatusOK, resp)
		return
	}

	//Using InsertClassroomResponse to respond to course query as well
	resp := &InsertClassroomResponse{
		Success:   true,
	}

	respondWithJSON(w, http.StatusOK, resp)
}


func InsertSessionEndpoint(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	var req InsertSessionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}

	sess, err := driver.InsertSession(req.Developer, req.Version, req.Keyword, req.Overwrite, req.Metadata)
	if err != nil {
		resp := &InsertSessionResponse{
			Success:   false,
			Error:     err.Error(),
			ErrorCode: 1,
		}
		respondWithJSON(w, http.StatusOK, resp)
		return
	}

	resp := &InsertSessionResponse{
		Success:   true,
		SessionID: sess.ID,
	}
	respondWithJSON(w, http.StatusOK, resp)
}

// InsertFrameEndpoint reponds to legacy InsertFrame endpoint
// (POST /sessions/{session_id}/{type}/frames/{schema}/{channel}/).
func InsertFrameEndpoint(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	// check whether session ID is specified
	params := mux.Vars(r)
	sessID, ok := params["session_id"]
	if !ok {
		resp := &InsertFrameResponse{
			Success:   false,
			Error:     "invalid session ID",
			ErrorCode: 1,
		}
		respondWithJSON(w, http.StatusBadRequest, resp)
		return
	}

	schema, ok := params["schema"]
	if !ok {
		resp := &InsertFrameResponse{
			Success:   false,
			Error:     "schema not specified",
			ErrorCode: 1,
		}
		respondWithJSON(w, http.StatusBadRequest, resp)
		return
	}

	channel, ok := params["channel"]
	if !ok {
		resp := &InsertFrameResponse{
			Success:   false,
			Error:     "channel not specified",
			ErrorCode: 1,
		}
		respondWithJSON(w, http.StatusBadRequest, resp)
		return
	}

	mediaType, ok := params["type"]
	if mediaType == "video" {
		var videoReq InsertQueriableVideoFrameRequest

		if err := json.NewDecoder(r.Body).Decode(&videoReq); err == nil {
			for _, frame := range videoReq.Frames {
				if err := driver.InsertQueriableVideoFrame(sessID, schema, channel, frame); err != nil {
					resp := &InsertFrameResponse{
						Success:   false,
						Error:     err.Error(),
						ErrorCode: 1,
					}
					respondWithJSON(w, http.StatusOK, resp)
					return
				}
			}
		} else {
			resp := &InsertFrameResponse{
				Success:   false,
				Error:     err.Error(),
				ErrorCode: 1,
			}
			respondWithJSON(w, http.StatusOK, resp)
			return
		}
	} else if mediaType == "audio" {
		var audioReq InsertQueriableAudioFrameRequest
		if err := json.NewDecoder(r.Body).Decode(&audioReq); err == nil {
			for _, frame := range audioReq.Frames {
				if err = driver.InsertQueriableAudioFrame(sessID, schema, channel, frame); err != nil {
					resp := &InsertFrameResponse{
						Success:   false,
						Error:     err.Error(),
						ErrorCode: 2,
					}
					respondWithJSON(w, http.StatusOK, resp)
					return
				}
			}
		} else {
			resp := &InsertFrameResponse{
				Success:   false,
				Error:     err.Error(),
				ErrorCode: 1,
			}
			respondWithJSON(w, http.StatusOK, resp)
			return
		}
	} else {
		var req InsertFrameRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err == nil {
			for _, frame := range req.Frames {
				if err := driver.InsertFrame(sessID, schema, channel, frame); err != nil {
					resp := &InsertFrameResponse{
						Success:   false,
						Error:     err.Error(),
						ErrorCode: 1,
					}
					respondWithJSON(w, http.StatusOK, resp)
					return
				}
			}
		} else {
			resp := &InsertFrameResponse{
				Success:   false,
				Error:     err.Error(),
				ErrorCode: 1,
			}
			respondWithJSON(w, http.StatusOK, resp)
			return
		}
	}

	resp := &InsertFrameResponse{
		Success: true,
	}

	respondWithJSON(w, http.StatusOK, resp)
}

// QueryEndpoint responds all new GraphQL queries (POST /query).
func QueryEndpoint(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	var req GetFramesQueryRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		resp := &GetFramesQueryResponse{
			Success:   false,
			Error:     "invalid request payload",
			ErrorCode: 1,
		}
		respondWithJSON(w, http.StatusBadRequest, resp)
		return
	}

	queryResult := querySchema.Exec(r.Context(), req.Query, req.OperationName,
		req.Variables)
	resultJSON, err := json.Marshal(queryResult)
	if err != nil {
		resp := &GetFramesQueryResponse{
			Success:   false,
			Error:     "error occured when running query",
			ErrorCode: 1,
		}
		respondWithJSON(w, http.StatusInternalServerError, resp)
		return
	}

	resp := &GetFramesQueryResponse{
		Success:  true,
		Response: string(resultJSON),
	}

	respondWithJSON(w, http.StatusOK, resp)
}

func main() {
	portPtr := flag.String("port", "3000", "port for REST API")
	dbHostPortPtr := flag.String("dbhost", "localhost:27017", "host:port for MongoDB")
	dbPtr := flag.String("db", "edusense", "db name for MongoDB")
	flag.Parse()

	// Check host/port
	hostPort := net.JoinHostPort("", *portPtr)

	// get keys
	certPem := os.Getenv("SSL_CERT")
	keyPem := os.Getenv("SSL_CERT_PRIVATE_KEY")
	username := os.Getenv("APP_USERNAME")
	password := os.Getenv("APP_PASSWORD")

	// TODO(DohyunKimOfficial): add mongo db credentials

	// Set up database.
	// TODO(DohyunKimOfficial): add memory-only db-like construct for testing.
	var err error
	driver, err = mongo.NewMongoDriver(*dbHostPortPtr, *dbPtr)
	if err != nil {
		log.Fatal(err)
	}

	// Set up authentication
	auth, err := NewAuthDriver(username, password)
	if err != nil {
		log.Fatal(err)
	}

	// Set up query
	querySchema = query.MustParseSchema(driver)

	// Set up camera monitor
	cameraInfos := []cameraInfo{}
	initializeCameraMonitor(cameraInfos, 300)

	// Set up mux router for REST APIs
	router := mux.NewRouter()

	// Mutation REST Endpoints
	// Get class information. Legacy endpoints only for posting sessions/frames.
	// TODO(DohyunKimOfficial): Implement proper mutation in GraphQL
	router.HandleFunc("/classroom", auth.BasicAuth(InsertClassroomEndpoint)).Methods("POST")
	router.HandleFunc("/course", auth.BasicAuth(InsertCourseEndpoint)).Methods("POST")
	router.HandleFunc("/sessions", auth.BasicAuth(InsertSessionEndpoint)).Methods("POST")
	router.HandleFunc("/sessions/{session_id}/{type}/frames/{schema}/{channel}/", auth.BasicAuth(InsertFrameEndpoint)).Methods("POST")

	// Query REST Endpoints
	// Unified query endpoint.
	router.HandleFunc("/query", auth.BasicAuth(QueryEndpoint)).Methods("POST") // Support for GraphQL

	// Camera query endpoints.
	// TODO(DohyunKimOfficial): Implement this in GraphQL
	router.HandleFunc("/camera/status", auth.BasicAuth(GetCameraStatusEndpoint)).Methods("GET")
	router.HandleFunc("/camera/status/{camera_name}", auth.BasicAuth(GetCameraStatusEndpoint)).Methods("GET")

	// Setup SSL/TLS and start web server.
	if certPem != "" && keyPem != "" {
		cert, err := tls.X509KeyPair([]byte(certPem), []byte(keyPem))
		if err != nil {
			log.Fatal(err)
		}

		cfg := &tls.Config{
			MinVersion:               tls.VersionTLS12,
			CurvePreferences:         []tls.CurveID{tls.CurveP521, tls.CurveP384, tls.CurveP256},
			PreferServerCipherSuites: true,
			CipherSuites: []uint16{
				tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
				tls.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,
				tls.TLS_RSA_WITH_AES_256_GCM_SHA384,
				tls.TLS_RSA_WITH_AES_256_CBC_SHA,
			},
			Certificates: []tls.Certificate{cert},
		}

		srv := &http.Server{
			Addr:         hostPort,
			Handler:      router,
			TLSConfig:    cfg,
			TLSNextProto: make(map[string]func(*http.Server, *tls.Conn, http.Handler), 0),
		}

		log.Println("Starting apiserver with TLS")
		if err = srv.ListenAndServeTLS("", ""); err != nil {
			exitCameraMonitor()
			log.Fatal(err)
		}
	} else {
		log.Println("Starting api server without TLS")
		if err = http.ListenAndServe(hostPort, router); err != nil {
			exitCameraMonitor()
			log.Fatal(err)
		}
	}
}

package main

import (
	"log"
	"net/http"
)

const defaultUsername = "edusense"
const defaultPassword = "onlyForDevelopmentDoNotUseDefaultPasswordInProduction"
const defaultWarning = `You are using default username and password. Do not use default credentials in production`

// AuthDriver manages user credentials.
// TODO(DohyunKimOfficial): Implement proper authentication with DB.
type AuthDriver struct {
	Username string
	Password string
}

// NewAuthDriver creates a new AuthDriver with given username and password.
func NewAuthDriver(username string, password string) (*AuthDriver, error) {
	if username == "" || password == "" {
		log.Println(defaultWarning)

		auth := &AuthDriver{Username: defaultUsername, Password: defaultPassword}
		return auth, nil
	}

	return &AuthDriver{Username: username, Password: password}, nil
}

// BasicAuth handles HTTP request with HTTP basic authentication.
func (a *AuthDriver) BasicAuth(h http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("WWW-Authenticate", `Basic realm="Restricted"`)

		username, password, ok := r.BasicAuth()
		if !ok || !a.handleAuth(username, password, r) {
			a.handleUnauthorized(w, r)
		} else {
			h.ServeHTTP(w, r)
		}
	}
}

func (a *AuthDriver) handleAuth(user, pass string, r *http.Request) bool {
	// ToDo: complete DB integration of username and password
	return user == a.Username && pass == a.Password
}

func (a *AuthDriver) handleUnauthorized(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	resp := &AuthErrorResponse{
		Error: "Unauthorized",
	}
	respondWithJSON(w, http.StatusUnauthorized, resp)

	return
}

package main

import (
	"net"
	"net/http"
	"time"

	mux "github.com/gorilla/mux"
)

type cameraMonitor struct {
	CameraInfos     []cameraInfo
	RefreshInterval time.Duration
	ReqsChan        chan cameraStatusRequest
	ExitChan        chan bool
	DoneChan        chan bool
}

var monitor *cameraMonitor

type cameraStatusRequest struct {
	Name  string
	Resps chan cameraStatusResponse
}

type cameraInfo struct {
	Name string
	Host string
	Port string
}

type cameraStatus struct {
	Name      string    `json:"name"`
	Status    string    `json:"status"`
	ErrorMsg  string    `json:"error_message,omit_empty"`
	Timestamp time.Time `json:"timestamp"`
}

type cameraStatusResponse struct {
	StatusList []cameraStatus `json:"camera_list"`
}

func checkConnectivity(cameraURL string) (string, string) {
	// resolve address
	_, err := net.ResolveTCPAddr("tcp", cameraURL)
	if err != nil {
		return "R", err.Error()
	}

	// 1 second timeout
	conn, err := net.DialTimeout("tcp", cameraURL, time.Duration(1)*time.Second)
	if err != nil {
		return "C", err.Error()
	}

	conn.Close()

	return "S", "Online"
}

func asyncCheckConnectivity(info cameraInfo, statusChan chan<- cameraStatus) {
	code, msg := checkConnectivity(net.JoinHostPort(info.Host, info.Port))
	status := cameraStatus{
		Name:      info.Name,
		Status:    code,
		ErrorMsg:  msg,
		Timestamp: time.Now(),
	}

	statusChan <- status
}

func (m *cameraMonitor) RunMonitor() {
	statusChan := make(chan cameraStatus)
	cameraStatusDict := make(map[string]cameraStatus)
	for _, info := range m.CameraInfos {
		cameraStatusDict[info.Name] = cameraStatus{
			Name:      info.Name,
			Status:    "U",
			ErrorMsg:  "Unknown: not checked yet",
			Timestamp: time.Now(),
		}
	}

	timer := time.NewTimer(m.RefreshInterval)
	for _, info := range m.CameraInfos {
		go asyncCheckConnectivity(info, statusChan)
	}

servingLoop:
	for {
		select {
		case <-m.ExitChan:
			break servingLoop
		case req := <-m.ReqsChan:
			// get all status
			statusList := []cameraStatus{}
			if req.Name == "" {
				for _, status := range cameraStatusDict {
					statusList = append(statusList, status)
				}
			} else if status, ok := cameraStatusDict[req.Name]; ok {
				statusList = append(statusList, status)
			}

			req.Resps <- cameraStatusResponse{
				StatusList: statusList,
			}
		case status := <-statusChan:
			cameraStatusDict[status.Name] = status
		case <-timer.C:
			for _, info := range m.CameraInfos {
				go asyncCheckConnectivity(info, statusChan)
			}
			timer = time.NewTimer(m.RefreshInterval)
		}
	}

	m.DoneChan <- true
}

// GetCameraStatusEndpoint responds to legacy CameraStatus queries
// (POST /camera/status, camera/status/{camera_name}).
func GetCameraStatusEndpoint(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	params := mux.Vars(r)
	cameraName, ok := params["camera_name"]
	if !ok {
		cameraName = ""
	}

	respChan := make(chan cameraStatusResponse)
	monitor.ReqsChan <- cameraStatusRequest{
		Name:  cameraName,
		Resps: respChan,
	}

	statusResp := <-respChan
	resp := GetCameraStatusResponse{
		Success:    true,
		StatusList: statusResp.StatusList,
	}
	respondWithJSON(w, http.StatusOK, resp)
}

func initializeCameraMonitor(cameraInfos []cameraInfo, refreshInterval int) {
	monitor = &cameraMonitor{
		CameraInfos:     cameraInfos,
		RefreshInterval: time.Duration(refreshInterval) * time.Second,
		ReqsChan:        make(chan cameraStatusRequest),
		ExitChan:        make(chan bool),
		DoneChan:        make(chan bool),
	}

	go monitor.RunMonitor()
}

func exitCameraMonitor() {
	monitor.ExitChan <- true
	<-monitor.DoneChan
}

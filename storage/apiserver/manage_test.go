package main

import (
	"testing"
	"time"
)

func TestConnectionCheck(t *testing.T) {
	code, _ := checkConnectivity("www.google.com:https")
	if code != "S" {
		t.Errorf("connection testing to www.google.com:https failed")
	}
}

func TestConnectionCheckRoutine(t *testing.T) {
	cameraInfos := []cameraInfo{
		cameraInfo{"google", "www.google.com", "https"}}
	initializeCameraMonitor(cameraInfos, 10)

retryLoop:
	for {
		respChan := make(chan cameraStatusResponse)
		monitor.ReqsChan <- cameraStatusRequest{
			Name:  "google",
			Resps: respChan,
		}

		timer := time.NewTimer(time.Duration(1) * time.Second)
		resp := <-respChan
		if len(resp.StatusList) != 1 {
			t.Errorf("unexpected number of cameras returned")
		} else {
			status := resp.StatusList[0]
			switch status.Status {
			case "S":
				// success
				break retryLoop
			case "R":
				t.Errorf("connection testing to www.google.com:https failed due to resolution error")
				break retryLoop
			case "U":
				// continue with time delay
				<-timer.C
				timer = time.NewTimer(time.Duration(1) * time.Second)
			case "C":
				t.Errorf("connection testing to www.google.com:https failed")
				break retryLoop
			}
		}
	}

	exitCameraMonitor()
}

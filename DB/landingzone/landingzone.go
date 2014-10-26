package main

import (
    "fmt"
    "net"
)

const (
    HOST = "0.0.0.0"
    PORT = "9000"
    INPUT_BUFFER_SIZE = 1024
)

// Extract data sent from sensor from request
func decodePacket (buffer []byte) {

}

// Handle a client's request
func handleRequest (conn net.Conn) {
    buffer := make ([]byte, INPUT_BUFFER_SIZE)
    requestLength, err := conn.Read (buffer)
    if err != nil {
        fmt.Println ("Error handling request: " + err.Error())
    } else if requestLength < 1 {
        fmt.Println ("Error: expected to receive request but got empty request")
    }

    conn.Write ([]byte("Response"))
    conn.Close()
}

func main() {
    listener, err := net.Listen ("tcp", HOST + ":" + PORT)
    if err != nil {
        fmt.Println ("Failed to open listener on port " + PORT)
        fmt.Println ("Error was: " + err.Error())
    }
    defer listener.Close()

    // Handle requests in a go routine
    for {
        conn, err := listener.Accept()
        if err != nil {
            fmt.Println ("Failed to accept request: " + err.Error())
        }
        handleRequest (conn);
    }
}

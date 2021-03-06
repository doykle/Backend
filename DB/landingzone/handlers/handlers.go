package handlers

import (
	"errors"
	"io"
	"log"
	"net"
	"time"

	"github.com/seadsystem/Backend/DB/landingzone/constants"
	"github.com/seadsystem/Backend/DB/landingzone/database"
	"github.com/seadsystem/Backend/DB/landingzone/decoders"
)

// Errors
var Timeout = errors.New("Action timed out.")
var InvalidLength = errors.New("Invalid length header.")

// HandleRequest handles a communication stream with a plug.
func HandleRequest(conn net.Conn, db database.DB) {
	log.Println("Got a connection.")

	var err error

	// Do initial sync to get serial number and start receiving data
	serial, offset, err := sync(conn)
	if err != nil {
		readError(err)
		return
	}

	// Main data receiving loop
	for {
		packet, err := readPacket(conn)

		if err != nil {
			// Kill connection to allow plug to reestablish a new connection
			break
		}

		log.Println("Parsing data...")
		data, err := decoders.DecodePacket(packet, offset)
		if err != nil {
			readError(err)
			break
		}
		data.Serial = serial
		log.Printf("Data: %+v\n", data)

		log.Println("Sending to database...")
		go db.InsertRawPacket(data)

		log.Println("Sending ACK...")
		writePacket(conn, []byte(constants.ACK))
		if err != nil {
			readError(err)
			break
		}
	}

	log.Println("Closing connection...")
	conn.Close()
	log.Println("Connection closed.")
}

// sync re-aligns the packets, resets the plug's configuration and resumes data transfer.
func sync(conn net.Conn) (serial int, offset time.Time, err error) {
	log.Println("Sending HEAD...")
	err = writePacket(conn, []byte(constants.HEAD))
	if err != nil {
		return
	}

	log.Println("Reading header...")
	data, err := readPacket(conn)
	if err != nil {
		return
	}

	log.Println("Parsing header for serial...")
	serial, offset, err = decoders.DecodeHeader(data)
	if err != nil {
		return
	}
	log.Printf("Plug serial: %d\n", serial)
	log.Printf("Plug offset: %+v\n", offset)

	log.Println("Sending configuration...")
	err = writePacket(conn, []byte(constants.CONFIG))
	if err != nil {
		return
	}

	log.Println("Sending OKAY...")
	err = writePacket(conn, []byte(constants.OKAY))
	if err != nil {
		return
	}

	return
}

// writePacket writes a message to the specified connection with proper error handling.
func writePacket(conn net.Conn, data []byte) (err error) {
	conn.SetWriteDeadline(time.Now().Add(time.Second * constants.WRITE_TIME_LIMIT))
	write_length, err := conn.Write(data)
	if err != nil {
		return
	}
	if write_length != len(data) {
		err = io.ErrShortWrite
		return
	}

	return
}

// readPacket reads in an entire packet (including length prefix) with proper error handling. The packet's payload (the entire packet minus the length prefix) is returned.
func readPacket(conn net.Conn) (data []byte, err error) {
	log.Println("Reading length header...")
	length_header, err := readBytes(conn, constants.LENGTH_HEADER_SIZE)
	if err != nil {
		return
	}

	log.Printf("Received length header: %s\n", length_header)
	data_length := decoders.Binary2uint(length_header[1:3])

	// Check that we got a length header
	if length_header[0] != 'L' || data_length == 0 {
		err = InvalidLength
		return
	}

	log.Printf("Length: %d\n", data_length)

	// Get the rest of the packet
	data, err = readBytes(conn, int(data_length-constants.LENGTH_HEADER_SIZE))
	if err != nil {
		return
	}

	log.Println("Read data:")
	log.Println(string(data))

	log.Println("Sending ACK...")
	err = writePacket(conn, []byte(constants.ACK))
	if err != nil {
		return
	}

	return
}

// readError checks the error and prints an appropriate friendly error message.
func readError(err error) {
	if err == io.EOF {
		log.Println("Done reading bytes.")
	} else {
		log.Println("Read error:", err)
	}
}

// readBytes reads the specified number of bytes from the connection with a time limit store in constants.READ_TIME_LIMIT. The timeout kills unneeded connections and helps unstick stuck plug interactions.
func readBytes(conn net.Conn, bytes int) (data []byte, err error) {
	conn.SetReadDeadline(time.Now().Add(time.Second * constants.READ_TIME_LIMIT))

	buffer := make([]byte, bytes)
	n, err := conn.Read(buffer)

	if err != nil {
		return
	}

	if bytes != n {
		err = io.ErrShortWrite
		return
	}
	data = buffer

	return
}

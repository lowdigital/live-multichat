<?php
	header("Content-Type: application/json");
	include ("options.php");

	$conn = new mysqli($host, $user, $pass, $db);

	if ($conn->connect_error) {
		http_response_code(500);
		echo json_encode(["status" => "error", "message" => "Database connection failed: " . $conn->connect_error]);
		exit;
	}

	$conn->set_charset("utf8mb4");

	$input = file_get_contents('php://input');

	if ($input) {
		$data = json_decode($input, true);
		
		if (json_last_error() === JSON_ERROR_NONE) {
			if (isset($data['source']) && isset($data['username']) && isset($data['message'])) {
				$source = $conn->real_escape_string($data['source']);
				$username = $conn->real_escape_string($data['username']);
				$message = $conn->real_escape_string($data['message']);
				
				$sql = "INSERT INTO chat (source, user_name, message) VALUES ('$source', '$username', '$message')";
				if ($conn->query($sql) === TRUE) {
					
					http_response_code(200);
					echo json_encode(["status" => "success", "message" => "Data saved successfully."]);
				} else {
					http_response_code(500);
					echo json_encode(["status" => "error", "message" => "Database error: " . $conn->error]);
				}
			} else {
				http_response_code(400);
				echo json_encode(["status" => "error", "message" => "Invalid data format. 'source', 'username', and 'message' are required."]);
			}
		} else {
			http_response_code(400);
			echo json_encode(["status" => "error", "message" => "Invalid JSON format."]);
		}
	} else {
		http_response_code(400);
		echo json_encode(["status" => "error", "message" => "No data received."]);
	}

	$conn->close();
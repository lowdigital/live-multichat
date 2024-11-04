<?php
	include ("options.php");
	
	$conn = new mysqli($host, $user, $pass, $db);
	if ($conn->connect_error) {
		die("Ошибка подключения: " . $conn->connect_error);
	}

	$conn->set_charset("utf8mb4");

	$sql = "SELECT id, source, user_name, message, date 
			FROM chat 
			WHERE date >= DATE_SUB(NOW(), INTERVAL 3 MINUTE)
			ORDER BY id DESC 
			LIMIT 10";
	$result = $conn->query($sql);

	$messages = [];
	$idsToKeep = [];
	if ($result->num_rows > 0) {
		while ($row = $result->fetch_assoc()) {
			$messages[] = $row;
			$idsToKeep[] = $row['id'];
		}
	}

	if (!empty($idsToKeep)) {
		$idsList = implode(',', $idsToKeep);
		$deleteSql = "DELETE FROM chat WHERE id NOT IN ($idsList)";
		if (!$conn->query($deleteSql)) {
			echo "Ошибка удаления записей: " . $conn->error;
		}
	}

	$conn->close();
	echo json_encode(array_reverse($messages));
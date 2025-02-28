<?php
// CORS-Header setzen (erlaubt Zugriff von allen Domains)
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, X-API-Key, anthropic-version");
header("Access-Control-Max-Age: 3600");
header("Content-Type: application/json");

// Bei OPTIONS-Anfragen (Preflight) gleich beenden
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Nur POST-Anfragen zulassen
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method Not Allowed']);
    exit;
}

// JSON-Daten aus dem Request-Body lesen
$requestData = json_decode(file_get_contents('php://input'), true);

// Überprüfen, ob alle notwendigen Daten vorhanden sind
if (!isset($requestData['apiKey']) || !isset($requestData['messages']) || !isset($requestData['model'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields (apiKey, messages, model)']);
    exit;
}

// Anthropic API-Anfrage vorbereiten
$apiUrl = 'https://api.anthropic.com/v1/messages';
$apiKey = $requestData['apiKey'];
$model = $requestData['model'];
$messages = $requestData['messages'];
$maxTokens = isset($requestData['max_tokens']) ? $requestData['max_tokens'] : 1024;

// Anfrage an Anthropic API senden
$ch = curl_init($apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-API-Key: ' . $apiKey,
    'anthropic-version: 2023-06-01'
]);

// Payload für Anthropic API
$payload = json_encode([
    'model' => $model,
    'messages' => $messages,
    'max_tokens' => $maxTokens
]);

curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);

// Antwort und HTTP-Status Code erhalten
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// HTTP-Status Code von Anthropic weitergeben
http_response_code($httpCode);

// Antwort weiterleiten
echo $response;
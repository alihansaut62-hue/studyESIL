<?php
require_once 'config/database.php';

if($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['email'])) {
    $email = $_POST['email'];
    
    try {
        $stmt = $pdo->prepare("INSERT INTO newsletter_subscribers (email) VALUES (?)");
        $stmt->execute([$email]);
        $_SESSION['message'] = 'Successfully subscribed!';
    } catch(PDOException $e) {
        $_SESSION['error'] = 'You are already subscribed!';
    }
    
    header('Location: ' . $_SERVER['HTTP_REFERER']);
}
?>
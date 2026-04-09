<?php
session_start();
require_once 'config/database.php';

if($_SERVER['REQUEST_METHOD'] == 'POST') {
    $first_name = $_POST['first_name'];
    $last_name = $_POST['last_name'];
    $email = $_POST['email'];
    $phone = $_POST['phone'];
    $password = $_POST['password'];
    $confirm_password = $_POST['confirm_password'];
    
    // Проверка совпадения паролей
    if($password !== $confirm_password) {
        $_SESSION['error'] = 'Passwords do not match!';
        header('Location: index.php?page=signup');
        exit();
    }
    
    // Хеширование пароля
    $password_hash = password_hash($password, PASSWORD_DEFAULT);
    
    try {
        // Проверка, существует ли уже email
        $check = $pdo->prepare("SELECT id FROM users WHERE email = ?");
        $check->execute([$email]);
        
        if($check->rowCount() > 0) {
            $_SESSION['error'] = 'Email already exists!';
            header('Location: index.php?page=signup');
            exit();
        }
        
        // Вставка нового пользователя
        $stmt = $pdo->prepare("INSERT INTO users (first_name, last_name, email, phone, password_hash) VALUES (?, ?, ?, ?, ?)");
        $stmt->execute([$first_name, $last_name, $email, $phone, $password_hash]);
        
        $_SESSION['user_id'] = $pdo->lastInsertId();
        $_SESSION['user_email'] = $email;
        $_SESSION['user_name'] = $first_name . ' ' . $last_name;
        
        // Перенаправление на страницу благодарности
        header('Location: index.php?page=thank-you');
        exit();
        
    } catch(PDOException $e) {
        $_SESSION['error'] = 'Registration failed: ' . $e->getMessage();
        header('Location: index.php?page=signup');
        exit();
    }
} else {
    // Если кто-то пытается зайти напрямую
    header('Location: index.php?page=signup');
    exit();
}
?>
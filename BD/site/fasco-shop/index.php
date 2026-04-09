<?php
session_start();
require_once 'config/database.php';

$page = isset($_GET['page']) ? $_GET['page'] : 'home';

include 'includes/header.php';
include 'includes/navbar.php';

switch($page) {
    case 'shop':
        include 'pages/shop.php';
        break;
    case 'product':
        include 'pages/product.php';
        break;
    case 'cart':
        include 'pages/cart.php';
        break;
    case 'checkout':
        include 'pages/checkout.php';
        break;
    case 'login':
        include 'pages/login.php';
        break;
    case 'signup':
        include 'pages/signup.php';
        break;
    case 'forgot-password':
        include 'pages/forgot-password.php';
        break;
    case 'thank-you':
        include 'pages/thank-you.php';
        break;
    default:
        include 'pages/home.php';
}

include 'includes/footer.php';
?>
<?php
session_start();
if(!isset($_SESSION['user_id'])) {
    header('Location: ?page=login');
    exit();
}

// Получаем товары из корзины
$stmt = $pdo->prepare("
    SELECT c.*, p.name, p.price 
    FROM cart c 
    JOIN products p ON c.product_id = p.id 
    WHERE c.user_id = ?
");
$stmt->execute([$_SESSION['user_id']]);
$cart_items = $stmt->fetchAll();

// Подсчет суммы
$subtotal = 0;
foreach($cart_items as $item) {
    $subtotal += $item['price'] * $item['quantity'];
}
$shipping = $subtotal >= 100 ? 0 : 10;
$total = $subtotal + $shipping;
?>

<div class="checkout-page">
    <div class="container">
        <h1>FASCO Demo Checkout</h1>

        <div class="checkout-grid">
            <div class="checkout-form">
                <section class="contact-section">
                    <h2>Contact</h2>
                    <p>Have an account? <a href="?page=login">Create Account</a></p>
                    
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" value="<?= $_SESSION['user_email'] ?? '' ?>">
                        <button class="btn-apply">Apply</button>
                    </div>
                </section>

                <section class="delivery-section">
                    <h2>Delivery</h2>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="country">Country / Region</label>
                            <input type="text" id="country" name="country">
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="first_name">First Name</label>
                            <input type="text" id="first_name" name="first_name">
                        </div>
                        <div class="form-group">
                            <label for="last_name">Last Name</label>
                            <input type="text" id="last_name" name="last_name">
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="address">Address</label>
                        <input type="text" id="address" name="address">
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="city">City</label>
                            <input type="text" id="city" name="city">
                        </div>
                        <div class="form-group">
                            <label for="postal">Postal Code</label>
                            <input type="text" id="postal" name="postal">
                        </div>
                    </div>

                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="save_info">
                            Save This Info For Future
                        </label>
                    </div>
                </section>

                <section class="payment-section">
                    <h2>Payment</h2>
                    
                    <div class="payment-method">
                        <label>
                            <input type="radio" name="payment" value="credit" checked>
                            Credit Card
                        </label>
                    </div>

                    <div class="form-group">
                        <label for="card_number">Card Number</label>
                        <input type="text" id="card_number" name="card_number" placeholder="1234 1234 1234 1234">
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="expiry">Expiration Date</label>
                            <input type="text" id="expiry" name="expiry" placeholder="MM/YY">
                        </div>
                        <div class="form-group">
                            <label for="cvv">Security Code</label>
                            <input type="text" id="cvv" name="cvv" placeholder="CVV">
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="card_name">Card Holder Name</label>
                        <input type="text" id="card_name" name="card_name">
                    </div>

                    <div class="form-group">
                        <label>
                            <input type="checkbox" name="save_payment">
                            Save This Info For Future
                        </label>
                    </div>

                    <form action="process-order.php" method="POST">
                        <button type="submit" class="btn-pay">Pay Now</button>
                    </form>
                </section>
            </div>

            <div class="order-summary">
                <div class="summary-card">
                    <?php foreach($cart_items as $item): ?>
                    <div class="order-item">
                        <img src="assets/images/product-<?= $item['product_id'] ?>.jpg" alt="<?= $item['name'] ?>">
                        <div class="item-details">
                            <h4><?= $item['name'] ?></h4>
                            <p class="color"><?= $item['color'] ?? 'Red' ?></p>
                            <p class="price">$<?= number_format($item['price'], 2) ?></p>
                        </div>
                    </div>
                    <?php endforeach; ?>

                    <div class="discount-code">
                        <input type="text" placeholder="Discount code">
                        <button class="btn-apply">Apply</button>
                    </div>

                    <div class="summary-totals">
                        <div class="summary-row">
                            <span>Subtotal</span>
                            <span>$<?= number_format($subtotal, 2) ?></span>
                        </div>
                        <div class="summary-row">
                            <span>Shipping</span>
                            <span>$<?= number_format($shipping, 2) ?></span>
                        </div>
                        <div class="summary-row total">
                            <span>Total</span>
                            <span>$<?= number_format($total, 2) ?></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
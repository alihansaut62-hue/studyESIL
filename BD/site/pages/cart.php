<?php
// Получаем товары из корзины (сессия или база данных)
session_start();
$user_id = $_SESSION['user_id'] ?? null;

if($user_id) {
    $stmt = $pdo->prepare("
        SELECT c.*, p.name, p.price, p.image_url 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = ?
    ");
    $stmt->execute([$user_id]);
    $cart_items = $stmt->fetchAll();
} else {
    // Для неавторизованных пользователей храним в сессии
    $cart_items = $_SESSION['cart'] ?? [];
}

// Подсчет общей суммы
$subtotal = 0;
foreach($cart_items as $item) {
    $subtotal += $item['price'] * $item['quantity'];
}
$shipping = 0; // Бесплатная доставка при заказе > $100
if($subtotal < 100) {
    $shipping = 10;
}
$total = $subtotal + $shipping;
$free_shipping_needed = max(0, 100 - $subtotal);
?>

<div class="cart-page">
    <div class="container">
        <nav class="breadcrumb">
            <a href="?page=home">Home</a> > Your Shopping Cart
        </nav>

        <?php if($free_shipping_needed > 0): ?>
        <div class="free-shipping-progress">
            Buy <strong>$<?= number_format($free_shipping_needed, 2) ?></strong> More And Get <strong>Free Shipping</strong>
        </div>
        <?php endif; ?>

        <div class="cart-content">
            <table class="cart-table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Price</th>
                        <th>Quantity</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach($cart_items as $item): ?>
                    <tr>
                        <td class="product-info">
                            <img src="assets/images/product-<?= $item['product_id'] ?>.jpg" alt="<?= $item['name'] ?>">
                            <div>
                                <h4><?= $item['name'] ?></h4>
                                <p class="color">Color: <?= $item['color'] ?? 'Red' ?></p>
                                <a href="pages/remove-from-cart.php?id=<?= $item['id'] ?>" class="remove">Remove</a>
                            </div>
                        </td>
                        <td class="price">$<?= number_format($item['price'], 2) ?></td>
                        <td class="quantity">
                            <button class="qty-btn minus" data-id="<?= $item['id'] ?>">-</button>
                            <input type="number" value="<?= $item['quantity'] ?>" min="1" max="99" readonly>
                            <button class="qty-btn plus" data-id="<?= $item['id'] ?>">+</button>
                        </td>
                        <td class="total">$<?= number_format($item['price'] * $item['quantity'], 2) ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>

            <div class="cart-sidebar">
                <div class="gift-wrap">
                    <label>
                        <input type="checkbox" name="gift_wrap">
                        For $10.00 Please Wrap The Product
                    </label>
                </div>

                <div class="cart-summary">
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

                <div class="cart-actions">
                    <a href="?page=checkout" class="btn-checkout">Checkout</a>
                    <a href="?page=shop" class="btn-view-cart">View Cart</a>
                </div>
            </div>
        </div>
    </div>
</div>
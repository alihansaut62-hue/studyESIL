<?php
// Получаем товары месяца
$stmt = $pdo->query("SELECT * FROM products WHERE old_price IS NOT NULL LIMIT 4");
$deals = $stmt->fetchAll();

// Получаем новые поступления
$stmt = $pdo->query("SELECT * FROM products ORDER BY created_at DESC LIMIT 4");
$new_arrivals = $stmt->fetchAll();
?>

<div class="hero-section">
    <div class="container">
        <h1>ULTIMATE <span>SALE</span></h1>
        <div class="brands">
            <span>CHANEL</span>
            <span>LOUIS VUITTON</span>
            <span>PRADA</span>
            <span>Calvin Klein</span>
            <span>DENIM</span>
        </div>
    </div>
</div>

<section class="deals-of-month">
    <div class="container">
        <h2>Deals Of The Month</h2>
        <div class="products-grid">
            <?php foreach($deals as $product): ?>
            <div class="product-card">
                <img src="assets/images/product-<?= $product['id'] ?>.jpg" alt="<?= $product['name'] ?>">
                <h3><?= $product['name'] ?></h3>
                <div class="price">
                    <span class="current">$<?= $product['price'] ?></span>
                    <?php if($product['old_price']): ?>
                        <span class="old">$<?= $product['old_price'] ?></span>
                        <span class="discount">30% OFF</span>
                    <?php endif; ?>
                </div>
                <a href="?page=product&id=<?= $product['id'] ?>" class="btn">Shop Now</a>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<section class="new-arrivals">
    <div class="container">
        <h2>New Arrivals</h2>
        <div class="products-grid">
            <?php foreach($new_arrivals as $product): ?>
            <div class="product-card">
                <img src="assets/images/product-<?= $product['id'] ?>.jpg" alt="<?= $product['name'] ?>">
                <h3><?= $product['name'] ?></h3>
                <div class="price">$<?= $product['price'] ?></div>
                <a href="?page=product&id=<?= $product['id'] ?>" class="btn">View Product</a>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<section class="instagram-feed">
    <div class="container">
        <h2>Follow Us On Instagram</h2>
        <div class="instagram-grid">
            <!-- Instagram photos would go here -->
        </div>
    </div>
</section>

<section class="testimonials">
    <div class="container">
        <h2>This Is What Our Customers Say</h2>
        <!-- Testimonials slider -->
    </div>
</section>
<?php
$product_id = $_GET['id'] ?? 1;

// Получаем информацию о товаре
$stmt = $pdo->prepare("SELECT * FROM products WHERE id = ?");
$stmt->execute([$product_id]);
$product = $stmt->fetch();

// Получаем похожие товары
$stmt = $pdo->prepare("SELECT * FROM products WHERE category = ? AND id != ? LIMIT 4");
$stmt->execute([$product['category'], $product_id]);
$related_products = $stmt->fetchAll();

// Получаем отзывы
$stmt = $pdo->prepare("
    SELECT r.*, u.first_name, u.last_name 
    FROM reviews r 
    JOIN users u ON r.user_id = u.id 
    WHERE r.product_id = ?
");
$stmt->execute([$product_id]);
$reviews = $stmt->fetchAll();
?>

<div class="product-details">
    <div class="container">
        <div class="product-info">
            <div class="product-image">
                <img src="assets/images/product-<?= $product['id'] ?>.jpg" alt="<?= $product['name'] ?>">
            </div>
            
            <div class="product-details-info">
                <h1><?= $product['name'] ?></h1>
                
                <div class="price-section">
                    <span class="current-price">$<?= $product['price'] ?></span>
                    <?php if($product['old_price']): ?>
                        <span class="old-price">$<?= $product['old_price'] ?></span>
                    <?php endif; ?>
                </div>
                
                <div class="stock-status">
                    <?php if($product['stock_quantity'] > 0): ?>
                        <p class="in-stock">Only <?= $product['stock_quantity'] ?> item(s) left in stock!</p>
                    <?php else: ?>
                        <p class="out-of-stock">Out of stock</p>
                    <?php endif; ?>
                </div>

                <div class="product-options">
                    <label for="color">Color:</label>
                    <select id="color" name="color">
                        <option value="<?= $product['color'] ?>"><?= $product['color'] ?></option>
                    </select>

                    <label for="size">Size:</label>
                    <select id="size" name="size">
                        <option value="<?= $product['size'] ?>"><?= $product['size'] ?></option>
                    </select>

                    <label for="quantity">Quantity:</label>
                    <input type="number" id="quantity" name="quantity" min="1" max="<?= $product['stock_quantity'] ?>" value="1">
                </div>

                <form action="pages/add-to-cart.php" method="POST">
                    <input type="hidden" name="product_id" value="<?= $product['id'] ?>">
                    <button type="submit" class="btn-add-to-cart" <?= $product['stock_quantity'] <= 0 ? 'disabled' : '' ?>>
                        Add to cart
                    </button>
                </form>

                <div class="brands-section">
                    <h3>Peaky Blinders</h3>
                    <h3>Hugo Boss</h3>
                    <span>$100.00</span>
                </div>
            </div>
        </div>

        <div class="related-products">
            <h2>People Also Loved</h2>
            <div class="products-grid">
                <?php foreach($related_products as $related): ?>
                <div class="related-item">
                    <img src="assets/images/product-<?= $related['id'] ?>.jpg" alt="<?= $related['name'] ?>">
                    <h4><?= $related['name'] ?></h4>
                    <p>$<?= $related['price'] ?></p>
                </div>
                <?php endforeach; ?>
            </div>
        </div>

        <div class="countdown-timer">
            <h3>Hurry, Before It's Too Late!</h3>
            <div class="timer">
                <div class="time-block">02 <span>Days</span></div>
                <div class="time-block">06 <span>Hr</span></div>
                <div class="time-block">05 <span>Mins</span></div>
                <div class="time-block">30 <span>Sec</span></div>
            </div>
        </div>

        <div class="reviews-section">
            <h3>Customer Reviews</h3>
            <?php foreach($reviews as $review): ?>
            <div class="review">
                <div class="reviewer"><?= $review['first_name'] ?> <?= $review['last_name'] ?></div>
                <div class="rating"><?= str_repeat('★', $review['rating']) ?><?= str_repeat('☆', 5 - $review['rating']) ?></div>
                <p><?= $review['comment'] ?></p>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
</div>
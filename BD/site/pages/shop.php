<?php
// Получаем параметры фильтрации
$size = $_GET['size'] ?? '';
$color = $_GET['color'] ?? '';
$price_range = $_GET['price'] ?? '';
$brand = $_GET['brand'] ?? '';
$category = $_GET['category'] ?? '';

// Базовый SQL запрос
$sql = "SELECT * FROM products WHERE 1=1";
$params = [];

if($size) {
    $sql .= " AND size = ?";
    $params[] = $size;
}
if($color) {
    $sql .= " AND color = ?";
    $params[] = $color;
}
if($brand) {
    $sql .= " AND brand = ?";
    $params[] = $brand;
}
if($category) {
    $sql .= " AND category = ?";
    $params[] = $category;
}

$stmt = $pdo->prepare($sql);
$stmt->execute($params);
$products = $stmt->fetchAll();

// Получаем уникальные значения для фильтров
$sizes = $pdo->query("SELECT DISTINCT size FROM products WHERE size IS NOT NULL")->fetchAll();
$colors = $pdo->query("SELECT DISTINCT color FROM products WHERE color IS NOT NULL")->fetchAll();
$brands = $pdo->query("SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL")->fetchAll();
?>

<div class="shop-container">
    <aside class="filters">
        <h3>Filters</h3>
        
        <div class="filter-section">
            <h4>Size</h4>
            <?php foreach($sizes as $s): ?>
            <label>
                <input type="checkbox" name="size" value="<?= $s['size'] ?>">
                <?= $s['size'] ?>
            </label>
            <?php endforeach; ?>
        </div>

        <div class="filter-section">
            <h4>Colors</h4>
            <?php foreach($colors as $c): ?>
            <label>
                <input type="checkbox" name="color" value="<?= $c['color'] ?>">
                <?= $c['color'] ?>
            </label>
            <?php endforeach; ?>
        </div>

        <div class="filter-section">
            <h4>Prices</h4>
            <label><input type="radio" name="price" value="0-50"> $0 – $50</label>
            <label><input type="radio" name="price" value="50-100"> $50 – $100</label>
            <label><input type="radio" name="price" value="100-150"> $100 – $150</label>
            <label><input type="radio" name="price" value="150-200"> $150 – $200</label>
            <label><input type="radio" name="price" value="200-250"> $200 – $250</label>
        </div>

        <div class="filter-section">
            <h4>Brands</h4>
            <?php foreach($brands as $b): ?>
            <label>
                <input type="checkbox" name="brand" value="<?= $b['brand'] ?>">
                <?= $b['brand'] ?>
            </label>
            <?php endforeach; ?>
        </div>
    </aside>

    <main class="products-section">
        <div class="best-selling">
            <h3>Best selling</h3>
            <!-- Best selling products -->
        </div>

        <div class="products-grid">
            <?php foreach($products as $product): ?>
            <div class="product-item">
                <img src="assets/images/product-<?= $product['id'] ?>.jpg" alt="<?= $product['name'] ?>">
                <h4><?= $product['name'] ?></h4>
                <div class="price">
                    <span>$<?= $product['price'] ?></span>
                    <?php if($product['old_price']): ?>
                        <span class="old">$<?= $product['old_price'] ?></span>
                    <?php endif; ?>
                </div>
                <a href="?page=product&id=<?= $product['id'] ?>" class="btn">View Details</a>
            </div>
            <?php endforeach; ?>
        </div>
    </main>
</div>
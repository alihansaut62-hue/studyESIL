<div class="auth-page">
    <div class="auth-container">
        <h1>Forget Password</h1>

        <form action="process-forgot-password.php" method="POST">
            <div class="form-group">
                <label for="first_name">First Name</label>
                <input type="text" id="first_name" name="first_name" required>
            </div>

            <div class="form-group">
                <label for="last_name">Last Name</label>
                <input type="text" id="last_name" name="last_name" required>
            </div>

            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required>
            </div>

            <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone" name="phone" required>
            </div>

            <button type="submit" class="btn-send">Send Confirmation Code</button>
        </form>

        <p class="login-link">
            Already have an account? <a href="?page=login">Login</a>
        </p>

        <p class="terms">
            FASCO Terms & Conditions
        </p>
    </div>
</div>
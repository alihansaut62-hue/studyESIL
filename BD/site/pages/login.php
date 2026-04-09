<div class="auth-page">
    <div class="auth-container">
        <h1>Sign In To FASCO</h1>
        
        <button class="btn-google">
            <img src="assets/images/google-icon.png" alt="Google">
            sign up with Google
        </button>

        <button class="btn-email">
            <span>✉</span> sign up with Email
        </button>

        <div class="divider">OR</div>

        <form action="process-login.php" method="POST">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>

            <button type="submit" class="btn-signin">Sign In</button>
        </form>

        <p class="register-link">
            <a href="?page=signup">Register Now</a>
        </p>

        <p class="forgot-link">
            <a href="?page=forgot-password">Forget Password?</a>
        </p>

        <p class="terms">
            FASCO Terms & Conditions
        </p>
    </div>
</div>
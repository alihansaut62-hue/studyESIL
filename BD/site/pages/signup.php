<div class="auth-page">
    <div class="auth-container">
        <h1>Create Account</h1>
        
        <button class="btn-google">
            <img src="assets/images/google-icon.png" alt="Google">
            Signup with Google
        </button>

        <button class="btn-email">
            <span>✉</span> Sign up with Email
        </button>

        <div class="divider">OR</div>

        <form action="process-signup.php" method="POST">
            <div class="form-row">
                <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input type="text" id="first_name" name="first_name" required>
                </div>

                <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input type="text" id="last_name" name="last_name" required>
                </div>
            </div>

            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required>
            </div>

            <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone" name="phone">
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>

            <div class="form-group">
                <label for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>

            <button type="submit" class="btn-create">Create Account</button>
        </form>

        <p class="login-link">
            Already have an account? <a href="?page=login">Login</a>
        </p>

        <p class="terms">
            FASCO Terms & Conditions
        </p>
    </div>
</div>
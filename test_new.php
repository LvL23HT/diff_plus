<?php
/**
 * User Authentication System - Version 2.0
 * Secure login handler with prepared statements and password hashing
 */

class UserAuth {
    private $db;
    private $session_timeout = 7200;
    private $max_login_attempts = 5;
    
    public function __construct($database) {
        $this->db = $database;
        $this->initSession();
    }
    
    /**
     * Initialize secure session
     */
    private function initSession() {
        if (session_status() == PHP_SESSION_NONE) {
            session_start();
            session_regenerate_id(true);
        }
    }
    
    /**
     * Login user with username and password (secure version)
     */
    public function login($username, $password) {
        // Check login attempts
        if ($this->isAccountLocked($username)) {
            return ['success' => false, 'error' => 'Account temporarily locked'];
        }
        
        $query = "SELECT id, username, password, email FROM users WHERE username = ? LIMIT 1";
        $stmt = $this->db->prepare($query);
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result && $row = $result->fetch_assoc()) {
            if (password_verify($password, $row['password'])) {
                $_SESSION['user_id'] = $row['id'];
                $_SESSION['username'] = $row['username'];
                $_SESSION['email'] = $row['email'];
                $_SESSION['login_time'] = time();
                $this->resetLoginAttempts($username);
                return ['success' => true, 'user' => $row];
            } else {
                $this->incrementLoginAttempts($username);
            }
        }
        return ['success' => false, 'error' => 'Invalid credentials'];
    }
    
    /**
     * Check if user is logged in and session is valid
     */
    public function isLoggedIn() {
        if (!isset($_SESSION['user_id']) || !isset($_SESSION['login_time'])) {
            return false;
        }
        
        // Check session timeout
        if (time() - $_SESSION['login_time'] > $this->session_timeout) {
            $this->logout();
            return false;
        }
        
        return true;
    }
    
    /**
     * Logout current user securely
     */
    public function logout() {
        $_SESSION = array();
        if (ini_get("session.use_cookies")) {
            $params = session_get_cookie_params();
            setcookie(session_name(), '', time() - 42000,
                $params["path"], $params["domain"],
                $params["secure"], $params["httponly"]
            );
        }
        session_destroy();
    }
    
    /**
     * Get current user data
     */
    public function getCurrentUser() {
        if ($this->isLoggedIn()) {
            $id = $_SESSION['user_id'];
            $query = "SELECT id, username, email, created_at FROM users WHERE id = ?";
            $stmt = $this->db->prepare($query);
            $stmt->bind_param("i", $id);
            $stmt->execute();
            $result = $stmt->get_result();
            return $result->fetch_assoc();
        }
        return null;
    }
    
    /**
     * Check if account is locked due to failed attempts
     */
    private function isAccountLocked($username) {
        // Implementation for account locking
        return false; // Placeholder
    }
    
    /**
     * Increment failed login attempts
     */
    private function incrementLoginAttempts($username) {
        // Implementation for tracking attempts
    }
    
    /**
     * Reset login attempts counter
     */
    private function resetLoginAttempts($username) {
        // Implementation for resetting attempts
    }
}

// Usage example with error handling
$auth = new UserAuth($mysqli);

if (isset($_POST['action']) && $_POST['action'] === 'login') {
    $username = filter_input(INPUT_POST, 'username', FILTER_SANITIZE_STRING);
    $password = $_POST['password'];
    
    $result = $auth->login($username, $password);
    
    if ($result['success']) {
        echo json_encode(['status' => 'success', 'message' => 'Login successful!']);
    } else {
        echo json_encode(['status' => 'error', 'message' => $result['error']]);
    }
}
?>

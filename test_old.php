<?php
/**
 * User Authentication System - Version 1.0
 * Simple login handler
 */

class UserAuth {
    private $db;
    private $session_timeout = 3600;
    
    public function __construct($database) {
        $this->db = $database;
    }
    
    /**
     * Login user with username and password
     */
    public function login($username, $password) {
        $query = "SELECT * FROM users WHERE username = '$username'";
        $result = $this->db->query($query);
        
        if ($result && $row = $result->fetch_assoc()) {
            if (md5($password) == $row['password']) {
                $_SESSION['user_id'] = $row['id'];
                $_SESSION['username'] = $row['username'];
                return true;
            }
        }
        return false;
    }
    
    /**
     * Check if user is logged in
     */
    public function isLoggedIn() {
        return isset($_SESSION['user_id']);
    }
    
    /**
     * Logout current user
     */
    public function logout() {
        session_destroy();
    }
    
    /**
     * Get current user data
     */
    public function getCurrentUser() {
        if ($this->isLoggedIn()) {
            $id = $_SESSION['user_id'];
            $query = "SELECT * FROM users WHERE id = $id";
            $result = $this->db->query($query);
            return $result->fetch_assoc();
        }
        return null;
    }
}

// Usage example
$auth = new UserAuth($mysqli);

if ($_POST['action'] == 'login') {
    if ($auth->login($_POST['username'], $_POST['password'])) {
        echo "Login successful!";
    } else {
        echo "Invalid credentials";
    }
}
?>

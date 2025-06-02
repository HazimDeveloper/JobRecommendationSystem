// Main JavaScript file for UiTM Machang Job Recommender

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Auto close alerts after 5 seconds
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Password confirmation validation
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    
    if (passwordField && confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            if (passwordField.value !== confirmPasswordField.value) {
                confirmPasswordField.setCustomValidity("Passwords do not match");
            } else {
                confirmPasswordField.setCustomValidity("");
            }
        });
    }

    // Toggle job posting visibility
    const toggleButtons = document.querySelectorAll('.toggle-job-btn');
    
    if (toggleButtons) {
        toggleButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Show confirmation dialog
                if (confirm('Are you sure you want to change the status of this job posting?')) {
                    window.location.href = button.getAttribute('href');
                }
            });
        });
    }

    // Application status update confirmation
    const statusForms = document.querySelectorAll('.status-update-form');
    
    if (statusForms) {
        statusForms.forEach(function(form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Show confirmation dialog
                if (confirm('Are you sure you want to update this application status?')) {
                    form.submit();
                }
            });
        });
    }

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation styles
    (function() {
        'use strict';
        
        // Fetch all forms we want to apply custom validation styles to
        var forms = document.querySelectorAll('.needs-validation');
        
        // Loop over them and prevent submission
        Array.prototype.slice.call(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    })();
});
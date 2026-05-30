document.addEventListener("DOMContentLoaded", () => {
    const emailInput = document.getElementById("id_username");

    if (emailInput) {
        emailInput.focus();
    }

    // Toggle password visibility
    const toggleBtn = document.getElementById('togglePwdBtn');
    const pwdInput = document.querySelector('input[type="password"], input[type="text"][name$="password"]');
    const eyeIcon = document.getElementById('eyeIcon');
    if (toggleBtn && pwdInput && eyeIcon) {
        toggleBtn.addEventListener('click', function() {
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
                eyeIcon.name = 'eye-off-outline';
            } else {
                pwdInput.type = 'password';
                eyeIcon.name = 'eye-outline';
            }
        });
    }
});


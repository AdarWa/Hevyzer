const addBtn = document.getElementById('addEmailBtn');
const emailInput = document.getElementById('newEmail');
const emailList = document.getElementById('emailList');

// Regex for email validation
const emailRegex = /^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*)")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9]{2}|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9]{2}|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/i;

addBtn.addEventListener('click', () => {
    const email = emailInput.value.trim();
    if (!email) return;

    // Validate email
    if (!emailRegex.test(email)) {
        alert('Invalid email address');
        return;
    }

    // Prevent duplicate emails
    const existingEmails = Array.from(emailList.querySelectorAll('input[type=hidden]')).map(i => i.value);
    if (existingEmails.includes(email)) {
        alert('Email already added');
        return;
    }

    // create tag
    const span = document.createElement('span');
    span.classList.add('email-tag');
    span.innerHTML = `${email}<span class="remove-btn">&times;</span>`;
    emailList.appendChild(span);

    // create hidden input for form submission
    const hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = 'emails';
    hidden.value = email;
    emailList.appendChild(hidden);

    emailInput.value = '';
});

// remove email tag
emailList.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-btn')) {
        const inputs = emailList.querySelectorAll('input[type=hidden]');
        if (inputs.length <= 1) {
            alert('At least one email is required');
            return;
        }

        const tag = e.target.parentElement;
        const value = tag.textContent.slice(0, -1); // remove ×
        tag.remove();

        // remove corresponding hidden input
        inputs.forEach(input => {
            if (input.value === value) input.remove();
        });
    }
});

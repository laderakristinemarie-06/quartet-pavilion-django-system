document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signupForm');

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault(); 
            
            const nameInput = this.querySelector('input[name="name"]');
            const nameValue = nameInput ? nameInput.value.trim() : "";
            
            this.innerHTML = `
                <div style="animation: fadeIn 0.5s ease; width: 100%;">
                    <p style="margin-bottom: 10px; font-family: 'Montserrat', sans-serif; font-weight: 600; color: #1c2b1f;">
                        Any comment?
                    </p>
                    <textarea id="userMessage" name="message" placeholder="Write your message here..." 
                        style="width: 100%; height: 80px; padding: 10px; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 10px; display: block; font-family: 'Montserrat', sans-serif;"></textarea>
                    <button type="button" id="finalBtn" class="btn-signup">Send Message</button>
                </div>
            `;

            document.getElementById('finalBtn').onclick = async function() {
                const messageValue = document.getElementById('userMessage').value;
                this.textContent = "Sending...";
                this.disabled = true;

                try {
                    const response = await fetch("https://formspree.io/f/mreoyeog", {
                        method: 'POST',
                        body: JSON.stringify({ name: nameValue || "Anonymous", message: messageValue }),
                        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }
                    });

                    if (response.ok) {
                        form.innerHTML = `<p style="color: #1c2b1f; font-weight: bold;"> Message sent! Thank you.</p>`;
                    } else {
                        alert("Try again.");
                    }
                } catch (error) {
                    alert("Network error.");
                }
            };
        });
    }
});
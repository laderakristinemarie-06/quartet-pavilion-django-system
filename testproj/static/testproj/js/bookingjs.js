// booking-logic.js

document.addEventListener('DOMContentLoaded', () => {
    const bookingForm = document.getElementById('mainBookingForm');
    const bookingCard = document.getElementById('bookingCard');
    const successMessage = document.getElementById('successMessage');
    
    const pavilionSelect = document.getElementById('pavilionType');
    const priceDisplay = document.getElementById('totalPriceDisplay');
    const nameInput = document.getElementById('custName');
    const displayUser = document.getElementById('displayUser');

    // Philippine Pavilion Rates
    const rates = {
        garden: 15000,
        grand: 35000,
        executive: 8500
    };

    // Update price estimate in real-time
    pavilionSelect.addEventListener('change', () => {
        const selectedValue = pavilionSelect.value;
        const price = rates[selectedValue] || 0;
        
        // Format to Philippine Peso Currency
        priceDisplay.innerText = "₱ " + price.toLocaleString('en-PH', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    });

    // Handle form submission
    bookingForm.addEventListener('submit', (e) => {
        e.preventDefault(); // Stop the page from reloading

        // Set the customer name in the Thank You message
        displayUser.innerText = nameInput.value;

        // Hide form, Show success message
        bookingCard.style.display = 'none';
        successMessage.style.display = 'block';

        // Scroll to top to see the message
        window.scrollTo(0, 0);
    });
});
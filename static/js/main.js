document.addEventListener('DOMContentLoaded', function() {
    // Flash message auto-hide (backup if CSS fails)
    setTimeout(() => {
        const flashes = document.querySelectorAll('.flash');
        flashes.forEach(f => {
            f.style.display = 'none';
        });
    }, 3000);

    // Active nav link highlight
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Room filtering on available_rooms.html
    const filterButtons = document.querySelectorAll('.filter-btn');
    if (filterButtons.length > 0) {
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const type = btn.dataset.type;
                const cards = document.querySelectorAll('.room-card');
                
                cards.forEach(card => {
                    if (type === 'all' || card.dataset.type === type) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    // Live Total Calculator on book_room.html
    const checkIn = document.getElementById('check_in');
    const checkOut = document.getElementById('check_out');
    const totalDisplay = document.getElementById('total_amount_display');
    const pricePerNight = parseFloat(document.getElementById('price_per_night')?.value || 0);

    if (checkIn && checkOut) {
        // Set min dates
        const today = new Date().toISOString().split('T')[0];
        checkIn.min = today;
        
        checkIn.addEventListener('change', () => {
            const nextDay = new Date(checkIn.value);
            nextDay.setDate(nextDay.getDate() + 1);
            checkOut.min = nextDay.toISOString().split('T')[0];
            calculateTotal();
        });

        checkOut.addEventListener('change', calculateTotal);
    }

    function calculateTotal() {
        if (checkIn.value && checkOut.value) {
            const start = new Date(checkIn.value);
            const end = new Date(checkOut.value);
            const diffTime = Math.abs(end - start);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays > 0) {
                const total = diffDays * pricePerNight;
                totalDisplay.innerText = `${diffDays} nights × ₹${pricePerNight} = ₹${total}`;
            } else {
                totalDisplay.innerText = "Select valid dates";
            }
        }
    }

    // Confirm dialogs
    const deleteBtns = document.querySelectorAll('.confirm-delete');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to proceed with this deletion?')) {
                e.preventDefault();
            }
        });
    });

    const cancelBtns = document.querySelectorAll('.confirm-cancel');
    cancelBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to cancel this booking?')) {
                e.preventDefault();
            }
        });
    });
});

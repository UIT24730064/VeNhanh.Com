<script>
const PRICE_NORMAL = {{ showtime.price }};
const PRICE_VIP = {{ showtime.price + 20000 }};
let selected = [];

document.querySelectorAll('.seat').forEach(seat => {
    seat.addEventListener('click', () => {
        seat.classList.toggle('selected');

        const code = seat.dataset.seat;
        if (selected.includes(code)) {
            selected = selected.filter(s => s !== code);
        } else {
            selected.push(code);
        }
        update();
    });
});

function update() {
    let total = 0;
    document.querySelectorAll('.seat.selected').forEach(s => {
        total += s.classList.contains('vip') ? PRICE_VIP : PRICE_NORMAL;
    });

    document.getElementById('seats').value = selected.join(',');
    document.getElementById('selectedSeats').innerText = selected.join(', ') || '---';
    document.getElementById('total').innerText = total.toLocaleString('vi-VN');
    document.getElementById('submitBtn').disabled = selected.length === 0;
}
</script>
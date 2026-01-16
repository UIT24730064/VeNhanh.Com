const socket = io();
fetch('/updatesocketsid', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({sid: socket.id})
   });
const SHOWTIME_ID = "{{ showtime.id }}";
let selectedSeats = new Map(); // Dùng Map để quản lý mã ghế và giá tiền

// Đồng bộ SID ngay khi kết nối để tránh lỗi "Ghế không hợp lệ"
socket.on("connect", () => {
    fetch("/update_socket_sid", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sid: socket.id })
    });
});

/* 1. XỬ LÝ KHI CLICK GHẾ */
document.querySelectorAll(".seat").forEach(seat => {
    seat.addEventListener("click", () => {
        const code = seat.dataset.code;

        // Nếu ghế đã bán hoặc người khác đang giữ thì không làm gì
        if (seat.classList.contains("occupied") || seat.classList.contains("holding")) return;

        if (seat.classList.contains("selected")) {
            socket.emit("release_seat", { showtime_id: SHOWTIME_ID, seat_code: code });
        } else {
            socket.emit("hold_seat", { showtime_id: SHOWTIME_ID, seat_code: code });
        }
    });
});

/* 2. CHỈ KHI SERVER XÁC NHẬN RIÊNG CHO BẠN MỚI HIỆN MÀU ĐỎ */
socket.on("hold_success", data => {
    const seat = document.querySelector(`[data-code="${data.seat_code}"]`);
    if (seat) {
        seat.className = "seat selected"; // Màu đỏ của bạn
        selectedSeats.set(data.seat_code, parseInt(seat.dataset.price));
        updateUI();
    }
});

/* 3. CẬP NHẬT TRẠNG THÁI TỪ NGƯỜI KHÁC HOẶC HỆ THỐNG */
socket.on("seat_update", data => {
    const seat = document.querySelector(`[data-code="${data.seat_code}"]`);
    if (!seat) return;

    if (data.status === "holding") {
        // Chỉ hiện màu vàng nếu mình KHÔNG phải là người giữ ghế đó
        if (!selectedSeats.has(data.seat_code)) {
            seat.className = "seat holding";
        }
    } else if (data.status === "available") {
        seat.className = "seat available";
        selectedSeats.delete(data.seat_code);
    } else if (data.status === "booked") {
        seat.className = "seat occupied";
        selectedSeats.delete(data.seat_code);
    }
    updateUI();
});

socket.on("connect", () => {
    fetch("/save_socket_sid", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sid: socket.id })
    });
});

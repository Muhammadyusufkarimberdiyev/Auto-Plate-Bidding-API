document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const plate_id = urlParams.get('plate_id');
    document.getElementById('plate_id').value = plate_id;
});

document.getElementById('bid-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = "index.html";
        return;
    }

    const plate_id = document.getElementById('plate_id').value;
    const amount = document.getElementById('amount').value;

    const response = await fetch(`http://127.0.0.1:8000/bid/${plate_id}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ amount })
    });

    if (response.ok) {
        alert("Taklif muvaffaqiyatli yuborildi!");
        window.location.href = "plates.html";
    } else {
        alert("Xatolik yuz berdi!");
    }
});

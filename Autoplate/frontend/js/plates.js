document.addEventListener('DOMContentLoaded', async function() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = "index.html";
    }

    const response = await fetch('http://127.0.0.1:8000/plates/', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
    });

    const plates = await response.json();
    const container = document.getElementById('plates-container');

    plates.forEach(plate => {
        const card = document.createElement('div');
        card.className = "col-md-4 mb-3";
        card.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${plate.plate_number}</h5>
                    <p class="card-text">${plate.description}</p>
                    <p><strong>Joriy eng yuqori taklif:</strong> $${plate.highest_bid || "Hali yo'q"}</p>
                    <a href="bid.html?plate_id=${plate.id}" class="btn btn-primary">Taklif berish</a>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const stocksData = JSON.parse(document.getElementById('stocksData').textContent);

    stocksData.forEach(stock => {
        const canvas = document.getElementById(`chart-${stock.symbol}`);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            const sortedHistory = stock.history.dates
                .map((date, index) => ({ date, price: stock.history.prices[index] }))
                .sort((a, b) => new Date(a.date) - new Date(b.date));
            const last7DaysHistory = sortedHistory.slice(-7);

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: last7DaysHistory.map(item => item.date),
                    datasets: [{
                        label: 'Closing Price',
                        data: last7DaysHistory.map(item => item.price),
                        borderColor: 'rgba(0, 0, 0, 1)',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: {
                        x: {
                            title: {
                                display: true, 
                                text: 'Date'   
                            },
                            ticks: {
                                display: false 
                            }
                        },
                        y: {
                            title: {
                                display: true, 
                                text: 'Price ($)' 
                            }
                        }
                    }
                }
            });
        }
    });

    const searchInput = document.getElementById('searchInput');
    const sectorFilter = document.getElementById('sectorFilter');
    const stockTableBody = document.getElementById('stockTableBody');

    function filterStocks() {
        const searchValue = searchInput.value.toLowerCase();
        const sectorValue = sectorFilter.value;

        Array.from(stockTableBody.children).forEach(row => {
            const symbol = row.getAttribute('data-symbol').toLowerCase();
            const name = row.getAttribute('data-name').toLowerCase();
            const sector = row.getAttribute('data-sector');

            const matchesSearch = symbol.includes(searchValue) || name.includes(searchValue);
            const matchesSector = !sectorValue || sector === sectorValue;

            row.style.display = matchesSearch && matchesSector ? '' : 'none';
        });
    }

    searchInput.addEventListener('input', filterStocks);
    sectorFilter.addEventListener('change', filterStocks);

    async function showDetails(symbol) {
        try {
            const response = await fetch(`/stock-details/${symbol}/`);
            const data = await response.json();

            if (response.ok) {
                document.getElementById('stockDetailsTitle').innerText = `${symbol} - ${data.name}`;
                document.getElementById('stockDetailsBody').innerHTML = `
                    <p>Sector: ${data.sector}</p>
                    <p>Market Cap: $${data.market_cap}</p>
                    <p>52-Week High: $${data.high_52_week}</p>
                    <p>52-Week Low: $${data.low_52_week}</p>
                    <p>Daily Volume: ${data.volume}</p>`;
                new bootstrap.Modal(document.getElementById('stockDetailsModal')).show();
            } else {
                alert(data.error || "Failed to fetch stock details.");
            }
        } catch {
            alert("Error fetching stock details.");
        }
    }

    async function toggleFavorite(symbol) {
        try {
            const response = await fetch(`/toggle-favorite/${symbol}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
            });
            const data = await response.json();

            if (response.ok) {
                alert(data.success);
                const button = document.querySelector(`button.favorite-btn[data-symbol="${symbol}"]`);
                if (button) {
                    const isFavorite = button.innerText === 'Favorite';
                    button.innerText = isFavorite ? 'Unfavorite' : 'Favorite';
                }
            } else {
                alert(data.error || "Failed to toggle favorite.");
            }
        } catch {
            alert("Error toggling favorite.");
        }
    }

    window.showDetails = showDetails;
    window.toggleFavorite = toggleFavorite;
});

let currentPrice = 0;

function showSellNowModal(symbol, quantity, value) {
    currentPrice = value / quantity;
    document.getElementById('sellNowSymbol').value = symbol;
    document.getElementById('sellQuantity').value = '';
    const modal = new bootstrap.Modal(document.getElementById('sellNowModal'));
    modal.show();
}

async function submitSellNow() {
    const symbol = document.getElementById('sellNowSymbol').value;
    const quantity = parseInt(document.getElementById('sellQuantity').value);

    if (!quantity || quantity <= 0) {
        alert("Please enter a valid quantity.");
        return;
    }

    try {
        const response = await fetch(`/sell-now/${symbol}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.success || "Stock sold successfully.");
            location.reload();
        } else {
            alert(data.error || "An error occurred while selling the stock.");
        }
    } catch (error) {
        console.error("Error during Sell Now request:", error);
        alert("Failed to sell the stock. Please try again.");
    }
}

function showWaitSellModal(symbol) {
    document.getElementById('waitSellSymbol').value = symbol;
    const modal = new bootstrap.Modal(document.getElementById('waitSellModal'));
    modal.show();
}

async function submitWaitSell() {
    const symbol = document.getElementById('waitSellSymbol').value;
    const targetPrice = parseFloat(document.getElementById('targetPrice').value);

    if (!targetPrice || targetPrice <= 0) {
        alert("Please enter a valid target price.");
        return;
    }

    try {
        const response = await fetch(`/wait-and-sell/${symbol}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ target_price: targetPrice })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.success || "Target price set successfully.");
            location.reload();
        } else {
            alert(data.error || "An error occurred while setting the target price.");
        }
    } catch (error) {
        console.error("Error during Wait and Sell request:", error);
        alert("Failed to set the target price. Please try again.");
    }
}

async function cancelPendingSell(sellId) {
    if (!confirm("Are you sure you want to cancel this pending sell?")) {
        return;
    }

    try {
        const response = await fetch(`/cancel-pending-sell/${sellId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            alert("Pending sell has been canceled.");
            location.reload();
        } else {
            const data = await response.json();
            alert(data.error || "Failed to cancel the pending sell.");
        }
    } catch (error) {
        console.error("Error during cancel pending sell request:", error);
        alert("Failed to cancel the pending sell. Please try again.");
    }
}

document.getElementById('updateStocksButton').addEventListener('click', async () => {
    const statusElement = document.getElementById('updateStatus');
    const spinner = document.getElementById('loadingSpinner');

    spinner.style.display = 'inline-block';
    statusElement.style.display = 'none';

    try {
        const response = await fetch('/stock-admin/update-stocks/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        });

        if (response.ok) {
            const data = await response.json();
            statusElement.textContent = `Updated stocks: ${data.updated_stocks.join(', ')}`;
            statusElement.style.color = 'green';
        } else {
            statusElement.textContent = 'Failed to update stock prices.';
            statusElement.style.color = 'red';
        }
    } catch (error) {
        console.error('Error updating stocks:', error);
        statusElement.textContent = 'Error occurred during update.';
        statusElement.style.color = 'red';
    } finally {
        spinner.style.display = 'none';
        statusElement.style.display = 'block';
    }
});

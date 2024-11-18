document.addEventListener('DOMContentLoaded', () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    async function toggleFavorite(symbol) {
        try {
            const response = await fetch(`/toggle-favorite/${symbol}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.success);

                const row = document.querySelector(`[data-symbol="${symbol}"]`);
                if (data.success.includes('removed')) {
                    if (row) row.remove();

                    const tableBody = document.getElementById('favoritesTableBody');
                    if (!tableBody.children.length) {
                        const container = document.querySelector('.container');
                        container.innerHTML = `
                            <h1 class="text-center">Favorites</h1>
                            <p class="text-center mt-5">No favorites added yet.</p>
                        `;
                    }
                }
            } else {
                alert(data.error || 'Failed to toggle favorite.');
            }
        } catch (error) {
            alert('Error toggling favorite.');
            console.error(error);
        }
    }

    window.toggleFavorite = toggleFavorite;
});

function getCSRFToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    // Fallback for meta tag if input is not found (though input is more common for Django forms)
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.content;
    }
    console.warn('CSRF token not found. Make sure you have a csrfmiddlewaretoken input or a csrf-token meta tag.');
    return '';
}

function updateSelection(itemId, itemType, isChecked) {
    const url = '/update_selection/'; // The URL for the new Django view
    const csrfToken = getCSRFToken();

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            item_id: itemId,
            item_type: itemType,
            is_checked: isChecked,
        }),
    })
    .then(response => {
        if (!response.ok) {
            // Try to get error message from response if possible
            return response.json().then(errData => {
                throw new Error(errData.error || `Server responded with status: ${response.status}`);
            }).catch(() => {
                // If response is not JSON or no specific error message
                throw new Error(`Server responded with status: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Selection updated successfully:', data);
            // Optional: Add user feedback here, e.g., a small toast notification
        } else {
            console.error('Failed to update selection:', data.error);
        }
    })
    .catch(error => {
        console.error('Error updating selection:', error);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', (event) => {
            const itemId = event.target.dataset.itemId;
            const itemType = event.target.dataset.itemType;
            const isChecked = event.target.checked;

            if (!itemId || !itemType) {
                console.error('Missing data-item-id or data-item-type on checkbox:', event.target);
                return;
            }

            updateSelection(itemId, itemType, isChecked);
        });
    });
});

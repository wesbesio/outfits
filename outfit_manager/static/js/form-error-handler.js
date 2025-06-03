// File: static/js/form-error-handler.js
// Revision: 1.0 - Basic HTMX global error handler

document.addEventListener('DOMContentLoaded', () => {
    const errorToast = document.getElementById('global-error-toast');
    const errorMessageElement = document.getElementById('global-error-message');

    if (!errorToast || !errorMessageElement) {
        console.warn('Global error display elements not found in the DOM.');
        return;
    }

    document.body.addEventListener('htmx:responseError', function(event) {
        console.error("HTMX Response Error:", event.detail.xhr);
        
        let message = `Error: ${event.detail.xhr.status} - ${event.detail.xhr.statusText}`;
        
        // Try to get a more specific error message if the server sends one in a known format
        // For example, if the server returns JSON with an "error" or "detail" key
        try {
            const responseJson = JSON.parse(event.detail.xhr.responseText);
            if (responseJson && responseJson.detail) {
                message = `Server Error: ${responseJson.detail}`;
            } else if (responseJson && responseJson.error) {
                 message = `Server Error: ${responseJson.error}`;
            }
        } catch (e) {
            // Response was not JSON or JSON parsing failed, stick to the generic message
            // If responseText is HTML and it's an error page, it might be too long for a toast.
            // For now, we'll keep it simple.
            if (event.detail.xhr.responseText && event.detail.xhr.responseText.length < 200 && !event.detail.xhr.responseText.trim().startsWith("<!DOCTYPE html>")) {
                // If it's a short text response, show it. Avoid showing full HTML pages.
                message = event.detail.xhr.responseText;
            }
        }
        
        errorMessageElement.textContent = message;
        errorToast.style.display = 'flex'; // Show the toast

        // Optional: auto-hide after some time
        // setTimeout(() => {
        //     errorToast.style.display = 'none';
        // }, 7000);
    });

    document.body.addEventListener('htmx:sendError', function(event) {
        console.error("HTMX Send Error (e.g., network issue):", event.detail.error);
        errorMessageElement.textContent = 'Network error or issue sending request. Please check your connection.';
        errorToast.style.display = 'flex';
    });

    // Example of how to manually trigger an error for testing:
    // htmx.trigger(document.body, 'htmx:responseError', { error: 'Test error', xhr: { status: 500, statusText: 'Internal Server Error', responseText: 'A test error occurred.'}});
});

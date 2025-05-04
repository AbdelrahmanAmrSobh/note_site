export async function fetchWithAuth(url, options = {}) {
    try {
        let response = await fetch(url, {
            ...options,
            credentials: 'include' // always include cookies
        });

        // If not unauthorized, return the response
        if (response.status !== 401) {
            return response;
        }

        // Unauthorized? Try refreshing token
        console.log('Access token expired, trying to refresh...');

        const refreshResponse = await fetch('http://localhost:8000/auth/refresh-tokens', {
            method: 'POST',
            credentials: 'include',
        });

        if (!refreshResponse.ok) {
            // Refresh failed, logout
            console.error('Token refresh failed');
            throw new Error('Token refresh failed');
        }

        // Token refreshed, retry original request
        console.log('Token refreshed, retrying original request...');
        response = await fetch(url, {
            ...options,
            credentials: 'include'
        });
        return response;

    } catch (error) {
        console.error('fetchWithAuth error:', error);
        throw error;
    }
}
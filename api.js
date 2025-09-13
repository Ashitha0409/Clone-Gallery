// API Service for CloneGallery
class APIService {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.token = localStorage.getItem('auth_token');
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    // Clear authentication token
    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    // Get headers with authentication
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Get headers for file uploads
    getUploadHeaders() {
        const headers = {};
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Make API request
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                if (response.status === 401) {
                    this.clearToken();
                    throw new Error('Authentication required');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Authentication endpoints
    async login(email, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username: email, password }),
        });
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        
        return response;
    }

    async register(userData) {
        const response = await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
        
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        
        return response;
    }

    async getCurrentUser() {
        return await this.request('/auth/me');
    }

    // Image endpoints
    async uploadImage(file, metadata) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', metadata.title);
        formData.append('caption', metadata.caption || '');
        formData.append('alt_text', metadata.alt_text || '');
        formData.append('privacy', metadata.privacy || 'public');
        formData.append('tags', metadata.tags ? metadata.tags.join(',') : '');

        const url = `${this.baseURL}/upload/image`;
        const config = {
            method: 'POST',
            headers: this.getUploadHeaders(),
            body: formData,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                if (response.status === 401) {
                    this.clearToken();
                    throw new Error('Authentication required');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Image upload failed:', error);
            throw error;
        }
    }

    async getImages(page = 1, limit = 20, userId = null, privacy = null) {
        const params = new URLSearchParams({
            page: page.toString(),
            limit: limit.toString(),
        });
        
        if (userId) params.append('user_id', userId);
        if (privacy) params.append('privacy', privacy);

        return await this.request(`/images?${params.toString()}`);
    }

    async getImage(imageId) {
        return await this.request(`/images/${imageId}`);
    }

    async getUserImages(userId, page = 1, limit = 20) {
        return await this.getImages(page, limit, userId);
    }

    // AI Generation endpoints
    async generateImage(prompt, options = {}) {
        const requestData = {
            prompt,
            width: options.width || 512,
            height: options.height || 512,
            num_inference_steps: options.steps || 25,
            guidance_scale: options.guidance || 7.5,
            negative_prompt: options.negative_prompt || '',
            seed: options.seed || null,
            model: options.model || 'stable-diffusion-v1-5',
        };

        return await this.request('/generate/image', {
            method: 'POST',
            body: JSON.stringify(requestData),
        });
    }

    // Health check
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    // Get models status
    async getModelsStatus() {
        return await this.request('/models/status');
    }
}

// Create global API instance
window.apiService = new APIService();



// CloneGallery Application JavaScript

// Application State
let currentUser = null;
let currentPage = 'dashboard';
let appData = {
    users: [],
    images: [],
    albums: [],
    tags: [],
    analytics: {},
    userLikes: new Set() // Track which images the current user has liked
};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    
    // Load sample data
    loadSampleData();
    
    // Initialize app
    setTimeout(() => {
        console.log('Transitioning to login screen...');
        hideLoadingScreen();
        showLoginScreen();
        setupEventListeners();
        setupThemeToggle();
    }, 1500);
});

// Load Sample Data
function loadSampleData() {
    appData = {
        "users": [
            {
                "id": "admin-001",
                "email": "admin@clonegallery.local",
                "name": "Gallery Admin",
                "role": "Admin",
                "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face",
                "joined": "2024-01-15",
                "uploads": 45,
                "views": 12500
            },
            {
                "id": "editor-001", 
                "email": "editor@clonegallery.local",
                "name": "Creative Editor",
                "role": "Editor",
                "avatar": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
                "joined": "2024-02-20",
                "uploads": 28,
                "views": 8200
            },
            {
                "id": "visitor-001",
                "email": "user@clonegallery.local", 
                "name": "Gallery Visitor",
                "role": "Visitor",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
                "joined": "2024-03-10",
                "uploads": 0,
                "views": 350
            }
        ],
        "images": [
            {
                "id": "img-001",
                "title": "Mountain Lake Sunset",
                "caption": "Beautiful alpine lake reflecting golden sunset colors with snow-capped mountains in the background",
                "alt_text": "Alpine lake at sunset with mountain reflection",
                "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=200&fit=crop",
                "uploader": "admin-001",
                "uploaded_at": "2024-09-10T14:30:00Z",
                "tags": ["nature", "landscape", "sunset", "mountains", "lake"],
                "privacy": "public",
                "likes": 24,
                "views": 156,
                "is_ai_generated": false,
                "width": 1920,
                "height": 1280,
                "size": "2.4 MB",
                "format": "JPEG"
            },
            {
                "id": "img-002",
                "title": "Urban Architecture Dreams", 
                "caption": "Modern glass skyscraper with geometric patterns and reflective surfaces creating abstract art",
                "alt_text": "Modern glass building with geometric reflections",
                "url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=300&h=200&fit=crop",
                "uploader": "editor-001",
                "uploaded_at": "2024-09-09T16:45:00Z",
                "tags": ["architecture", "urban", "modern", "glass", "reflection"],
                "privacy": "public",
                "likes": 31,
                "views": 203,
                "is_ai_generated": false,
                "width": 1920,
                "height": 1280,
                "size": "3.1 MB",
                "format": "JPEG"
            },
            {
                "id": "img-003",
                "title": "AI Generated Forest", 
                "caption": "Mystical forest scene generated with Stable Diffusion featuring ethereal lighting and fantasy elements",
                "alt_text": "AI-generated mystical forest with magical lighting",
                "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=300&h=200&fit=crop",
                "uploader": "admin-001",
                "uploaded_at": "2024-09-08T10:20:00Z",
                "tags": ["AI", "forest", "mystical", "fantasy", "generated"],
                "privacy": "public",
                "likes": 67,
                "views": 342,
                "is_ai_generated": true,
                "generation_meta": {
                    "model": "Stable Diffusion v1.5",
                    "prompt": "mystical forest with ethereal lighting, fantasy art style, detailed, atmospheric",
                    "steps": 25,
                    "guidance": 7.5
                },
                "width": 1024,
                "height": 1024,
                "size": "1.8 MB",
                "format": "PNG"
            },
            {
                "id": "img-004",
                "title": "Ocean Waves Macro",
                "caption": "Close-up view of ocean waves creating abstract patterns with foam and bubbles",
                "alt_text": "Macro photography of ocean wave foam patterns",
                "url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&h=600&fit=crop", 
                "thumbnail": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=300&h=200&fit=crop",
                "uploader": "editor-001",
                "uploaded_at": "2024-09-07T08:15:00Z",
                "tags": ["ocean", "waves", "macro", "abstract", "water"],
                "privacy": "public",
                "likes": 18,
                "views": 89,
                "is_ai_generated": false,
                "width": 1920,
                "height": 1280,
                "size": "2.8 MB",
                "format": "JPEG"
            },
            {
                "id": "img-005",
                "title": "Desert Dunes Landscape",
                "caption": "Golden sand dunes creating flowing patterns under dramatic lighting conditions",
                "alt_text": "Desert sand dunes with dramatic shadows and lighting",
                "url": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=300&h=200&fit=crop",
                "uploader": "admin-001",
                "uploaded_at": "2024-09-06T12:00:00Z",
                "tags": ["desert", "dunes", "landscape", "sand", "golden"],
                "privacy": "public",
                "likes": 42,
                "views": 178,
                "is_ai_generated": false,
                "width": 1920,
                "height": 1280,
                "size": "2.2 MB",
                "format": "JPEG"
            }
        ],
        "albums": [
            {
                "id": "album-001",
                "title": "Nature Collection",
                "description": "Curated collection of stunning nature photography from around the world",
                "cover_image": "img-001",
                "created_by": "admin-001",
                "created_at": "2024-09-01T10:00:00Z",
                "privacy": "public",
                "image_count": 3,
                "images": ["img-001", "img-004", "img-005"]
            },
            {
                "id": "album-002", 
                "title": "AI Experiments",
                "description": "Generated artwork and AI-assisted creative explorations",
                "cover_image": "img-003",
                "created_by": "admin-001",
                "created_at": "2024-09-02T14:30:00Z",
                "privacy": "public",
                "image_count": 1,
                "images": ["img-003"]
            },
            {
                "id": "album-003",
                "title": "Urban Photography",
                "description": "Architecture and city life captured in stunning detail",
                "cover_image": "img-002", 
                "created_by": "editor-001",
                "created_at": "2024-09-03T16:20:00Z",
                "privacy": "public",
                "image_count": 1,
                "images": ["img-002"]
            }
        ],
        "tags": [
            {"name": "nature", "count": 124, "trending": true},
            {"name": "landscape", "count": 89, "trending": true}, 
            {"name": "architecture", "count": 67, "trending": false},
            {"name": "AI", "count": 45, "trending": true},
            {"name": "urban", "count": 56, "trending": false},
            {"name": "abstract", "count": 34, "trending": false},
            {"name": "mountains", "count": 78, "trending": true},
            {"name": "ocean", "count": 92, "trending": false}
        ],
        "analytics": {
            "total_images": 1247,
            "total_users": 156, 
            "total_views": 45680,
            "total_likes": 8934,
            "storage_used": "12.4 GB",
            "ai_generated": 234,
            "processing_queue": 3
        }
    };
}

// Screen Management
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'none';
        console.log('Loading screen hidden');
    }
}

function showLoginScreen() {
    const loginScreen = document.getElementById('login-screen');
    if (loginScreen) {
        loginScreen.classList.remove('hidden');
        loginScreen.style.display = 'flex';
        console.log('Login screen shown');
    }
}

function hideLoginScreen() {
    const loginScreen = document.getElementById('login-screen');
    if (loginScreen) {
        loginScreen.classList.add('hidden');
        loginScreen.style.display = 'none';
    }
}

function showMainApp() {
    const mainApp = document.getElementById('main-app');
    if (mainApp) {
        mainApp.classList.remove('hidden');
        mainApp.style.display = 'block';
    }
}

function hideMainApp() {
    const mainApp = document.getElementById('main-app');
    if (mainApp) {
        mainApp.classList.add('hidden');
        mainApp.style.display = 'none';
    }
}

// Authentication
async function handleLogin(email, password) {
    try {
        const response = await apiService.login(email, password);
        
        if (response.access_token) {
            // Get user info
            const userInfo = await apiService.getCurrentUser();
            currentUser = userInfo;
            
            hideLoginScreen();
            showMainApp();
            initializeUserSession();
            showToast('Login successful!', 'success');
            return true;
        } else {
            showToast('Invalid credentials', 'error');
            return false;
        }
    } catch (error) {
        console.error('Login failed:', error);
        showToast('Login failed: ' + error.message, 'error');
        return false;
    }
}

async function handleRegister(userData) {
    try {
        const response = await apiService.register(userData);
        
        if (response.access_token) {
            // Get user info
            const userInfo = await apiService.getCurrentUser();
            currentUser = userInfo;
            
            hideLoginScreen();
            showMainApp();
            initializeUserSession();
            showToast('Account created successfully!', 'success');
            return true;
        } else {
            showToast('Registration failed', 'error');
            return false;
        }
    } catch (error) {
        console.error('Registration failed:', error);
        showToast('Registration failed: ' + error.message, 'error');
        return false;
    }
}

async function handleDemoLogin(role) {
    try {
        // Use demo credentials based on role
        let email, password;
        switch(role) {
            case 'admin':
                email = 'admin@clonegallery.local';
                password = 'admin123';
                break;
            case 'editor':
                email = 'editor@clonegallery.local';
                password = 'editor123';
                break;
            case 'visitor':
                email = 'user@clonegallery.local';
                password = 'user123';
                break;
        }
        
        const success = await handleLogin(email, password);
        if (success) {
            showToast(`Logged in as ${currentUser.role}`, 'success');
        }
    } catch (error) {
        console.error('Demo login failed:', error);
        showToast('Demo login failed', 'error');
    }
}

function initializeUserSession() {
    // Set user info in UI
    const userAvatar = document.getElementById('user-avatar');
    const dropdownAvatar = document.getElementById('dropdown-avatar');
    const dropdownName = document.getElementById('dropdown-name');
    const dropdownRole = document.getElementById('dropdown-role');
    
    if (userAvatar) userAvatar.src = currentUser.avatar;
    if (dropdownAvatar) dropdownAvatar.src = currentUser.avatar;
    if (dropdownName) dropdownName.textContent = currentUser.name;
    if (dropdownRole) dropdownRole.textContent = currentUser.role;
    
    // Apply role-based styling
    document.body.className = `user-${currentUser.role.toLowerCase()}`;
    
    // Initialize dashboard
    navigateToPage('dashboard');
    updateDashboardStats();
    loadRecentImages();
    loadPopularImages();
    
    // Setup role-based features
    setupRoleBasedFeatures();
}

function setupRoleBasedFeatures() {
    const adminElements = document.querySelectorAll('.admin-only');
    const isAdmin = currentUser && currentUser.role === 'Admin';
    
    adminElements.forEach(element => {
        if (isAdmin) {
            element.style.display = element.classList.contains('nav-item') ? 'flex' : 'block';
        } else {
            element.style.display = 'none';
        }
    });
}

function handleLogout() {
    apiService.clearToken();
    currentUser = null;
    document.body.className = '';
    hideMainApp();
    showLoginScreen();
    showToast('Logged out successfully', 'info');
}

// Event Listeners Setup
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            handleLogin(email, password);
        });
    }
    
    // Register form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('reg-name').value;
            const username = document.getElementById('reg-username').value;
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('reg-confirm-password').value;
            
            // Validate passwords match
            if (password !== confirmPassword) {
                showToast('Passwords do not match', 'error');
                return;
            }
            
            // Validate password length
            if (password.length < 8) {
                showToast('Password must be at least 8 characters long', 'error');
                return;
            }
            
            const userData = {
                name: name,
                username: username,
                email: email,
                password: password,
                role: 'Visitor'
            };
            
            handleRegister(userData);
        });
    }
    
    // Auth mode toggle
    const authModeSwitch = document.getElementById('auth-mode-switch');
    const authModeText = document.getElementById('auth-mode-text');
    const authTitle = document.getElementById('auth-title');
    const loginFormEl = document.getElementById('login-form');
    const registerFormEl = document.getElementById('register-form');
    
    if (authModeSwitch) {
        authModeSwitch.addEventListener('click', function() {
            const isLoginMode = !loginFormEl.classList.contains('hidden');
            
            if (isLoginMode) {
                // Switch to register mode
                loginFormEl.classList.add('hidden');
                registerFormEl.classList.remove('hidden');
                authTitle.textContent = 'Create Account';
                authModeText.textContent = 'Already have an account?';
                this.textContent = 'Sign In';
            } else {
                // Switch to login mode
                registerFormEl.classList.add('hidden');
                loginFormEl.classList.remove('hidden');
                authTitle.textContent = 'Sign In';
                authModeText.textContent = 'Don\'t have an account?';
                this.textContent = 'Create Account';
            }
        });
    }
    
    // Demo login buttons
    document.querySelectorAll('[data-role]').forEach(button => {
        button.addEventListener('click', function() {
            console.log('Demo login clicked:', this.dataset.role);
            handleDemoLogin(this.dataset.role);
        });
    });
    
    // Navigation
    document.querySelectorAll('[data-page]').forEach(element => {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            navigateToPage(this.dataset.page);
        });
    });
    
    // User menu
    const userMenuBtn = document.getElementById('user-menu-btn');
    if (userMenuBtn) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = document.getElementById('user-dropdown');
            if (dropdown) {
                dropdown.classList.toggle('hidden');
            }
        });
    }
    
    // Close user menu when clicking outside
    document.addEventListener('click', function() {
        const dropdown = document.getElementById('user-dropdown');
        if (dropdown) {
            dropdown.classList.add('hidden');
        }
    });
    
    // Logout
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Search
    const mainSearch = document.getElementById('main-search');
    if (mainSearch) {
        mainSearch.addEventListener('input', handleMainSearch);
    }
    
    const advancedSearchBtn = document.getElementById('advanced-search-btn');
    if (advancedSearchBtn) {
        advancedSearchBtn.addEventListener('click', handleAdvancedSearch);
    }
    
    // Upload
    setupUploadHandlers();
    
    // Gallery
    setupGalleryHandlers();
    
    // Modal
    setupModalHandlers();
    
    // AI Generation
    setupAIGenerationHandlers();
    
    // Albums
    setupAlbumHandlers();
    
    // Image Editor
    setupImageEditorHandlers();
}

// Navigation
function navigateToPage(pageId) {
    console.log('Navigating to page:', pageId);
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageId) {
            item.classList.add('active');
        }
    });
    
    // Show/hide pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    const targetPage = document.getElementById(pageId + '-page');
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    currentPage = pageId;
    
    // Load page-specific content
    switch(pageId) {
        case 'gallery':
            loadGalleryImages();
            loadGalleryFilters();
            break;
        case 'albums':
            loadAlbums();
            break;
        case 'admin':
            loadAdminData();
            break;
        case 'search':
            setupSearchPage();
            break;
    }
}

// Dashboard Functions
async function updateDashboardStats() {
    try {
        // Get user's images to calculate stats
        const userImages = await apiService.getUserImages(currentUser.id, 1, 1000);
        
        const totalImages = userImages.total || 0;
        const totalViews = userImages.images.reduce((sum, img) => sum + img.views, 0);
        const totalLikes = 0; // TODO: Implement likes system
        const storageUsed = userImages.images.reduce((sum, img) => sum + (img.size_bytes || 0), 0);
        
        const totalImagesEl = document.getElementById('total-images');
        const totalViewsEl = document.getElementById('total-views');
        const totalLikesEl = document.getElementById('total-likes');
        const storageUsedEl = document.getElementById('storage-used');
        
        if (totalImagesEl) totalImagesEl.textContent = totalImages.toLocaleString();
        if (totalViewsEl) totalViewsEl.textContent = totalViews.toLocaleString();
        if (totalLikesEl) totalLikesEl.textContent = totalLikes.toLocaleString();
        if (storageUsedEl) storageUsedEl.textContent = formatBytes(storageUsed);
    } catch (error) {
        console.error('Failed to update dashboard stats:', error);
        // Fallback to static values
        const totalImages = document.getElementById('total-images');
        const totalViews = document.getElementById('total-views');
        const totalLikes = document.getElementById('total-likes');
        const storageUsed = document.getElementById('storage-used');
        
        if (totalImages) totalImages.textContent = '0';
        if (totalViews) totalViews.textContent = '0';
        if (totalLikes) totalLikes.textContent = '0';
        if (storageUsed) storageUsed.textContent = '0 B';
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function loadRecentImages() {
    try {
        const userImages = await apiService.getUserImages(currentUser.id, 1, 6);
        const recentImages = userImages.images || [];
        
        const container = document.getElementById('recent-images');
        if (container) {
            if (recentImages.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: var(--color-text-secondary);">No images uploaded yet</p>';
            } else {
                container.innerHTML = recentImages.map(image => createImageCard(image, true)).join('');
                
                // Add click handlers
                container.querySelectorAll('.image-card').forEach(card => {
                    card.addEventListener('click', function() {
                        openImageModal(this.dataset.imageId);
                    });
                });
            }
        }
    } catch (error) {
        console.error('Failed to load recent images:', error);
        const container = document.getElementById('recent-images');
        if (container) {
            container.innerHTML = '<p style="text-align: center; color: var(--color-text-secondary);">Failed to load images</p>';
        }
    }
}

async function loadPopularImages() {
    try {
        const allImages = await apiService.getImages(1, 100);
        const popularImages = allImages.images
            .sort((a, b) => b.views - a.views)
            .slice(0, 6);
        
        const container = document.getElementById('popular-images');
        if (container) {
            if (popularImages.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: var(--color-text-secondary);">No images available</p>';
            } else {
                container.innerHTML = popularImages.map(image => createImageCard(image, true)).join('');
                
                // Add click handlers
                container.querySelectorAll('.image-card').forEach(card => {
                    card.addEventListener('click', function() {
                        openImageModal(this.dataset.imageId);
                    });
                });
            }
        }
    } catch (error) {
        console.error('Failed to load popular images:', error);
        const container = document.getElementById('popular-images');
        if (container) {
            container.innerHTML = '<p style="text-align: center; color: var(--color-text-secondary);">Failed to load images</p>';
        }
    }
}

// Gallery Functions
async function loadGalleryImages(filters = {}) {
    try {
        const response = await apiService.getImages(1, 100);
        let images = response.images || [];
        
        // Apply filters
        if (filters.tags && filters.tags.length > 0) {
            images = images.filter(img => 
                filters.tags.some(tag => img.tags.includes(tag))
            );
        }
        
        if (filters.sort) {
            switch(filters.sort) {
                case 'newest':
                    images.sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at));
                    break;
                case 'oldest':
                    images.sort((a, b) => new Date(a.uploaded_at) - new Date(b.uploaded_at));
                    break;
                case 'popular':
                    images.sort((a, b) => b.views - a.views);
                    break;
                case 'views':
                    images.sort((a, b) => b.views - a.views);
                    break;
            }
        }
        
        const container = document.getElementById('gallery-container');
        if (container) {
            if (images.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: var(--color-text-secondary); padding: var(--space-32);">No images found</p>';
            } else {
                container.innerHTML = images.map(image => createImageCard(image)).join('');
                
                // Add click handlers
                container.querySelectorAll('.image-card').forEach(card => {
                    card.addEventListener('click', function() {
                        openImageModal(this.dataset.imageId);
                    });
                });
            }
        }
    } catch (error) {
        console.error('Failed to load gallery images:', error);
        const container = document.getElementById('gallery-container');
        if (container) {
            container.innerHTML = '<p style="text-align: center; color: var(--color-text-secondary); padding: var(--space-32);">Failed to load images</p>';
        }
    }
}

function loadGalleryFilters() {
    const container = document.getElementById('filter-tags');
    if (!container) return;
    
    const allTags = appData.tags.slice(0, 10); // Show top 10 tags
    
    container.innerHTML = allTags.map(tag => 
        `<button class="tag-filter" data-tag="${tag.name}">
            ${tag.name} (${tag.count})
        </button>`
    ).join('');
    
    // Add click handlers
    container.querySelectorAll('.tag-filter').forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('active');
            updateGalleryWithFilters();
        });
    });
}

function updateGalleryWithFilters() {
    const activeTags = Array.from(document.querySelectorAll('.tag-filter.active'))
        .map(button => button.dataset.tag);
    
    const gallerySort = document.getElementById('gallery-sort');
    const sortValue = gallerySort ? gallerySort.value : 'newest';
    
    loadGalleryImages({
        tags: activeTags,
        sort: sortValue
    });
}

function setupGalleryHandlers() {
    // Sort handler
    const gallerySort = document.getElementById('gallery-sort');
    if (gallerySort) {
        gallerySort.addEventListener('change', updateGalleryWithFilters);
    }
    
    // View mode handlers
    document.querySelectorAll('.view-mode').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.view-mode').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const container = document.getElementById('gallery-container');
            if (container) {
                if (this.dataset.view === 'list') {
                    container.classList.add('list-view');
                } else {
                    container.classList.remove('list-view');
                }
            }
        });
    });
}

// Image Card Creation
function createImageCard(image, compact = false) {
    const uploadDate = new Date(image.uploaded_at).toLocaleDateString();
    
    return `
        <div class="image-card" data-image-id="${image.id}">
            <img src="${image.thumbnail}" alt="${image.alt_text || image.title}" loading="lazy">
            <div class="image-card-content">
                <h3 class="image-card-title">${image.title}</h3>
                ${!compact ? `<p class="image-card-caption">${(image.caption || '').substring(0, 80)}${(image.caption || '').length > 80 ? '...' : ''}</p>` : ''}
                <div class="image-card-meta">
                    <span>By ${image.uploader_id}</span>
                    <span>${uploadDate}</span>
                </div>
                <div class="image-stats">
                    <span><i class="fas fa-eye"></i> ${image.views}</span>
                </div>
                ${image.is_ai_generated ? '<div class="ai-badge"><i class="fas fa-robot"></i> AI Generated</div>' : ''}
                <div class="image-tags">
                    ${(image.tags || []).slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            </div>
        </div>
    `;
}

// Upload Functions
function setupUploadHandlers() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    const fileSelectBtn = document.getElementById('file-select-btn');
    
    if (!uploadZone || !fileInput || !fileSelectBtn) return;
    
    // File select button
    fileSelectBtn.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', function() {
        handleFiles(Array.from(this.files));
    });
    
    // Drag and drop
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', function() {
        this.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files).filter(file => 
            file.type.startsWith('image/')
        );
        
        handleFiles(files);
    });
}

function handleFiles(files) {
    if (files.length === 0) return;
    
    files.forEach(file => {
        if (validateFile(file)) {
            createUploadItem(file);
            simulateUpload(file);
        }
    });
}

function validateFile(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (!validTypes.includes(file.type)) {
        showToast(`Invalid file type: ${file.name}`, 'error');
        return false;
    }
    
    if (file.size > maxSize) {
        showToast(`File too large: ${file.name}`, 'error');
        return false;
    }
    
    return true;
}

function createUploadItem(file) {
    const queue = document.getElementById('upload-queue');
    if (!queue) return;
    
    const itemId = 'upload-' + Date.now();
    
    const uploadItem = document.createElement('div');
    uploadItem.className = 'upload-item';
    uploadItem.id = itemId;
    
    uploadItem.innerHTML = `
        <div class="upload-item-header">
            <div class="upload-item-info">
                <div class="upload-item-name">${file.name}</div>
                <div class="upload-item-size">${formatFileSize(file.size)}</div>
            </div>
            <div class="upload-item-actions">
                <button class="btn btn--outline btn--sm" onclick="openImageEditor(this.closest('.upload-item').dataset.file)">
                    <i class="fas fa-edit"></i> Edit
                </button>
            </div>
            <div class="status">Uploading...</div>
        </div>
        <div class="upload-progress">
            <div class="upload-progress-bar" style="width: 0%"></div>
        </div>
        <div class="upload-metadata">
            <div class="form-group">
                <label class="form-label">Title</label>
                <input type="text" class="form-control" value="${file.name.replace(/\.[^/.]+$/, '')}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Tags</label>
                <input type="text" class="form-control" placeholder="nature, landscape, photography...">
            </div>
            <div class="form-group">
                <label class="form-label">Caption</label>
                <textarea class="form-control" rows="3" placeholder="Describe your image..."></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Privacy</label>
                <select class="form-control">
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                </select>
            </div>
        </div>
    `;
    
    // Store file reference for editing
    uploadItem.dataset.file = file;
    
    queue.appendChild(uploadItem);
    
    // Start real upload
    setTimeout(() => uploadImageToAPI(itemId, file), 100);
}

async function uploadImageToAPI(itemId, file) {
    const progressBar = document.querySelector(`#${itemId} .upload-progress-bar`);
    const status = document.querySelector(`#${itemId} .status`);
    
    if (!progressBar || !status) return;
    
    try {
        // Get metadata from form
        const titleInput = document.querySelector(`#${itemId} input[type="text"]`);
        const captionInput = document.querySelector(`#${itemId} textarea`);
        const tagsInput = document.querySelector(`#${itemId} input[placeholder*="tags"]`);
        const privacySelect = document.querySelector(`#${itemId} select`);
        
        const metadata = {
            title: titleInput ? titleInput.value : file.name.replace(/\.[^/.]+$/, ''),
            caption: captionInput ? captionInput.value : '',
            alt_text: '',
            privacy: privacySelect ? privacySelect.value : 'public',
            tags: tagsInput ? tagsInput.value.split(',').map(tag => tag.trim()).filter(tag => tag) : []
        };
        
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 90) {
                progress = 90;
                clearInterval(progressInterval);
            }
            progressBar.style.width = progress + '%';
        }, 100);
        
        status.textContent = 'Uploading...';
        
        // Upload to API
        const uploadedImage = await apiService.uploadImage(file, metadata);
        
        // Complete progress
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        status.textContent = 'Complete!';
        status.style.color = 'var(--color-success)';
        
        showToast('Image uploaded successfully!', 'success');
        
        // Refresh dashboard and gallery if on those pages
        if (currentPage === 'dashboard') {
            await updateDashboardStats();
            await loadRecentImages();
        } else if (currentPage === 'gallery') {
            await loadGalleryImages();
        }
        
    } catch (error) {
        console.error('Upload failed:', error);
        status.textContent = 'Failed!';
        status.style.color = 'var(--color-error)';
        showToast('Upload failed: ' + error.message, 'error');
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Search Functions
function handleMainSearch(e) {
    const query = e.target.value.toLowerCase();
    
    if (query.length < 2) {
        hideSuggestions();
        return;
    }
    
    const suggestions = generateSearchSuggestions(query);
    showSuggestions(suggestions);
}

function generateSearchSuggestions(query) {
    const suggestions = [];
    
    // Search in image titles
    appData.images.forEach(image => {
        if (image.title.toLowerCase().includes(query)) {
            suggestions.push({
                type: 'image',
                text: image.title,
                id: image.id
            });
        }
    });
    
    // Search in tags
    appData.tags.forEach(tag => {
        if (tag.name.toLowerCase().includes(query)) {
            suggestions.push({
                type: 'tag',
                text: tag.name,
                count: tag.count
            });
        }
    });
    
    // Search in users
    appData.users.forEach(user => {
        if (user.name.toLowerCase().includes(query)) {
            suggestions.push({
                type: 'user',
                text: user.name,
                id: user.id
            });
        }
    });
    
    return suggestions.slice(0, 8);
}

function showSuggestions(suggestions) {
    const container = document.getElementById('search-suggestions');
    if (!container) return;
    
    if (suggestions.length === 0) {
        hideSuggestions();
        return;
    }
    
    container.innerHTML = suggestions.map(suggestion => {
        let icon = '';
        let subtitle = '';
        
        switch(suggestion.type) {
            case 'image':
                icon = '<i class="fas fa-image"></i>';
                break;
            case 'tag':
                icon = '<i class="fas fa-tag"></i>';
                subtitle = `${suggestion.count} images`;
                break;
            case 'user':
                icon = '<i class="fas fa-user"></i>';
                break;
        }
        
        return `
            <div class="suggestion-item" data-type="${suggestion.type}" data-value="${suggestion.text}">
                ${icon} ${suggestion.text}
                ${subtitle ? `<small>${subtitle}</small>` : ''}
            </div>
        `;
    }).join('');
    
    container.style.display = 'block';
    
    // Add click handlers
    container.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', function() {
            const mainSearch = document.getElementById('main-search');
            if (mainSearch) {
                mainSearch.value = this.dataset.value;
            }
            hideSuggestions();
            performSearch(this.dataset.value);
        });
    });
}

function hideSuggestions() {
    const container = document.getElementById('search-suggestions');
    if (container) {
        container.style.display = 'none';
    }
}

function performSearch(query) {
    navigateToPage('search');
    const advancedSearchInput = document.getElementById('advanced-search-input');
    if (advancedSearchInput) {
        advancedSearchInput.value = query;
    }
    handleAdvancedSearch();
}

function setupSearchPage() {
    // Populate uploader filter
    const uploaderFilter = document.getElementById('uploader-filter');
    if (uploaderFilter) {
        uploaderFilter.innerHTML = '<option value="">All Users</option>' +
            appData.users.map(user => `<option value="${user.id}">${user.name}</option>`).join('');
    }
    
    // Setup similarity search
    const similarityBtn = document.getElementById('similarity-btn');
    const similarityInput = document.getElementById('similarity-input');
    
    if (similarityBtn && similarityInput) {
        similarityBtn.addEventListener('click', function() {
            similarityInput.click();
        });
        
        similarityInput.addEventListener('change', function() {
            if (this.files[0]) {
                simulateSimilaritySearch(this.files[0]);
            }
        });
    }
}

function handleAdvancedSearch() {
    const searchInput = document.getElementById('advanced-search-input');
    const query = searchInput ? searchInput.value : '';
    
    const tagFilter = document.getElementById('tag-filter');
    const tagFilterValue = tagFilter ? tagFilter.value : '';
    
    const uploaderFilter = document.getElementById('uploader-filter');
    const uploaderFilterValue = uploaderFilter ? uploaderFilter.value : '';
    
    const aiFilter = document.getElementById('ai-filter');
    const aiFilterValue = aiFilter ? aiFilter.value : '';
    
    let results = [...appData.images];
    
    // Apply filters
    if (query) {
        results = results.filter(img => 
            img.title.toLowerCase().includes(query.toLowerCase()) ||
            img.caption.toLowerCase().includes(query.toLowerCase()) ||
            img.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
        );
    }
    
    if (tagFilterValue) {
        const tags = tagFilterValue.split(',').map(tag => tag.trim().toLowerCase());
        results = results.filter(img => 
            tags.some(tag => img.tags.some(imgTag => imgTag.toLowerCase().includes(tag)))
        );
    }
    
    if (uploaderFilterValue) {
        results = results.filter(img => img.uploader === uploaderFilterValue);
    }
    
    if (aiFilterValue === 'true') {
        results = results.filter(img => img.is_ai_generated);
    } else if (aiFilterValue === 'false') {
        results = results.filter(img => !img.is_ai_generated);
    }
    
    displaySearchResults(results, query);
}

function displaySearchResults(results, query) {
    const container = document.getElementById('search-results');
    if (!container) return;
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="search-empty" style="text-align: center; padding: var(--space-32); color: var(--color-text-secondary);">
                <i class="fas fa-search" style="font-size: 3rem; margin-bottom: var(--space-16);"></i>
                <h3>No results found</h3>
                <p>Try adjusting your search criteria</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="search-header" style="margin-bottom: var(--space-24);">
            <h3>Search Results</h3>
            <p style="color: var(--color-text-secondary);">Found ${results.length} images${query ? ` for "${query}"` : ''}</p>
        </div>
        <div class="search-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-20);">
            ${results.map(image => createImageCard(image)).join('')}
        </div>
    `;
    
    // Add click handlers
    container.querySelectorAll('.image-card').forEach(card => {
        card.addEventListener('click', function() {
            openImageModal(this.dataset.imageId);
        });
    });
}

function simulateSimilaritySearch(file) {
    showToast('Analyzing image for similarity search...', 'info');
    
    setTimeout(() => {
        // Simulate AI similarity results
        const similarImages = appData.images.slice(1, 4); // Mock similar images
        displaySimilarityResults(similarImages);
        showToast('Similarity search complete!', 'success');
    }, 3000);
}

function displaySimilarityResults(results) {
    const container = document.getElementById('search-results');
    if (!container) return;
    
    container.innerHTML = `
        <div class="search-header" style="margin-bottom: var(--space-24);">
            <h3>Similar Images</h3>
            <p style="color: var(--color-text-secondary);">AI-powered similarity search results</p>
        </div>
        <div class="search-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-20);">
            ${results.map((image, index) => {
                const similarity = (95 - index * 5).toFixed(1);
                return `
                    <div style="position: relative;">
                        ${createImageCard(image)}
                        <div class="similarity-score" style="position: absolute; top: var(--space-8); right: var(--space-8); background: var(--color-surface); padding: var(--space-4) var(--space-8); border-radius: var(--radius-sm); font-size: var(--font-size-xs); font-weight: var(--font-weight-medium);">
                            ${similarity}% similar
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    // Add click handlers
    container.querySelectorAll('.image-card').forEach(card => {
        card.addEventListener('click', function() {
            openImageModal(this.dataset.imageId);
        });
    });
}

// Albums Functions
function loadAlbums() {
    const container = document.getElementById('albums-container');
    if (!container) return;
    
    container.innerHTML = appData.albums.map(album => {
        const coverImage = appData.images.find(img => img.id === album.cover_image);
        const creator = appData.users.find(u => u.id === album.created_by);
        
        return `
            <div class="album-card" data-album-id="${album.id}">
                <div class="album-cover">
                    <img src="${coverImage ? coverImage.thumbnail : 'https://via.placeholder.com/300x200?text=No+Cover'}" alt="${album.title}">
                </div>
                <div class="album-info">
                    <h3 class="album-title">${album.title}</h3>
                    <p class="album-description">${album.description}</p>
                    <div class="album-meta">
                        <span>${album.image_count} images</span>
                        <span>By ${creator ? creator.name : 'Unknown'}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // Add click handlers
    container.querySelectorAll('.album-card').forEach(card => {
        card.addEventListener('click', function() {
            openAlbumModal(this.dataset.albumId);
        });
    });
}

function setupAlbumHandlers() {
    const createAlbumBtn = document.getElementById('create-album-btn');
    if (createAlbumBtn) {
        createAlbumBtn.addEventListener('click', function() {
            showCreateAlbumModal();
        });
    }
}

function showCreateAlbumModal() {
    showToast('Album creation feature coming soon!', 'info');
}

function openAlbumModal(albumId) {
    const album = appData.albums.find(a => a.id === albumId);
    if (!album) return;
    
    const albumImages = album.images.map(imgId => 
        appData.images.find(img => img.id === imgId)
    ).filter(Boolean);
    
    showToast(`Viewing album: ${album.title} (${albumImages.length} images)`, 'info');
}

// AI Generation Functions
function setupAIGenerationHandlers() {
    const stepsSlider = document.getElementById('ai-steps');
    const guidanceSlider = document.getElementById('ai-guidance');
    const generateBtn = document.getElementById('generate-btn');
    
    if (stepsSlider) {
        stepsSlider.addEventListener('input', function() {
            const stepsValue = document.getElementById('steps-value');
            if (stepsValue) {
                stepsValue.textContent = this.value;
            }
        });
    }
    
    if (guidanceSlider) {
        guidanceSlider.addEventListener('input', function() {
            const guidanceValue = document.getElementById('guidance-value');
            if (guidanceValue) {
                guidanceValue.textContent = this.value;
            }
        });
    }
    
    if (generateBtn) {
        generateBtn.addEventListener('click', handleAIGeneration);
    }
}

function handleAIGeneration() {
    const promptInput = document.getElementById('ai-prompt');
    const prompt = promptInput ? promptInput.value : '';
    
    if (!prompt.trim()) {
        showToast('Please enter a prompt', 'error');
        return;
    }
    
    const modelSelect = document.getElementById('ai-model');
    const stepsInput = document.getElementById('ai-steps');
    const guidanceInput = document.getElementById('ai-guidance');
    
    const model = modelSelect ? modelSelect.value : 'sd-1.5';
    const steps = stepsInput ? stepsInput.value : '25';
    const guidance = guidanceInput ? guidanceInput.value : '7.5';
    
    simulateAIGeneration(prompt, model, steps, guidance);
}

async function simulateAIGeneration(prompt, model, steps, guidance) {
    const resultsContainer = document.getElementById('generation-results');
    const generateBtn = document.getElementById('generate-btn');
    
    if (!resultsContainer || !generateBtn) return;
    
    // Show loading state
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    
    resultsContainer.innerHTML = `
        <div class="generation-status">
            <div class="loading-spinner" style="margin: 0 auto var(--space-16) auto;"></div>
            <h3>Generating Image</h3>
            <p>This may take a few moments...</p>
            <div class="generation-progress" style="width: 100%; height: 6px; background: var(--color-secondary); border-radius: var(--radius-full); overflow: hidden; margin-top: var(--space-16);">
                <div class="generation-progress-bar" style="height: 100%; background: var(--color-primary); transition: width var(--duration-fast) var(--ease-standard); width: 0%;"></div>
            </div>
        </div>
    `;
    
    try {
        // Call the actual AI generation API
        const response = await apiService.generateImage(prompt, {
            width: 512,
            height: 512,
            steps: parseInt(steps),
            guidance: parseFloat(guidance),
            model: model
        });
        
        // Show the generated image
        showGenerationResult(prompt, model, response.image_url);
        
    } catch (error) {
        console.error('AI generation failed:', error);
        
        // Fallback to simulation if API is not available
        showToast('AI service unavailable, using demo mode', 'warning');
        
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(progressInterval);
                
                setTimeout(() => {
                    showGenerationResult(prompt, model);
                    generateBtn.disabled = false;
                    generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Image';
                }, 1000);
            }
            
            const progressBar = document.querySelector('.generation-progress-bar');
            if (progressBar) {
                progressBar.style.width = progress + '%';
            }
        }, 500);
    }
}

function showGenerationResult(prompt, model, generatedImageUrl = null) {
    const resultsContainer = document.getElementById('generation-results');
    const generateBtn = document.getElementById('generate-btn');
    
    if (!resultsContainer) return;
    
    // Reset button state
    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Image';
    }
    
    // Use generated image if available, otherwise fallback to random image
    let imageUrl;
    if (generatedImageUrl) {
        imageUrl = generatedImageUrl;
    } else {
        const randomImage = appData.images[Math.floor(Math.random() * appData.images.length)];
        imageUrl = randomImage.url;
    }
    
    resultsContainer.innerHTML = `
        <div class="generated-image">
            <img src="${imageUrl}" alt="Generated: ${prompt}" style="width: 100%; height: 250px; object-fit: cover; border-radius: var(--radius-base) var(--radius-base) 0 0;">
            <div class="generated-image-info" style="padding: var(--space-16);">
                <h4>Generated Image</h4>
                <p><strong>Prompt:</strong> ${prompt}</p>
                <p><strong>Model:</strong> ${model}</p>
                <div class="generation-actions" style="display: flex; gap: var(--space-8); margin-top: var(--space-16);">
                    <button class="btn btn--primary btn--sm" onclick="saveGeneratedImage('${imageUrl}', '${prompt}', '${model}')">Save to Gallery</button>
                    <button class="btn btn--outline btn--sm" onclick="downloadGeneratedImage('${imageUrl}', '${prompt}')">Download</button>
                </div>
            </div>
        </div>
    `;
    
    showToast('Image generated successfully!', 'success');
}

async function saveGeneratedImage(imageUrl, prompt, model) {
    try {
        // Convert base64 data URL to blob
        const response = await fetch(imageUrl);
        const blob = await response.blob();
        const file = new File([blob], `generated-${Date.now()}.png`, { type: 'image/png' });
        
        // Upload the generated image
        const metadata = {
            title: prompt.substring(0, 50) + (prompt.length > 50 ? '...' : ''),
            caption: `AI Generated: ${prompt}`,
            alt_text: `AI generated image: ${prompt}`,
            privacy: 'public',
            tags: ['AI', 'generated', 'artificial-intelligence']
        };
        
        const uploadedImage = await apiService.uploadImage(file, metadata);
        
        // Refresh gallery if on gallery page
        if (currentPage === 'gallery') {
            await loadGalleryImages();
        }
        
        // Refresh dashboard if on dashboard page
        if (currentPage === 'dashboard') {
            await loadRecentImages();
            await updateDashboardStats();
        }
        
        showToast('Generated image saved to gallery!', 'success');
        
    } catch (error) {
        console.error('Failed to save generated image:', error);
        showToast('Failed to save generated image', 'error');
    }
}

function downloadGeneratedImage(imageUrl, prompt) {
    // Create a temporary link to download the image
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `generated-${prompt.replace(/[^a-zA-Z0-9]/g, '-')}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showToast('Image downloaded!', 'success');
}

// Admin Functions
function loadAdminData() {
    // Update admin stats
    const adminTotalUsers = document.getElementById('admin-total-users');
    const adminProcessingQueue = document.getElementById('admin-processing-queue');
    const adminAiGenerated = document.getElementById('admin-ai-generated');
    
    if (adminTotalUsers) adminTotalUsers.textContent = appData.analytics.total_users;
    if (adminProcessingQueue) adminProcessingQueue.textContent = appData.analytics.processing_queue;
    if (adminAiGenerated) adminAiGenerated.textContent = appData.analytics.ai_generated;
    
    // Load user list
    const userList = document.getElementById('user-list');
    if (userList) {
        userList.innerHTML = appData.users.map(user => `
            <div class="user-item">
                <img src="${user.avatar}" alt="${user.name}">
                <div class="user-item-info">
                    <div class="user-item-name">${user.name}</div>
                    <div class="user-item-email">${user.email}</div>
                </div>
                <div class="user-item-role">${user.role}</div>
                <div class="user-item-stats">
                    <small>${user.uploads} uploads • ${user.views} views</small>
                </div>
            </div>
        `).join('');
    }
}

// Modal Functions
function setupModalHandlers() {
    const modal = document.getElementById('image-modal');
    const closeBtn = document.getElementById('modal-close');
    const backdrop = document.querySelector('.modal-backdrop');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeImageModal);
    }
    
    if (backdrop) {
        backdrop.addEventListener('click', closeImageModal);
    }
    
    // ESC key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
            closeImageModal();
        }
    });
    
    // Like button
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', function() {
            const imageId = this.dataset.imageId;
            toggleLike(imageId);
        });
    }
    
    // Download button
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const imageId = this.dataset.imageId;
            downloadImage(imageId);
        });
    }
    
    // Share button
    const shareBtn = document.getElementById('share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function() {
            const imageId = this.dataset.imageId;
            shareImage(imageId);
        });
    }
}

async function openImageModal(imageId) {
    try {
        const image = await apiService.getImage(imageId);
        
        // Update modal content
        const modalImage = document.getElementById('modal-image');
        const modalTitle = document.getElementById('modal-title');
        const modalCaption = document.getElementById('modal-caption');
        const modalUploader = document.getElementById('modal-uploader');
        const modalDate = document.getElementById('modal-date');
        const modalSize = document.getElementById('modal-size');
        const modalViews = document.getElementById('modal-views');
        
        if (modalImage) {
            modalImage.src = image.url;
            modalImage.alt = image.alt_text || image.title;
        }
        if (modalTitle) modalTitle.textContent = image.title;
        if (modalCaption) modalCaption.textContent = image.caption || '';
        if (modalUploader) modalUploader.textContent = image.uploader_id;
        if (modalDate) modalDate.textContent = new Date(image.uploaded_at).toLocaleDateString();
        if (modalSize) modalSize.textContent = formatBytes(image.size_bytes || 0);
        if (modalViews) modalViews.textContent = image.views.toLocaleString();
        
        // Update tags
        const tagsContainer = document.getElementById('modal-tags');
        if (tagsContainer) {
            tagsContainer.innerHTML = (image.tags || []).map(tag => `<span class="tag">${tag}</span>`).join('');
        }
        
        // Update like button (placeholder for now)
        const likeBtn = document.getElementById('like-btn');
        const likeCount = document.getElementById('like-count');
        if (likeBtn) {
            likeBtn.dataset.imageId = imageId;
            likeBtn.classList.remove('liked');
            likeBtn.innerHTML = '<i class="far fa-heart"></i> <span id="like-count">0</span>';
        }
        if (likeCount) likeCount.textContent = '0';
        
        // Show modal
        const modal = document.getElementById('image-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('Failed to load image:', error);
        showToast('Failed to load image details', 'error');
    }
}

function closeImageModal() {
    const modal = document.getElementById('image-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function toggleLike(imageId) {
    const image = appData.images.find(img => img.id === imageId);
    if (!image || !currentUser) return;
    
    const likeKey = `${currentUser.id}-${imageId}`;
    const isLiked = appData.userLikes.has(likeKey);
    
    if (isLiked) {
        // Unlike the image
        appData.userLikes.delete(likeKey);
        image.likes = Math.max(0, image.likes - 1);
        showToast('Image unliked', 'info');
    } else {
        // Like the image
        appData.userLikes.add(likeKey);
        image.likes++;
        showToast('Image liked!', 'success');
    }
    
    // Update UI
    const likeCount = document.getElementById('like-count');
    const likeBtn = document.getElementById('like-btn');
    
    if (likeCount) {
        likeCount.textContent = image.likes;
    }
    
    if (likeBtn) {
        if (appData.userLikes.has(likeKey)) {
            likeBtn.classList.add('liked');
            likeBtn.innerHTML = '<i class="fas fa-heart"></i> <span id="like-count">' + image.likes + '</span>';
        } else {
            likeBtn.classList.remove('liked');
            likeBtn.innerHTML = '<i class="far fa-heart"></i> <span id="like-count">' + image.likes + '</span>';
        }
    }
    
    // Update like count in gallery cards
    updateImageCardLikes(imageId, image.likes);
}

function updateImageCardLikes(imageId, likeCount) {
    // Update like count in all image cards with this ID
    const imageCards = document.querySelectorAll(`[data-image-id="${imageId}"]`);
    imageCards.forEach(card => {
        const statsElement = card.querySelector('.image-stats');
        if (statsElement) {
            const likeElement = statsElement.querySelector('span:first-child');
            if (likeElement) {
                likeElement.innerHTML = `<i class="fas fa-heart"></i> ${likeCount}`;
            }
        }
    });
}

function downloadImage(imageId) {
    const image = appData.images.find(img => img.id === imageId);
    if (!image) return;
    
    // Simulate download
    showToast(`Downloading: ${image.title}`, 'info');
}

function shareImage(imageId) {
    const image = appData.images.find(img => img.id === imageId);
    if (!image) return;
    
    // Copy link to clipboard simulation
    const shareUrl = `${window.location.origin}/image/${imageId}`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(() => {
            showToast('Link copied to clipboard!', 'success');
        });
    } else {
        showToast('Share link: ' + shareUrl, 'info');
    }
}

// Theme Toggle
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    let isDark = false;
    
    themeToggle.addEventListener('click', function() {
        isDark = !isDark;
        
        if (isDark) {
            document.documentElement.setAttribute('data-color-scheme', 'dark');
            this.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            document.documentElement.setAttribute('data-color-scheme', 'light');
            this.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas fa-${getToastIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 4000);
}

function getToastIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'info': return 'info-circle';
        default: return 'info-circle';
    }
}

// Image Editor Functions
let currentEditingFile = null;
let originalImageData = null;
let currentCanvas = null;
let currentCtx = null;

function setupImageEditorHandlers() {
    // Editor modal controls
    const editorClose = document.getElementById('editor-close');
    const editorCancel = document.getElementById('editor-cancel');
    const editorSave = document.getElementById('editor-save');
    
    if (editorClose) {
        editorClose.addEventListener('click', closeImageEditor);
    }
    
    if (editorCancel) {
        editorCancel.addEventListener('click', closeImageEditor);
    }
    
    if (editorSave) {
        editorSave.addEventListener('click', saveEditedImage);
    }
    
    // Tab switching
    document.querySelectorAll('.editor-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            switchEditorTab(this.dataset.tab);
        });
    });
    
    // Crop controls
    const cropApply = document.getElementById('crop-apply');
    const cropReset = document.getElementById('crop-reset');
    
    if (cropApply) {
        cropApply.addEventListener('click', applyCrop);
    }
    
    if (cropReset) {
        cropReset.addEventListener('click', resetCrop);
    }
    
    // Resize controls
    const resizeApply = document.getElementById('resize-apply');
    const resizeReset = document.getElementById('resize-reset');
    const maintainAspect = document.getElementById('maintain-aspect');
    
    if (resizeApply) {
        resizeApply.addEventListener('click', applyResize);
    }
    
    if (resizeReset) {
        resizeReset.addEventListener('click', resetResize);
    }
    
    if (maintainAspect) {
        maintainAspect.addEventListener('change', function() {
            if (this.checked) {
                updateResizeHeight();
            }
        });
    }
    
    // Filter controls
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            applyFilter(this.dataset.filter);
        });
    });
    
    // Adjustment controls
    const brightness = document.getElementById('brightness');
    const contrast = document.getElementById('contrast');
    const saturation = document.getElementById('saturation');
    const adjustApply = document.getElementById('adjust-apply');
    const adjustReset = document.getElementById('adjust-reset');
    
    if (brightness) {
        brightness.addEventListener('input', function() {
            document.getElementById('brightness-value').textContent = this.value;
        });
    }
    
    if (contrast) {
        contrast.addEventListener('input', function() {
            document.getElementById('contrast-value').textContent = this.value;
        });
    }
    
    if (saturation) {
        saturation.addEventListener('input', function() {
            document.getElementById('saturation-value').textContent = this.value;
        });
    }
    
    if (adjustApply) {
        adjustApply.addEventListener('click', applyAdjustments);
    }
    
    if (adjustReset) {
        adjustReset.addEventListener('click', resetAdjustments);
    }
}

function openImageEditor(file) {
    currentEditingFile = file;
    
    // Create image element to load the file
    const img = new Image();
    img.onload = function() {
        // Initialize canvas
        currentCanvas = document.getElementById('editor-canvas');
        currentCtx = currentCanvas.getContext('2d');
        
        // Set canvas size to fit the image
        const maxWidth = 600;
        const maxHeight = 400;
        let { width, height } = calculateAspectRatio(img.width, img.height, maxWidth, maxHeight);
        
        currentCanvas.width = width;
        currentCanvas.height = height;
        
        // Draw image on canvas
        currentCtx.drawImage(img, 0, 0, width, height);
        
        // Store original image data
        originalImageData = currentCtx.getImageData(0, 0, width, height);
        
        // Set initial resize values
        document.getElementById('resize-width').value = img.width;
        document.getElementById('resize-height').value = img.height;
        
        // Show editor modal
        const modal = document.getElementById('image-editor-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    };
    
    img.src = URL.createObjectURL(file);
}

function closeImageEditor() {
    const modal = document.getElementById('image-editor-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
    
    // Reset editor state
    currentEditingFile = null;
    originalImageData = null;
    currentCanvas = null;
    currentCtx = null;
}

function switchEditorTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.editor-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update panels
    document.querySelectorAll('.editor-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`${tabName}-panel`).classList.add('active');
}

function calculateAspectRatio(originalWidth, originalHeight, maxWidth, maxHeight) {
    const aspectRatio = originalWidth / originalHeight;
    
    if (originalWidth <= maxWidth && originalHeight <= maxHeight) {
        return { width: originalWidth, height: originalHeight };
    }
    
    if (maxWidth / maxHeight > aspectRatio) {
        return { width: maxHeight * aspectRatio, height: maxHeight };
    } else {
        return { width: maxWidth, height: maxWidth / aspectRatio };
    }
}

function applyCrop() {
    // Simple crop implementation - in a real app, you'd have interactive crop selection
    showToast('Crop applied!', 'success');
}

function resetCrop() {
    if (originalImageData && currentCtx) {
        currentCtx.putImageData(originalImageData, 0, 0);
        showToast('Crop reset', 'info');
    }
}

function applyResize() {
    const width = parseInt(document.getElementById('resize-width').value);
    const height = parseInt(document.getElementById('resize-height').value);
    
    if (width <= 0 || height <= 0) {
        showToast('Invalid dimensions', 'error');
        return;
    }
    
    if (currentCanvas && currentCtx) {
        // Create temporary canvas for resizing
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        
        tempCanvas.width = width;
        tempCanvas.height = height;
        
        // Draw resized image
        tempCtx.drawImage(currentCanvas, 0, 0, width, height);
        
        // Update main canvas
        currentCanvas.width = width;
        currentCanvas.height = height;
        currentCtx.drawImage(tempCanvas, 0, 0);
        
        showToast('Image resized!', 'success');
    }
}

function resetResize() {
    if (currentEditingFile) {
        const img = new Image();
        img.onload = function() {
            const maxWidth = 600;
            const maxHeight = 400;
            let { width, height } = calculateAspectRatio(img.width, img.height, maxWidth, maxHeight);
            
            currentCanvas.width = width;
            currentCanvas.height = height;
            currentCtx.drawImage(img, 0, 0, width, height);
            
            document.getElementById('resize-width').value = img.width;
            document.getElementById('resize-height').value = img.height;
            
            showToast('Resize reset', 'info');
        };
        img.src = URL.createObjectURL(currentEditingFile);
    }
}

function updateResizeHeight() {
    const width = parseInt(document.getElementById('resize-width').value);
    const height = parseInt(document.getElementById('resize-height').value);
    const aspectRatio = width / height;
    
    if (currentEditingFile) {
        const img = new Image();
        img.onload = function() {
            const newHeight = Math.round(width / (img.width / img.height));
            document.getElementById('resize-height').value = newHeight;
        };
        img.src = URL.createObjectURL(currentEditingFile);
    }
}

function applyFilter(filterName) {
    if (!currentCtx || !originalImageData) return;
    
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-filter="${filterName}"]`).classList.add('active');
    
    // Apply filter
    const imageData = currentCtx.getImageData(0, 0, currentCanvas.width, currentCanvas.height);
    const data = imageData.data;
    
    switch(filterName) {
        case 'grayscale':
            for (let i = 0; i < data.length; i += 4) {
                const gray = data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114;
                data[i] = gray;
                data[i + 1] = gray;
                data[i + 2] = gray;
            }
            break;
        case 'sepia':
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                data[i] = Math.min(255, (r * 0.393) + (g * 0.769) + (b * 0.189));
                data[i + 1] = Math.min(255, (r * 0.349) + (g * 0.686) + (b * 0.168));
                data[i + 2] = Math.min(255, (r * 0.272) + (g * 0.534) + (b * 0.131));
            }
            break;
        case 'vintage':
            for (let i = 0; i < data.length; i += 4) {
                data[i] = Math.min(255, data[i] * 1.1);
                data[i + 1] = Math.min(255, data[i + 1] * 1.0);
                data[i + 2] = Math.min(255, data[i + 2] * 0.9);
            }
            break;
        case 'brightness':
            for (let i = 0; i < data.length; i += 4) {
                data[i] = Math.min(255, data[i] + 30);
                data[i + 1] = Math.min(255, data[i + 1] + 30);
                data[i + 2] = Math.min(255, data[i + 2] + 30);
            }
            break;
        case 'contrast':
            for (let i = 0; i < data.length; i += 4) {
                data[i] = Math.min(255, Math.max(0, (data[i] - 128) * 1.5 + 128));
                data[i + 1] = Math.min(255, Math.max(0, (data[i + 1] - 128) * 1.5 + 128));
                data[i + 2] = Math.min(255, Math.max(0, (data[i + 2] - 128) * 1.5 + 128));
            }
            break;
        case 'none':
            // Reset to original
            currentCtx.putImageData(originalImageData, 0, 0);
            return;
    }
    
    currentCtx.putImageData(imageData, 0, 0);
    showToast(`Filter applied: ${filterName}`, 'success');
}

function applyAdjustments() {
    const brightness = parseInt(document.getElementById('brightness').value);
    const contrast = parseInt(document.getElementById('contrast').value);
    const saturation = parseInt(document.getElementById('saturation').value);
    
    if (!currentCtx || !originalImageData) return;
    
    const imageData = currentCtx.getImageData(0, 0, currentCanvas.width, currentCanvas.height);
    const data = imageData.data;
    
    for (let i = 0; i < data.length; i += 4) {
        // Apply brightness
        data[i] = Math.min(255, Math.max(0, data[i] + brightness));
        data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + brightness));
        data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + brightness));
        
        // Apply contrast
        const contrastFactor = (100 + contrast) / 100;
        data[i] = Math.min(255, Math.max(0, (data[i] - 128) * contrastFactor + 128));
        data[i + 1] = Math.min(255, Math.max(0, (data[i + 1] - 128) * contrastFactor + 128));
        data[i + 2] = Math.min(255, Math.max(0, (data[i + 2] - 128) * contrastFactor + 128));
        
        // Apply saturation
        const gray = data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114;
        const saturationFactor = (100 + saturation) / 100;
        data[i] = Math.min(255, Math.max(0, gray + (data[i] - gray) * saturationFactor));
        data[i + 1] = Math.min(255, Math.max(0, gray + (data[i + 1] - gray) * saturationFactor));
        data[i + 2] = Math.min(255, Math.max(0, gray + (data[i + 2] - gray) * saturationFactor));
    }
    
    currentCtx.putImageData(imageData, 0, 0);
    showToast('Adjustments applied!', 'success');
}

function resetAdjustments() {
    document.getElementById('brightness').value = 0;
    document.getElementById('contrast').value = 0;
    document.getElementById('saturation').value = 0;
    document.getElementById('brightness-value').textContent = '0';
    document.getElementById('contrast-value').textContent = '0';
    document.getElementById('saturation-value').textContent = '0';
    
    if (originalImageData && currentCtx) {
        currentCtx.putImageData(originalImageData, 0, 0);
        showToast('Adjustments reset', 'info');
    }
}

function saveEditedImage() {
    if (!currentCanvas || !currentEditingFile) return;
    
    // Convert canvas to blob
    currentCanvas.toBlob(function(blob) {
        // Create new file with edited image
        const editedFile = new File([blob], currentEditingFile.name, {
            type: currentEditingFile.type,
            lastModified: Date.now()
        });
        
        // Update the upload item with edited file
        updateUploadItemWithEditedFile(editedFile);
        
        showToast('Image edited and saved!', 'success');
        closeImageEditor();
    }, currentEditingFile.type, 0.9);
}

function updateUploadItemWithEditedFile(editedFile) {
    // Find the upload item and update it
    const uploadItems = document.querySelectorAll('.upload-item');
    uploadItems.forEach(item => {
        const fileName = item.querySelector('.upload-item-name').textContent;
        if (fileName === currentEditingFile.name) {
            // Update the file reference (in a real app, you'd update the actual file object)
            item.dataset.editedFile = 'true';
            showToast('File updated with edits', 'success');
        }
    });
}

// Utility Functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}
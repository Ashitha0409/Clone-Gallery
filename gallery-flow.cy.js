describe('CloneGallery - Image Upload and Search Flow', () => {
  beforeEach(() => {
    // Login as test user
    cy.visit('/login');
    cy.get('[data-cy="email"]').type('test@clonegallery.local');
    cy.get('[data-cy="password"]').type('password123');
    cy.get('[data-cy="login-button"]').click();

    // Wait for redirect to gallery
    cy.url().should('include', '/gallery');
  });

  it('should complete the full image upload and search flow', () => {
    // Step 1: Upload image via drag and drop
    cy.get('[data-cy="upload-dropzone"]').should('be.visible');

    // Simulate file drop
    const fileName = 'test-image.jpg';
    cy.fixture(fileName).then(fileContent => {
      cy.get('[data-cy="upload-input"]').selectFile({
        contents: Cypress.Buffer.from(fileContent, 'base64'),
        fileName: fileName,
        mimeType: 'image/jpeg'
      }, { force: true });
    });

    // Step 2: Fill image metadata
    cy.get('[data-cy="image-title"]').type('Test Landscape Photo');
    cy.get('[data-cy="image-caption"]').type('A beautiful mountain landscape with clear blue sky');
    cy.get('[data-cy="image-alt-text"]').type('Mountain landscape with blue sky');
    cy.get('[data-cy="image-tags"]').type('landscape{enter}mountain{enter}nature{enter}');

    // Step 3: Set privacy and upload
    cy.get('[data-cy="privacy-public"]').click();
    cy.get('[data-cy="upload-button"]').click();

    // Step 4: Verify upload progress
    cy.get('[data-cy="upload-progress"]').should('be.visible');
    cy.get('[data-cy="upload-progress-bar"]').should('exist');

    // Wait for processing to complete
    cy.get('[data-cy="processing-status"]').should('contain', 'Processing complete');

    // Step 5: Verify image appears in gallery
    cy.visit('/gallery');
    cy.get('[data-cy="image-grid"]').should('be.visible');
    cy.get('[data-cy="image-card"]').first().should('contain', 'Test Landscape Photo');

    // Step 6: Test image detail view
    cy.get('[data-cy="image-card"]').first().click();
    cy.get('[data-cy="image-detail"]').should('be.visible');
    cy.get('[data-cy="image-title"]').should('contain', 'Test Landscape Photo');
    cy.get('[data-cy="image-caption"]').should('contain', 'beautiful mountain landscape');
    cy.get('[data-cy="image-tags"]').should('contain', 'landscape');
    cy.get('[data-cy="image-metadata"]').should('be.visible');

    // Step 7: Test text search
    cy.visit('/search');
    cy.get('[data-cy="search-input"]').type('mountain landscape');
    cy.get('[data-cy="search-button"]').click();

    cy.get('[data-cy="search-results"]').should('be.visible');
    cy.get('[data-cy="search-result-card"]').should('have.length.greaterThan', 0);
    cy.get('[data-cy="search-result-card"]').first().should('contain', 'Test Landscape Photo');

    // Step 8: Test vector similarity search
    cy.get('[data-cy="search-tabs"]').within(() => {
      cy.get('[data-cy="vector-search-tab"]').click();
    });

    cy.get('[data-cy="vector-search-input"]').type('beautiful nature scenery');
    cy.get('[data-cy="vector-search-button"]').click();

    cy.get('[data-cy="vector-search-results"]').should('be.visible');
    cy.get('[data-cy="similarity-score"]').should('be.visible');

    // Step 9: Test image actions (like, share)
    cy.get('[data-cy="search-result-card"]').first().click();
    cy.get('[data-cy="like-button"]').click();
    cy.get('[data-cy="like-count"]').should('contain', '1');

    cy.get('[data-cy="share-button"]').click();
    cy.get('[data-cy="share-modal"]').should('be.visible');
    cy.get('[data-cy="copy-link-button"]').click();
    cy.get('[data-cy="share-success"]').should('contain', 'Link copied');
  });

  it('should handle upload errors gracefully', () => {
    // Test file size limit
    cy.get('[data-cy="upload-dropzone"]').should('be.visible');

    // Simulate oversized file
    const largeFile = new File(['x'.repeat(60 * 1024 * 1024)], 'large-file.jpg', { 
      type: 'image/jpeg' 
    });

    cy.get('[data-cy="upload-input"]').selectFile(largeFile, { force: true });
    cy.get('[data-cy="upload-error"]').should('contain', 'File size exceeds maximum limit');

    // Test unsupported file type
    const textFile = new File(['test content'], 'document.txt', { 
      type: 'text/plain' 
    });

    cy.get('[data-cy="upload-input"]').selectFile(textFile, { force: true });
    cy.get('[data-cy="upload-error"]').should('contain', 'File type not supported');
  });

  it('should test accessibility features', () => {
    // Verify keyboard navigation
    cy.get('body').tab();
    cy.focused().should('have.attr', 'data-cy', 'search-input');

    cy.tab();
    cy.focused().should('have.attr', 'data-cy', 'upload-button');

    // Test screen reader labels
    cy.get('[data-cy="image-card"]').first().should('have.attr', 'aria-label');
    cy.get('[data-cy="search-input"]').should('have.attr', 'aria-label');
    cy.get('[data-cy="upload-button"]').should('have.attr', 'aria-label');

    // Check color contrast (this would be done via axe-core)
    cy.injectAxe();
    cy.checkA11y();
  });

  it('should test responsive design', () => {
    // Test mobile viewport
    cy.viewport(375, 667);
    cy.visit('/gallery');

    cy.get('[data-cy="mobile-menu-button"]').should('be.visible');
    cy.get('[data-cy="image-grid"]').should('have.class', 'mobile-grid');

    // Test tablet viewport
    cy.viewport(768, 1024);
    cy.get('[data-cy="image-grid"]').should('have.class', 'tablet-grid');

    // Test desktop viewport
    cy.viewport(1920, 1080);
    cy.get('[data-cy="image-grid"]').should('have.class', 'desktop-grid');
  });
});

// Handle file upload
async function handleUpload() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file first');
        return;
    }

    // Show loading state
    const uploadButton = document.querySelector('#upload-modal button:last-child');
    const originalText = uploadButton.textContent;
    uploadButton.textContent = 'Uploading...';
    uploadButton.disabled = true;

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert('File uploaded successfully!');
            window.location.reload(); // Refresh the page to show new document
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert(error.message || 'Failed to upload document. Please try again.');
    } finally {
        uploadButton.textContent = originalText;
        uploadButton.disabled = false;
        document.getElementById('upload-modal').classList.add('hidden');
    }
}

// Handle document actions
async function performAction(actionType) {
    console.log('performAction called with:', actionType);
    
    const selectedDoc = getSelectedDocument();
    console.log('Selected document:', selectedDoc);
    
    if (!selectedDoc) {
        alert('Please select a document first');
        return;
    }

    try {
        let endpoint;
        let data = {
            text: selectedDoc.content.toString(), // Ensure it's a string
            document_id: selectedDoc.id
        };
        console.log('Request data:', data);

        const button = document.querySelector(`button[onclick*="${actionType}"]`);
        const originalText = button.textContent;
        button.textContent = 'Processing...';
        button.disabled = true;

        switch (actionType) {
            case 'quiz':
                endpoint = '/generate_quiz';
                break;
            case 'summary':
                endpoint = '/summarize';
                break;
            case 'keywords':
                endpoint = '/extract_keywords';
                break;
            case 'translate':
                const targetLanguage = prompt('Enter target language:', 'Spanish');
                if (!targetLanguage) {
                    button.textContent = originalText;
                    button.disabled = false;
                    return;
                }
                data.target_language = targetLanguage;
                endpoint = '/translate';
                break;
            default:
                throw new Error('Unknown action type');
        }

        console.log('Making request to:', endpoint);
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        console.log('Response received:', response);
        const result = await response.json();
        console.log('Result:', result);

        if (response.ok) {
            showResult(actionType, result);
        } else {
            throw new Error(result.error || 'Action failed');
        }

        button.textContent = originalText;
        button.disabled = false;
    } catch (error) {
        console.error(`${actionType} error:`, error);
        alert(error.message || `Failed to ${actionType}. Please try again.`);
    }
}

function getSelectedDocument() {
    console.log('getSelectedDocument called');
    const selectedRadio = document.querySelector('input[name="selected_document"]:checked');
    
    if (!selectedRadio) {
        console.log('No document selected');
        alert('Please select a document first');
        return null;
    }

    const documentItem = selectedRadio.closest('.document-item');
    if (!documentItem) {
        console.error('Could not find document item container');
        return null;
    }

    const docId = documentItem.dataset.documentId;
    const docContent = documentItem.dataset.content;
    
    if (!docId || !docContent) {
        console.error('Missing document data', { docId, docContent });
        alert('Error retrieving document data');
        return null;
    }

    console.log('Document data found:', { docId, contentLength: docContent.length });
    return {
        id: docId,
        content: docContent
    };
}

function showResult(actionType, result) {
    const modalHtml = `
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-2xl font-bold">${actionType.charAt(0).toUpperCase() + actionType.slice(1)} Results</h2>
                    <button onclick="this.closest('.fixed').remove()" 
                            class="text-gray-500 hover:text-gray-700">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                <div class="prose max-w-none mb-6">
                    ${formatResult(actionType, result)}
                </div>
                <div class="flex justify-end">
                    <button onclick="this.closest('.fixed').remove()" 
                            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                        Close
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

function formatResult(actionType, result) {
    console.log('Formatting result for:', actionType);
    switch (actionType) {
        case 'quiz':
            try {
                const quizData = typeof result.quiz === 'string' ? JSON.parse(result.quiz) : result.quiz;
                return `<div class="space-y-4">${JSON.stringify(quizData, null, 2)}</div>`;
            } catch (e) {
                return `<pre class="whitespace-pre-wrap">${result.quiz}</pre>`;
            }
        case 'summary':
            return `<p class="whitespace-pre-line">${result.summary}</p>`;
        case 'keywords':
            try {
                let keywords;
                // Try to parse if it's a string
                keywords = typeof result.keywords === 'string' ? 
                    JSON.parse(result.keywords) : result.keywords;

                // Ensure we have an array
                if (!Array.isArray(keywords)) {
                    keywords = [keywords].filter(Boolean);
                }

                // Format as a list
                return `
                    <div class="space-y-2">
                        <ul class="list-disc pl-5 space-y-1">
                            ${keywords.map(keyword => 
                                `<li class="text-gray-800">${keyword}</li>`
                            ).join('')}
                        </ul>
                    </div>`;
            } catch (error) {
                console.error('Error formatting keywords:', error);
                // Fallback display if parsing fails
                return `<p class="text-gray-800 whitespace-pre-line">${result.keywords}</p>`;
            }
        case 'translate':
            return `<p class="whitespace-pre-line">${result.translation}</p>`;
        default:
            return `<pre class="whitespace-pre-wrap">${JSON.stringify(result, null, 2)}</pre>`;
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing event listeners');
    
    // Auto-select first document if available
    const firstRadio = document.querySelector('input[name="selected_document"]');
    if (firstRadio) {
        firstRadio.checked = true;
    }

    // Setup drag and drop
    const dropZone = document.querySelector('.upload-zone');
    if (dropZone) {
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('dragleave', handleDragLeave);
        dropZone.addEventListener('drop', handleDrop);
    }

    // File input change handler
    const fileInput = document.getElementById('file-upload');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                const fileLabel = dropZone?.querySelector('p');
                if (fileLabel) {
                    fileLabel.textContent = `Selected file: ${fileName}`;
                }
            }
        });
    }
});

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('border-purple-600', 'bg-purple-50');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('border-purple-600', 'bg-purple-50');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const dt = e.dataTransfer;
    const file = dt.files[0];
    
    const fileInput = document.getElementById('file-upload');
    if (fileInput) {
        fileInput.files = dt.files;
    }
    
    e.currentTarget.classList.remove('border-purple-600', 'bg-purple-50');
    
    // Update file name display
    if (file) {
        const dropZone = document.querySelector('.upload-zone');
        const fileLabel = dropZone?.querySelector('p');
        if (fileLabel) {
            fileLabel.textContent = `Selected file: ${file.name}`;
        }
    }
}
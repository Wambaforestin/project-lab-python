// static/js/analysis.js
const API_URL = 'http://localhost:5000';

async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

async function generateQuiz(text, documentId) {
    try {
        const response = await fetch(`${API_URL}/generate_quiz`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text, document_id: documentId })
        });
        return await response.json();
    } catch (error) {
        console.error('Quiz generation error:', error);
        throw error;
    }
}

async function generateSummary(text, documentId, length = 'medium') {
    try {
        const response = await fetch(`${API_URL}/summarize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text, document_id: documentId, length })
        });
        return await response.json();
    } catch (error) {
        console.error('Summary generation error:', error);
        throw error;
    }
}

async function translateText(text, targetLanguage, documentId) {
    try {
        const response = await fetch(`${API_URL}/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text,
                target_language: targetLanguage,
                document_id: documentId
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Translation error:', error);
        throw error;
    }
}

async function extractKeywords(text, documentId) {
    try {
        const response = await fetch(`${API_URL}/extract_keywords`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text, document_id: documentId })
        });
        return await response.json();
    } catch (error) {
        console.error('Keyword extraction error:', error);
        throw error;
    }
}
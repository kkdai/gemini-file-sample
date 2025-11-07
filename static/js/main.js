// API Key Management
const API_KEY_STORAGE_KEY = 'gemini_api_key';

function getApiKey() {
    return localStorage.getItem(API_KEY_STORAGE_KEY);
}

function saveApiKey() {
    const apiKeyInput = document.getElementById('api-key-input');
    const apiKey = apiKeyInput.value.trim();

    if (!apiKey) {
        alert('請輸入 API Key');
        return;
    }

    localStorage.setItem(API_KEY_STORAGE_KEY, apiKey);
    showApiKeyStatus('API Key 已儲存到瀏覽器', 'success');
    log('API Key saved to localStorage', 'success');
    alert('API Key 儲存成功！');
}

function clearApiKey() {
    if (!confirm('確定要清除已儲存的 API Key 嗎？')) {
        return;
    }

    localStorage.removeItem(API_KEY_STORAGE_KEY);
    document.getElementById('api-key-input').value = '';
    showApiKeyStatus('API Key 已清除', 'info');
    log('API Key cleared from localStorage', 'info');
    alert('API Key 已清除');
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('api-key-input');
    input.type = input.type === 'password' ? 'text' : 'password';
}

function showApiKeyStatus(message, type) {
    const statusDiv = document.getElementById('api-key-status');
    const statusText = document.getElementById('api-key-status-text');
    statusText.textContent = message;
    statusDiv.style.display = 'block';
    statusDiv.className = 'info-box ' + type;
}

function loadApiKey() {
    const apiKey = getApiKey();
    if (apiKey) {
        document.getElementById('api-key-input').value = apiKey;
        showApiKeyStatus('已從瀏覽器載入 API Key', 'success');
    }
}

// Tab functionality
function openTab(evt, tabName) {
    // Hide all tab contents
    const tabContents = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove('active');
    }

    // Remove active class from all tab buttons
    const tabButtons = document.getElementsByClassName('tab-button');
    for (let i = 0; i < tabButtons.length; i++) {
        tabButtons[i].classList.remove('active');
    }

    // Show the current tab and mark button as active
    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active');
}

// Logging functionality
function log(message, type = 'info') {
    const logBox = document.getElementById('log');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span>${message}`;
    logBox.appendChild(logEntry);
    logBox.scrollTop = logBox.scrollHeight;
}

// API call wrapper
async function apiCall(url, options = {}) {
    try {
        // Get API key from localStorage
        const apiKey = getApiKey();
        if (!apiKey) {
            throw new Error('API Key 尚未設定。請先到「設定」頁面輸入您的 API Key。');
        }

        // Add API key to headers
        options.headers = options.headers || {};
        options.headers['X-API-Key'] = apiKey;

        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }

        return data;
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
        throw error;
    }
}

// Create Store
async function createStore() {
    const displayName = document.getElementById('store-name').value || 'my-file-search-store';

    log(`Creating store: ${displayName}...`, 'info');

    try {
        const data = await apiCall('/api/create-store', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ display_name: displayName })
        });

        log(`Store created successfully: ${data.store_name}`, 'success');
        alert(`儲存空間建立成功！\n名稱：${data.store_name}\n顯示名稱：${data.display_name}`);
        listStores(); // Refresh the store list
    } catch (error) {
        log(`Failed to create store: ${error.message}`, 'error');
        alert(`建立儲存空間失敗：${error.message}`);
    }
}

// List Stores
async function listStores() {
    log('Fetching store list...', 'info');

    try {
        const data = await apiCall('/api/list-stores');

        const storeListDiv = document.getElementById('store-list');

        if (data.stores.length === 0) {
            storeListDiv.innerHTML = '<p class="info-text">找不到儲存空間。請先建立一個！</p>';
        } else {
            storeListDiv.innerHTML = '';
            data.stores.forEach(store => {
                const storeItem = document.createElement('div');
                storeItem.className = 'store-item';
                storeItem.innerHTML = `
                    <p><strong>⚠️ 完整名稱（上傳時必須使用此名稱）：</strong><br>
                    <code style="background: #f0f0f0; padding: 4px 8px; border-radius: 3px; font-size: 14px; display: inline-block; margin-top: 5px;">${store.name}</code>
                    <button onclick="copyStoreName('${store.name}')" class="btn btn-small" style="margin-left: 10px;">📋 複製名稱</button></p>
                    <p><strong>顯示名稱：</strong> ${store.display_name}</p>
                    <p><strong>建立時間：</strong> ${store.create_time}</p>
                `;
                storeListDiv.appendChild(storeItem);
            });
        }

        log(`Found ${data.stores.length} store(s)`, 'success');
    } catch (error) {
        log(`Failed to list stores: ${error.message}`, 'error');
    }
}

// Delete Store
async function deleteStore() {
    const storeName = document.getElementById('delete-store-name').value.trim();

    if (!storeName) {
        alert('請輸入儲存空間名稱');
        return;
    }

    if (!confirm(`確定要刪除 ${storeName} 嗎？`)) {
        return;
    }

    log(`Deleting store: ${storeName}...`, 'info');

    try {
        const data = await apiCall('/api/delete-store', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ store_name: storeName, force: true })
        });

        log(`Store deleted successfully`, 'success');
        alert('儲存空間刪除成功');
        document.getElementById('delete-store-name').value = '';
        listStores(); // Refresh the list
    } catch (error) {
        log(`Failed to delete store: ${error.message}`, 'error');
        alert(`刪除儲存空間失敗：${error.message}`);
    }
}

// Upload to Store (Direct)
async function uploadToStore() {
    const fileInput = document.getElementById('direct-upload-file');
    const storeName = document.getElementById('upload-store-name').value.trim();
    const fileName = document.getElementById('upload-file-name').value.trim();

    if (!fileInput.files[0]) {
        alert('請選擇檔案');
        return;
    }

    if (!storeName) {
        alert('請輸入儲存空間名稱');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('store_name', storeName);
    if (fileName) {
        formData.append('file_name', fileName);
    }

    log(`Uploading ${fileInput.files[0].name} to store...`, 'info');

    try {
        const data = await apiCall('/api/upload-to-store', {
            method: 'POST',
            body: formData
        });

        log(`File uploaded and imported successfully`, 'success');
        alert('檔案上傳並匯入成功！');
        fileInput.value = '';
    } catch (error) {
        log(`Failed to upload: ${error.message}`, 'error');
        alert(`上傳失敗：${error.message}`);
    }
}

// Upload File (Step 1)
async function uploadFile() {
    const fileInput = document.getElementById('upload-file');
    const fileName = document.getElementById('file-name').value.trim();

    if (!fileInput.files[0]) {
        alert('請選擇檔案');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (fileName) {
        formData.append('file_name', fileName);
    }

    log(`Uploading ${fileInput.files[0].name}...`, 'info');

    try {
        const data = await apiCall('/api/upload-file', {
            method: 'POST',
            body: formData
        });

        log(`File uploaded: ${data.file_name}`, 'success');

        // Show uploaded file info
        document.getElementById('uploaded-file-name').textContent = data.file_name;
        document.getElementById('uploaded-file-info').style.display = 'block';

        // Auto-fill the import file name
        document.getElementById('import-file-name').value = data.file_name;

        alert(`檔案上傳成功！\n檔案名稱：${data.file_name}`);
        fileInput.value = '';
    } catch (error) {
        log(`Failed to upload file: ${error.message}`, 'error');
        alert(`上傳檔案失敗：${error.message}`);
    }
}

// Import File (Step 2)
async function importFile() {
    const storeName = document.getElementById('import-store-name').value.trim();
    const fileName = document.getElementById('import-file-name').value.trim();

    if (!storeName || !fileName) {
        alert('請輸入儲存空間名稱和檔案名稱');
        return;
    }

    // Collect metadata
    const metadata = [];
    const metadataRows = document.querySelectorAll('.metadata-row');
    metadataRows.forEach(row => {
        const key = row.querySelector('.metadata-key').value.trim();
        const value = row.querySelector('.metadata-value').value.trim();
        const type = row.querySelector('.metadata-type').value;

        if (key && value) {
            const metadataItem = { key: key };
            if (type === 'numeric') {
                metadataItem.numeric_value = parseFloat(value);
            } else {
                metadataItem.string_value = value;
            }
            metadata.push(metadataItem);
        }
    });

    log(`Importing ${fileName} to ${storeName}...`, 'info');

    try {
        const data = await apiCall('/api/import-file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                store_name: storeName,
                file_name: fileName,
                custom_metadata: metadata
            })
        });

        log(`File imported successfully`, 'success');
        alert('檔案匯入成功！');
    } catch (error) {
        log(`Failed to import file: ${error.message}`, 'error');
        alert(`匯入檔案失敗：${error.message}`);
    }
}

// Copy store name to clipboard and auto-fill
function copyStoreName(storeName) {
    // Copy to clipboard
    navigator.clipboard.writeText(storeName).then(() => {
        log(`已複製儲存空間名稱：${storeName}`, 'success');
        alert(`已複製儲存空間名稱！\n${storeName}\n\n您現在可以到「檔案上傳」頁面貼上使用。`);

        // Auto-fill upload forms
        const uploadStoreNameInput = document.getElementById('upload-store-name');
        const importStoreNameInput = document.getElementById('import-store-name');
        const queryStoreNamesInput = document.getElementById('query-store-names');

        if (uploadStoreNameInput) uploadStoreNameInput.value = storeName;
        if (importStoreNameInput) importStoreNameInput.value = storeName;
        if (queryStoreNamesInput) queryStoreNamesInput.value = storeName;
    }).catch(err => {
        alert(`複製失敗。請手動複製此名稱：\n${storeName}`);
    });
}

// Add Metadata Row
function addMetadataRow() {
    const container = document.getElementById('metadata-container');
    const newRow = document.createElement('div');
    newRow.className = 'metadata-row';
    newRow.innerHTML = `
        <input type="text" placeholder="Key" class="metadata-key">
        <input type="text" placeholder="Value" class="metadata-value">
        <select class="metadata-type">
            <option value="string">字串</option>
            <option value="numeric">數字</option>
        </select>
    `;
    container.appendChild(newRow);
}

// Query Store
async function queryStore() {
    const storeNamesInput = document.getElementById('query-store-names').value.trim();
    const queryText = document.getElementById('query-text').value.trim();
    const metadataFilter = document.getElementById('metadata-filter').value.trim();

    if (!storeNamesInput || !queryText) {
        alert('請輸入儲存空間名稱和查詢內容');
        return;
    }

    // Split store names by comma
    const storeNames = storeNamesInput.split(',').map(s => s.trim()).filter(s => s);

    log(`Querying stores with: "${queryText}"...`, 'info');

    const requestBody = {
        store_names: storeNames,
        query: queryText
    };

    if (metadataFilter) {
        requestBody.metadata_filter = metadataFilter;
    }

    try {
        const data = await apiCall('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        // Display response
        const resultBox = document.getElementById('query-result');
        resultBox.className = 'result-box success';
        resultBox.textContent = data.response;

        // Display grounding metadata
        const groundingBox = document.getElementById('grounding-metadata');
        if (data.grounding_metadata) {
            groundingBox.className = 'result-box';
            groundingBox.textContent = data.grounding_metadata;
        } else {
            groundingBox.className = 'result-box';
            groundingBox.innerHTML = '<p class="info-text">無可用的引用資訊</p>';
        }

        log(`Query completed successfully`, 'success');
    } catch (error) {
        const resultBox = document.getElementById('query-result');
        resultBox.className = 'result-box error';
        resultBox.textContent = `錯誤：${error.message}`;

        log(`Query failed: ${error.message}`, 'error');
        alert(`查詢失敗：${error.message}`);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load saved API key
    loadApiKey();

    log('Gemini 檔案搜尋測試工具已初始化', 'success');

    const apiKey = getApiKey();
    if (apiKey) {
        log('已從 localStorage 載入 API Key', 'success');
        log('準備就緒，可以開始測試檔案搜尋 API', 'info');
    } else {
        log('尚未設定 API Key。請到「設定」頁面設定您的 API Key。', 'info');
    }
});

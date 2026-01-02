/**
 * Netspecs Dashboard - Main Application
 */

(function() {
    'use strict';

    // DOM Elements
    const elements = {
        themeToggle: document.getElementById('themeToggle'),
        settingsToggle: document.getElementById('settingsToggle'),
        settingsModal: document.getElementById('settingsModal'),
        settingsClose: document.getElementById('settingsClose'),
        settingsCancel: document.getElementById('settingsCancel'),
        settingsSave: document.getElementById('settingsSave'),
        statusIndicator: document.getElementById('statusIndicator'),
        liveLatency: document.getElementById('liveLatency'),
        packetLoss: document.getElementById('packetLoss'),
        btnLatency: document.getElementById('btnLatency'),
        btnSpeed: document.getElementById('btnSpeed'),
        btnJitter: document.getElementById('btnJitter'),
        btnNetInfo: document.getElementById('btnNetInfo'),
        btnAIDiagnostics: document.getElementById('btnAIDiagnostics'),
        resultsContainer: document.getElementById('resultsContainer'),
        resultsHistory: document.getElementById('resultsHistory'),
        clearResults: document.getElementById('clearResults'),
        loadResults: document.getElementById('loadResults'),
        // Global settings fields
        globalApiKey: document.getElementById('globalApiKey'),
        apiKeyStatus: document.getElementById('apiKeyStatus'),
        resultsStoragePath: document.getElementById('resultsStoragePath'),
        autoSaveResults: document.getElementById('autoSaveResults'),
        // Config fields
        latencyEndpoints: document.getElementById('latencyEndpoints'),
        latencyCount: document.getElementById('latencyCount'),
        speedIncludeOokla: document.getElementById('speedIncludeOokla'),
        jitterEndpoint: document.getElementById('jitterEndpoint'),
        jitterDuration: document.getElementById('jitterDuration'),
        aiApiKey: document.getElementById('aiApiKey'),
        aiModel: document.getElementById('aiModel'),
        aiPrompt: document.getElementById('aiPrompt'),
        aiRunLatency: document.getElementById('aiRunLatency'),
        aiRunJitter: document.getElementById('aiRunJitter'),
        aiRunNetInfo: document.getElementById('aiRunNetInfo'),
        aiUseExisting: document.getElementById('aiUseExisting'),
    };

    // State
    let ws = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 10;
    const reconnectDelay = 3000;
    
    // Settings and results storage
    let settings = {
        apiKey: '',
        storagePath: './netspecs_results',
        autoSave: true
    };
    let resultsHistory = [];
    let latestResults = {}; // Store latest test results for AI diagnostics

    // Theme Management
    function initTheme() {
        const savedTheme = localStorage.getItem('netspecs-theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('netspecs-theme', next);
    }

    // Settings Management
    function loadSettings() {
        const saved = localStorage.getItem('netspecs-settings');
        if (saved) {
            try {
                settings = { ...settings, ...JSON.parse(saved) };
            } catch (e) {
                console.error('Failed to load settings:', e);
            }
        }
        
        // Apply settings to UI
        if (elements.globalApiKey) {
            elements.globalApiKey.value = settings.apiKey || '';
        }
        if (elements.resultsStoragePath) {
            elements.resultsStoragePath.value = settings.storagePath || './netspecs_results';
        }
        if (elements.autoSaveResults) {
            elements.autoSaveResults.checked = settings.autoSave !== false;
        }
        
        // Validate API key if present
        if (settings.apiKey) {
            validateApiKey(settings.apiKey);
        } else {
            // Check server for environment API key
            fetchServerApiKeyStatus();
        }
    }
    
    function saveSettings() {
        settings.apiKey = elements.globalApiKey?.value || '';
        settings.storagePath = elements.resultsStoragePath?.value || './netspecs_results';
        settings.autoSave = elements.autoSaveResults?.checked !== false;
        
        localStorage.setItem('netspecs-settings', JSON.stringify(settings));
        
        // Validate the new API key
        if (settings.apiKey) {
            validateApiKey(settings.apiKey);
        }
        
        closeSettingsModal();
    }
    
    async function validateApiKey(key) {
        if (!elements.apiKeyStatus) return;
        
        if (!key) {
            elements.apiKeyStatus.textContent = 'No API key set';
            elements.apiKeyStatus.className = 'field-hint';
            return;
        }
        
        elements.apiKeyStatus.textContent = 'Validating...';
        elements.apiKeyStatus.className = 'field-hint';
        
        try {
            const response = await fetch('/api/validate-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: key })
            });
            const data = await response.json();
            
            if (data.valid) {
                elements.apiKeyStatus.textContent = 'API key valid';
                elements.apiKeyStatus.className = 'field-hint valid';
            } else {
                elements.apiKeyStatus.textContent = data.message || 'Invalid API key';
                elements.apiKeyStatus.className = 'field-hint invalid';
            }
        } catch (e) {
            elements.apiKeyStatus.textContent = 'Could not validate';
            elements.apiKeyStatus.className = 'field-hint';
        }
    }
    
    async function fetchServerApiKeyStatus() {
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();
            
            if (data.has_api_key) {
                if (elements.apiKeyStatus) {
                    elements.apiKeyStatus.textContent = 'Using environment API key';
                    elements.apiKeyStatus.className = 'field-hint valid';
                }
                if (elements.globalApiKey && !elements.globalApiKey.value) {
                    elements.globalApiKey.placeholder = 'Environment key detected';
                }
            } else if (elements.apiKeyStatus) {
                elements.apiKeyStatus.textContent = 'No API key configured';
                elements.apiKeyStatus.className = 'field-hint';
            }
        } catch (e) {
            console.error('Failed to fetch server settings:', e);
        }
    }
    
    function openSettingsModal() {
        elements.settingsModal?.classList.add('open');
    }
    
    function closeSettingsModal() {
        elements.settingsModal?.classList.remove('open');
    }

    // WebSocket Management
    function connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/live`;
        
        try {
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                reconnectAttempts = 0;
                updateStatus('connected', 'Connected');
            };
            
            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'ping') {
                        updateLiveMetrics(data);
                    }
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                updateStatus('disconnected', 'Disconnected');
                attemptReconnect();
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                updateStatus('disconnected', 'Error');
            };
        } catch (e) {
            console.error('Failed to create WebSocket:', e);
            updateStatus('disconnected', 'Failed to connect');
        }
    }

    function attemptReconnect() {
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            updateStatus('', `Reconnecting (${reconnectAttempts}/${maxReconnectAttempts})...`);
            setTimeout(connectWebSocket, reconnectDelay);
        } else {
            updateStatus('disconnected', 'Connection failed');
        }
    }

    function updateStatus(status, text) {
        elements.statusIndicator.className = 'status-indicator ' + status;
        elements.statusIndicator.querySelector('.status-text').textContent = text;
    }

    function updateLiveMetrics(data) {
        if (data.latency_ms !== null && data.latency_ms !== undefined) {
            elements.liveLatency.textContent = data.latency_ms.toFixed(1);
        }
        if (data.packet_loss !== null && data.packet_loss !== undefined) {
            elements.packetLoss.textContent = data.packet_loss.toFixed(1);
        }
    }

    // Config Panel Toggles
    function initConfigToggles() {
        document.querySelectorAll('.config-toggle').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                const targetId = this.dataset.target;
                const panel = document.getElementById(targetId);
                if (panel) {
                    panel.classList.toggle('open');
                    this.classList.toggle('active');
                }
            });
        });
    }

    // Get configuration values
    function getTestConfig(testType) {
        const config = {};
        
        switch (testType) {
            case 'latency':
                if (elements.latencyEndpoints && elements.latencyEndpoints.value.trim()) {
                    config.endpoints = elements.latencyEndpoints.value
                        .split(',')
                        .map(e => e.trim())
                        .filter(e => e);
                }
                if (elements.latencyCount) {
                    config.count = parseInt(elements.latencyCount.value) || 10;
                }
                break;
            case 'jitter':
                if (elements.jitterEndpoint && elements.jitterEndpoint.value.trim()) {
                    config.endpoint = elements.jitterEndpoint.value.trim();
                }
                if (elements.jitterDuration) {
                    config.duration = parseInt(elements.jitterDuration.value) || 10;
                }
                break;
            case 'speed':
                if (elements.speedIncludeOokla) {
                    config.include_ookla = elements.speedIncludeOokla.checked;
                }
                break;
            case 'ai-diagnostics':
                // API key: use AI-specific key, fall back to global key
                const aiKey = elements.aiApiKey?.value.trim();
                const globalKey = settings.apiKey;
                if (aiKey) {
                    config.api_key = aiKey;
                } else if (globalKey) {
                    config.api_key = globalKey;
                }
                
                if (elements.aiModel && elements.aiModel.value.trim()) {
                    config.model = elements.aiModel.value.trim();
                }
                if (elements.aiPrompt && elements.aiPrompt.value.trim()) {
                    config.custom_prompt = elements.aiPrompt.value.trim();
                }
                
                // Tests to run
                config.run_tests = {
                    latency: elements.aiRunLatency?.checked !== false,
                    jitter: elements.aiRunJitter?.checked !== false,
                    network_info: elements.aiRunNetInfo?.checked !== false
                };
                
                // Use existing results
                config.use_existing = elements.aiUseExisting?.checked || false;
                if (config.use_existing && Object.keys(latestResults).length > 0) {
                    config.existing_results = latestResults;
                }
                break;
        }
        
        return config;
    }

    // API Calls
    async function runTest(testType, button) {
        if (button.classList.contains('loading')) return;
        
        button.classList.add('loading');
        button.disabled = true;
        
        try {
            let response;
            let endpoint;
            const config = getTestConfig(testType);
            
            switch (testType) {
                case 'latency':
                    endpoint = '/api/latency';
                    response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    });
                    break;
                case 'speed':
                    endpoint = '/api/speed';
                    response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    });
                    break;
                case 'jitter':
                    endpoint = '/api/jitter';
                    response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    });
                    break;
                case 'network-info':
                    endpoint = '/api/network-info';
                    response = await fetch(endpoint, { method: 'GET' });
                    break;
                case 'ai-diagnostics':
                    endpoint = '/api/ai-diagnostics';
                    response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    });
                    break;
                default:
                    throw new Error('Unknown test type');
            }
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            displayResult(testType, data);
            
        } catch (error) {
            console.error(`${testType} test failed:`, error);
            displayError(testType, error.message);
        } finally {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }

    // Results Display
    function displayResult(testType, data) {
        const placeholder = elements.resultsContainer.querySelector('.results-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        // Move existing results to history
        const existingResults = elements.resultsContainer.querySelectorAll('.result-item');
        existingResults.forEach(item => {
            moveToHistory(item);
        });
        
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        const timestamp = new Date().toLocaleTimeString();
        const fullTimestamp = new Date().toISOString();
        const title = getTestTitle(testType);
        
        // Store result for AI diagnostics reuse
        if (testType !== 'ai-diagnostics') {
            latestResults[testType] = { data, timestamp: fullTimestamp };
        }
        
        let content = '';
        
        switch (testType) {
            case 'latency':
                content = formatLatencyResult(data);
                break;
            case 'speed':
                content = formatSpeedResult(data);
                break;
            case 'jitter':
                content = formatJitterResult(data);
                break;
            case 'network-info':
                content = formatNetworkInfoResult(data);
                break;
            case 'ai-diagnostics':
                content = formatAIDiagnosticsResult(data);
                break;
            default:
                content = `<div class="result-data">${JSON.stringify(data, null, 2)}</div>`;
        }
        
        resultItem.innerHTML = `
            <h3>${title} <span class="timestamp">${timestamp}</span></h3>
            ${content}
        `;
        resultItem.dataset.testType = testType;
        resultItem.dataset.timestamp = fullTimestamp;
        resultItem.dataset.rawData = JSON.stringify(data);
        
        elements.resultsContainer.insertBefore(resultItem, elements.resultsContainer.firstChild);
    }
    
    function moveToHistory(resultItem) {
        const testType = resultItem.dataset.testType || 'unknown';
        const timestamp = resultItem.dataset.timestamp || new Date().toISOString();
        const title = getTestTitle(testType);
        const time = new Date(timestamp).toLocaleTimeString();
        const content = resultItem.querySelector('.result-grid, .result-data');
        
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-header">
                <div class="history-title">
                    <span class="history-type">${title}</span>
                    <span class="history-time">${time}</span>
                </div>
                <svg class="history-toggle" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"/>
                </svg>
            </div>
            <div class="history-content">
                ${content ? content.outerHTML : ''}
            </div>
        `;
        
        historyItem.querySelector('.history-header').addEventListener('click', function() {
            historyItem.classList.toggle('open');
        });
        
        elements.resultsHistory.insertBefore(historyItem, elements.resultsHistory.firstChild);
        
        // Limit history to 20 items
        const historyItems = elements.resultsHistory.querySelectorAll('.history-item');
        if (historyItems.length > 20) {
            historyItems[historyItems.length - 1].remove();
        }
    }

    function displayError(testType, message) {
        const placeholder = elements.resultsContainer.querySelector('.results-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        const timestamp = new Date().toLocaleTimeString();
        const title = getTestTitle(testType);
        
        resultItem.innerHTML = `
            <h3>${title} <span class="timestamp">${timestamp}</span></h3>
            <div class="result-data" style="color: var(--color-error);">Error: ${message}</div>
        `;
        
        elements.resultsContainer.insertBefore(resultItem, elements.resultsContainer.firstChild);
    }

    function getTestTitle(testType) {
        const titles = {
            'latency': 'Latency Test',
            'speed': 'Speed Test',
            'jitter': 'Jitter Test',
            'network-info': 'Network Info',
            'ai-diagnostics': 'AI Diagnostics Report'
        };
        return titles[testType] || testType;
    }

    function formatLatencyResult(data) {
        if (!data.results || data.results.length === 0) {
            return '<div class="result-data">No results</div>';
        }
        
        let html = '<div class="result-grid">';
        for (const result of data.results) {
            const latencyClass = getLatencyClass(result.avg_ms);
            html += `
                <div class="result-stat">
                    <span class="result-stat-label">${result.host}</span>
                    <span class="result-stat-value ${latencyClass}">${result.avg_ms?.toFixed(1) || '--'} ms</span>
                </div>
            `;
        }
        html += '</div>';
        return html;
    }

    function formatSpeedResult(data) {
        const result = data.result || {};
        const download = result.download_mbps || 0;
        const upload = result.upload_mbps || 0;
        
        return `
            <div class="result-grid">
                <div class="result-stat">
                    <span class="result-stat-label">Download</span>
                    <span class="result-stat-value ${getSpeedClass(download)}">${download.toFixed(1)} Mbps</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">Upload</span>
                    <span class="result-stat-value ${getSpeedClass(upload)}">${upload.toFixed(1)} Mbps</span>
                </div>
                ${result.ping_ms ? `
                <div class="result-stat">
                    <span class="result-stat-label">Ping</span>
                    <span class="result-stat-value">${result.ping_ms.toFixed(1)} ms</span>
                </div>
                ` : ''}
            </div>
        `;
    }

    function formatJitterResult(data) {
        const result = data.result || {};
        const jitter = result.jitter_ms || 0;
        
        return `
            <div class="result-grid">
                <div class="result-stat">
                    <span class="result-stat-label">Jitter</span>
                    <span class="result-stat-value ${getJitterClass(jitter)}">${jitter.toFixed(2)} ms</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">Min Latency</span>
                    <span class="result-stat-value">${result.min_ms?.toFixed(1) || '--'} ms</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">Max Latency</span>
                    <span class="result-stat-value">${result.max_ms?.toFixed(1) || '--'} ms</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">Samples</span>
                    <span class="result-stat-value">${result.sample_count || '--'}</span>
                </div>
            </div>
        `;
    }

    function formatNetworkInfoResult(data) {
        const info = data.info || {};
        
        return `
            <div class="result-grid">
                <div class="result-stat">
                    <span class="result-stat-label">Public IP</span>
                    <span class="result-stat-value">${info.public_ip || 'Unknown'}</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">ISP</span>
                    <span class="result-stat-value">${info.isp || 'Unknown'}</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">Local IP</span>
                    <span class="result-stat-value">${info.local_ip || 'Unknown'}</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">Gateway</span>
                    <span class="result-stat-value">${info.default_gateway || 'Unknown'}</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">Interface</span>
                    <span class="result-stat-value">${info.interface_type || 'Unknown'}</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-label">DNS</span>
                    <span class="result-stat-value">${info.dns_servers?.join(', ') || 'Unknown'}</span>
                </div>
            </div>
        `;
    }

    function formatAIDiagnosticsResult(data) {
        if (data.error) {
            return `<div class="result-data" style="color: var(--color-error);">${data.error}</div>`;
        }
        
        const report = data.report || 'No report generated.';
        // Convert markdown-style formatting to HTML
        const formattedReport = report
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        
        return `<div class="result-data ai-report">${formattedReport}</div>`;
    }

    function getLatencyClass(ms) {
        if (ms === null || ms === undefined) return '';
        if (ms < 50) return 'good';
        if (ms < 100) return 'warning';
        return 'bad';
    }

    function getSpeedClass(mbps) {
        if (mbps >= 100) return 'good';
        if (mbps >= 25) return 'warning';
        return 'bad';
    }

    function getJitterClass(ms) {
        if (ms < 5) return 'good';
        if (ms < 15) return 'warning';
        return 'bad';
    }

    function clearResults() {
        elements.resultsContainer.innerHTML = '<p class="results-placeholder">Run a test to see results here.</p>';
        elements.resultsHistory.innerHTML = '';
        latestResults = {};
    }

    // Event Listeners
    function initEventListeners() {
        elements.themeToggle?.addEventListener('click', toggleTheme);
        
        // Settings modal
        elements.settingsToggle?.addEventListener('click', openSettingsModal);
        elements.settingsClose?.addEventListener('click', closeSettingsModal);
        elements.settingsCancel?.addEventListener('click', closeSettingsModal);
        elements.settingsSave?.addEventListener('click', saveSettings);
        
        // Close modal on overlay click
        elements.settingsModal?.addEventListener('click', function(e) {
            if (e.target === elements.settingsModal) {
                closeSettingsModal();
            }
        });
        
        // Validate API key on blur
        elements.globalApiKey?.addEventListener('blur', function() {
            if (this.value) {
                validateApiKey(this.value);
            }
        });
        
        // Test buttons
        elements.btnLatency?.addEventListener('click', function() {
            runTest('latency', this);
        });
        
        elements.btnSpeed?.addEventListener('click', function() {
            runTest('speed', this);
        });
        
        elements.btnJitter?.addEventListener('click', function() {
            runTest('jitter', this);
        });
        
        elements.btnNetInfo?.addEventListener('click', function() {
            runTest('network-info', this);
        });
        
        elements.btnAIDiagnostics?.addEventListener('click', function() {
            runTest('ai-diagnostics', this);
        });
        
        elements.clearResults?.addEventListener('click', clearResults);
        
        // Load results button
        elements.loadResults?.addEventListener('click', loadResultsFromStorage);
    }
    
    async function loadResultsFromStorage() {
        try {
            const response = await fetch('/api/results/latest');
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                data.results.forEach((result, index) => {
                    if (index === 0) {
                        displayResult(result.type, result.data);
                    } else {
                        // Add directly to history
                        latestResults[result.type] = result;
                    }
                });
            }
        } catch (e) {
            console.error('Failed to load results:', e);
        }
    }

    // Initialize
    function init() {
        initTheme();
        loadSettings();
        initEventListeners();
        initConfigToggles();
        connectWebSocket();
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();


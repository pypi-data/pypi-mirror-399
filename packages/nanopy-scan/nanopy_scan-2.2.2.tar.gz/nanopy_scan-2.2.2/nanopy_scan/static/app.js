// ========== State ==========
let currentView = 'home';
let blocksPage = 1;
let txsPage = 1;
let addressPage = 1;
let currentAddress = '';

// ========== Utilities ==========
function formatNumber(n) {
    if (n === null || n === undefined) return '--';
    return n.toLocaleString();
}

function formatHash(hash, len = 8) {
    if (!hash) return '--';
    return hash.slice(0, len + 2) + '...' + hash.slice(-len);
}

function formatAddr(addr) {
    if (!addr) return '--';
    return addr.slice(0, 10) + '...' + addr.slice(-8);
}

function formatValue(wei) {
    if (!wei || wei === '0') return '0 NPY';
    const val = BigInt(wei);
    const npy = Number(val) / 1e18;
    if (npy >= 1) return npy.toFixed(4) + ' NPY';
    if (npy >= 0.0001) return npy.toFixed(6) + ' NPY';
    return npy.toExponential(2) + ' NPY';
}

function timeAgo(timestamp) {
    if (!timestamp) return '--';
    const seconds = Math.floor(Date.now() / 1000) - timestamp;
    if (seconds < 0) return 'just now';
    if (seconds < 60) return seconds + 's ago';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
    return Math.floor(seconds / 86400) + 'd ago';
}

// ========== API Calls ==========
async function api(endpoint) {
    try {
        const res = await fetch('/api' + endpoint);
        return await res.json();
    } catch (e) {
        console.error('API error:', e);
        return null;
    }
}

// ========== Navigation ==========
function navigate(view, param = null) {
    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    // Update nav
    document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
    const navEl = document.getElementById('nav-' + view);
    if (navEl) navEl.classList.add('active');

    currentView = view;

    // Show selected view
    const viewEl = document.getElementById('view-' + view);
    if (viewEl) viewEl.classList.add('active');

    // Load data
    switch(view) {
        case 'home': loadDashboard(); break;
        case 'blocks': loadBlocksList(); break;
        case 'transactions': loadTxsList(); break;
        case 'validators': loadValidators(); break;
        case 'network': loadNetwork(); break;
        case 'block': loadBlockDetail(param); break;
        case 'tx': loadTxDetail(param); break;
        case 'address': loadAddressDetail(param); break;
    }

    // Update URL
    let url = '/';
    if (view === 'blocks') url = '/blocks';
    else if (view === 'transactions') url = '/transactions';
    else if (view === 'validators') url = '/validators';
    else if (view === 'network') url = '/network';
    else if (view === 'block') url = '/block/' + param;
    else if (view === 'tx') url = '/tx/' + param;
    else if (view === 'address') url = '/address/' + param;

    history.pushState({view, param}, '', url);
}

// ========== Dashboard ==========
async function loadDashboard() {
    // Load status
    const status = await api('/status');
    if (status) {
        document.getElementById('networkName').textContent = status.networkName || 'NanoPy';
        document.getElementById('statBlockHeight').textContent = formatNumber(status.chainHeight);
        document.getElementById('statTxCount').textContent = formatNumber(status.indexedTransactions);
        document.getElementById('statTps').textContent = status.tps.toFixed(4);
        document.getElementById('statAddresses').textContent = formatNumber(status.totalAddresses);
        document.getElementById('statSyncStatus').textContent =
            `${formatNumber(status.indexedBlocks)} indexed`;
    }

    // Load latest blocks
    const blocks = await api('/blocks?limit=6');
    if (blocks && blocks.blocks) {
        document.getElementById('latestBlocks').innerHTML = blocks.blocks.map(b => `
            <tr>
                <td><a href="/block/${b.number}" onclick="navigate('block', ${b.number}); return false;">${formatNumber(b.number)}</a></td>
                <td class="hide-mobile mono truncate"><a href="/address/${b.miner}" onclick="navigate('address', '${b.miner}'); return false;">${formatAddr(b.miner)}</a></td>
                <td><span class="badge badge-muted">${b.tx_count}</span></td>
                <td>${timeAgo(b.timestamp)}</td>
            </tr>
        `).join('');
    }

    // Load latest transactions
    const txs = await api('/transactions?limit=6');
    if (txs && txs.transactions) {
        document.getElementById('latestTxs').innerHTML = txs.transactions.length > 0
            ? txs.transactions.map(tx => `
                <tr>
                    <td class="mono"><a href="/tx/${tx.hash}" onclick="navigate('tx', '${tx.hash}'); return false;">${formatHash(tx.hash)}</a></td>
                    <td class="hide-mobile mono truncate"><a href="/address/${tx.from_addr}" onclick="navigate('address', '${tx.from_addr}'); return false;">${formatAddr(tx.from_addr)}</a></td>
                    <td>${formatValue(tx.value)}</td>
                </tr>
            `).join('')
            : '<tr><td colspan="3" style="text-align:center;color:var(--muted-foreground);">No transactions yet</td></tr>';
    }
}

// ========== Blocks List ==========
async function loadBlocksList(page = 1) {
    blocksPage = page;
    const data = await api(`/blocks?page=${page}&limit=25`);
    if (!data) return;

    document.getElementById('blocksTotal').textContent = formatNumber(data.total) + ' blocks';

    document.getElementById('blocksList').innerHTML = data.blocks.map(b => `
        <tr>
            <td><a href="/block/${b.number}" onclick="navigate('block', ${b.number}); return false;">${formatNumber(b.number)}</a></td>
            <td class="mono truncate">${formatHash(b.hash, 10)}</td>
            <td class="hide-mobile mono truncate"><a href="/address/${b.miner}" onclick="navigate('address', '${b.miner}'); return false;">${formatAddr(b.miner)}</a></td>
            <td><span class="badge badge-muted">${b.tx_count}</span></td>
            <td>${formatNumber(b.gas_used)}</td>
            <td>${timeAgo(b.timestamp)}</td>
        </tr>
    `).join('');

    renderPagination('blocksPagination', data.page, data.pages, (p) => loadBlocksList(p));
}

// ========== Transactions List ==========
async function loadTxsList(page = 1) {
    txsPage = page;
    const data = await api(`/transactions?page=${page}&limit=25`);
    if (!data) return;

    document.getElementById('txsTotal').textContent = formatNumber(data.total) + ' transactions';

    document.getElementById('txsList').innerHTML = data.transactions.length > 0
        ? data.transactions.map(tx => `
            <tr>
                <td class="mono"><a href="/tx/${tx.hash}" onclick="navigate('tx', '${tx.hash}'); return false;">${formatHash(tx.hash)}</a></td>
                <td><a href="/block/${tx.block_number}" onclick="navigate('block', ${tx.block_number}); return false;">${tx.block_number}</a></td>
                <td class="mono truncate"><a href="/address/${tx.from_addr}" onclick="navigate('address', '${tx.from_addr}'); return false;">${formatAddr(tx.from_addr)}</a></td>
                <td class="mono truncate"><a href="/address/${tx.to_addr}" onclick="navigate('address', '${tx.to_addr}'); return false;">${formatAddr(tx.to_addr)}</a></td>
                <td>${formatValue(tx.value)}</td>
                <td class="hide-mobile">${tx.status === 1 ? '<span class="badge badge-success">Success</span>' : '<span class="badge badge-warning">Failed</span>'}</td>
            </tr>
        `).join('')
        : '<tr><td colspan="6" style="text-align:center;color:var(--muted-foreground);">No transactions yet</td></tr>';

    renderPagination('txsPagination', data.page, data.pages, (p) => loadTxsList(p));
}

// ========== Validators ==========
async function loadValidators() {
    const data = await api('/validators?limit=50');
    if (!data) return;

    document.getElementById('validatorsList').innerHTML = data.validators.length > 0
        ? data.validators.map((v, i) => `
            <tr>
                <td>${i + 1}</td>
                <td class="mono"><a href="/address/${v.address}" onclick="navigate('address', '${v.address}'); return false;">${v.address}</a></td>
                <td>${formatNumber(v.blockCount)}</td>
                <td>${timeAgo(v.lastBlock)}</td>
            </tr>
        `).join('')
        : '<tr><td colspan="4" style="text-align:center;color:var(--muted-foreground);">No validators found</td></tr>';
}

// ========== Network Status ==========
async function loadNetwork() {
    const data = await api('/network');
    if (!data) {
        document.getElementById('networkHealthStatus').textContent = 'Error';
        document.getElementById('networkHealthStatus').style.color = 'var(--warning)';
        return;
    }

    // Network Health
    const healthEl = document.getElementById('networkHealthStatus');
    const healthSubEl = document.getElementById('networkHealthSub');
    if (data.network.healthy) {
        healthEl.textContent = 'Healthy';
        healthEl.style.color = 'var(--success)';
        healthSubEl.textContent = 'All systems operational';
    } else if (data.node.online) {
        healthEl.textContent = 'Degraded';
        healthEl.style.color = 'var(--warning)';
        healthSubEl.textContent = `Last block ${data.network.secondsSinceBlock}s ago`;
    } else {
        healthEl.textContent = 'Offline';
        healthEl.style.color = 'var(--destructive-foreground)';
        healthSubEl.textContent = 'Node unreachable';
    }

    // Node Status
    const nodeStatusEl = document.getElementById('nodeStatus');
    if (data.node.online) {
        nodeStatusEl.textContent = 'Online';
        nodeStatusEl.style.color = 'var(--success)';
    } else {
        nodeStatusEl.textContent = 'Offline';
        nodeStatusEl.style.color = 'var(--warning)';
    }
    document.getElementById('nodeUrl').textContent = data.node.url;

    // Peers
    document.getElementById('networkPeers').textContent = data.node.peerCount;

    // Last Block
    document.getElementById('networkLastBlock').textContent = formatNumber(data.node.blockHeight);
    document.getElementById('networkLastBlockTime').textContent = timeAgo(data.network.lastBlockTime);

    // Node Details
    document.getElementById('nodeDetails').innerHTML = `
        <div class="detail-row"><div class="detail-label">RPC URL</div><div class="detail-value mono">${data.node.url}</div></div>
        <div class="detail-row"><div class="detail-label">Chain ID</div><div class="detail-value">${data.node.chainId}</div></div>
        <div class="detail-row"><div class="detail-label">Network</div><div class="detail-value">${data.node.networkName}</div></div>
        <div class="detail-row"><div class="detail-label">Block Height</div><div class="detail-value">${formatNumber(data.node.blockHeight)}</div></div>
        <div class="detail-row"><div class="detail-label">Peers</div><div class="detail-value">${data.node.peerCount}</div></div>
        <div class="detail-row"><div class="detail-label">Gas Price</div><div class="detail-value">${data.node.gasPriceGwei} Gwei</div></div>
        <div class="detail-row"><div class="detail-label">TPS (60s)</div><div class="detail-value">${data.network.tps}</div></div>
    `;

    // Indexer Details
    const syncStatus = data.indexer.isSynced
        ? '<span class="badge badge-success">Synced</span>'
        : '<span class="badge badge-warning">Syncing</span>';

    document.getElementById('indexerDetails').innerHTML = `
        <div class="detail-row"><div class="detail-label">Status</div><div class="detail-value">${syncStatus}</div></div>
        <div class="detail-row"><div class="detail-label">Indexed Blocks</div><div class="detail-value">${formatNumber(data.indexer.indexedBlocks)}</div></div>
        <div class="detail-row"><div class="detail-label">Chain Height</div><div class="detail-value">${formatNumber(data.indexer.syncedWith)}</div></div>
        <div class="detail-row"><div class="detail-label">Last Sync</div><div class="detail-value">${timeAgo(data.indexer.lastSync)}</div></div>
    `;
}

// ========== Block Detail ==========
async function loadBlockDetail(blockId) {
    document.getElementById('blockDetailNumber').textContent = blockId;

    const data = await api(`/block/${blockId}`);
    if (!data || !data.block) {
        document.getElementById('blockDetails').innerHTML = '<div style="padding:2rem;text-align:center;color:var(--muted-foreground);">Block not found</div>';
        return;
    }

    const b = data.block;
    document.getElementById('blockDetails').innerHTML = `
        <div class="detail-row"><div class="detail-label">Block Height</div><div class="detail-value">${formatNumber(b.number)}</div></div>
        <div class="detail-row"><div class="detail-label">Hash</div><div class="detail-value mono">${b.hash}</div></div>
        <div class="detail-row"><div class="detail-label">Parent Hash</div><div class="detail-value mono">${b.parent_hash}</div></div>
        <div class="detail-row"><div class="detail-label">Timestamp</div><div class="detail-value">${new Date(b.timestamp * 1000).toLocaleString()} (${timeAgo(b.timestamp)})</div></div>
        <div class="detail-row"><div class="detail-label">Validator</div><div class="detail-value mono"><a href="/address/${b.miner}" onclick="navigate('address', '${b.miner}'); return false;">${b.miner}</a></div></div>
        <div class="detail-row"><div class="detail-label">Transactions</div><div class="detail-value">${b.tx_count}</div></div>
        <div class="detail-row"><div class="detail-label">Gas Used</div><div class="detail-value">${formatNumber(b.gas_used)} / ${formatNumber(b.gas_limit)}</div></div>
        <div class="detail-row"><div class="detail-label">Size</div><div class="detail-value">${formatNumber(b.size)} bytes</div></div>
    `;

    // Block transactions
    document.getElementById('blockTxsList').innerHTML = data.transactions.length > 0
        ? data.transactions.map(tx => `
            <tr>
                <td class="mono"><a href="/tx/${tx.hash}" onclick="navigate('tx', '${tx.hash}'); return false;">${formatHash(tx.hash)}</a></td>
                <td class="mono truncate"><a href="/address/${tx.from_addr}" onclick="navigate('address', '${tx.from_addr}'); return false;">${formatAddr(tx.from_addr)}</a></td>
                <td class="mono truncate"><a href="/address/${tx.to_addr}" onclick="navigate('address', '${tx.to_addr}'); return false;">${formatAddr(tx.to_addr)}</a></td>
                <td>${formatValue(tx.value)}</td>
                <td>${tx.status === 1 ? '<span class="badge badge-success">Success</span>' : '<span class="badge badge-warning">Failed</span>'}</td>
            </tr>
        `).join('')
        : '<tr><td colspan="5" style="text-align:center;color:var(--muted-foreground);">No transactions in this block</td></tr>';
}

// ========== Transaction Detail ==========
async function loadTxDetail(txHash) {
    const data = await api(`/tx/${txHash}`);
    if (!data || !data.transaction) {
        document.getElementById('txDetails').innerHTML = '<div style="padding:2rem;text-align:center;color:var(--muted-foreground);">Transaction not found</div>';
        return;
    }

    const tx = data.transaction;
    const gasPrice = BigInt(tx.gas_price || '0');
    const gasUsed = tx.gas_used || 0;
    const txFee = Number(gasPrice * BigInt(gasUsed)) / 1e18;

    document.getElementById('txDetails').innerHTML = `
        <div class="detail-row"><div class="detail-label">Transaction Hash</div><div class="detail-value mono">${tx.hash}</div></div>
        <div class="detail-row"><div class="detail-label">Status</div><div class="detail-value">${tx.status === 1 ? '<span class="badge badge-success">Success</span>' : '<span class="badge badge-warning">Failed</span>'}</div></div>
        <div class="detail-row"><div class="detail-label">Block</div><div class="detail-value"><a href="/block/${tx.block_number}" onclick="navigate('block', ${tx.block_number}); return false;">${tx.block_number}</a></div></div>
        <div class="detail-row"><div class="detail-label">Timestamp</div><div class="detail-value">${new Date(tx.timestamp * 1000).toLocaleString()} (${timeAgo(tx.timestamp)})</div></div>
        <div class="detail-row"><div class="detail-label">From</div><div class="detail-value mono"><a href="/address/${tx.from_addr}" onclick="navigate('address', '${tx.from_addr}'); return false;">${tx.from_addr}</a></div></div>
        <div class="detail-row"><div class="detail-label">To</div><div class="detail-value mono"><a href="/address/${tx.to_addr}" onclick="navigate('address', '${tx.to_addr}'); return false;">${tx.to_addr || 'Contract Creation'}</a></div></div>
        <div class="detail-row"><div class="detail-label">Value</div><div class="detail-value">${formatValue(tx.value)}</div></div>
        <div class="detail-row"><div class="detail-label">Transaction Fee</div><div class="detail-value">${txFee.toFixed(9)} NPY</div></div>
        <div class="detail-row"><div class="detail-label">Gas Price</div><div class="detail-value">${Number(gasPrice) / 1e9} Gwei</div></div>
        <div class="detail-row"><div class="detail-label">Gas Used</div><div class="detail-value">${formatNumber(gasUsed)} / ${formatNumber(tx.gas)}</div></div>
        <div class="detail-row"><div class="detail-label">Nonce</div><div class="detail-value">${tx.nonce}</div></div>
        ${tx.input_data && tx.input_data !== '0x' ? `<div class="detail-row"><div class="detail-label">Input Data</div><div class="detail-value mono" style="word-break:break-all;font-size:0.75rem;">${tx.input_data}</div></div>` : ''}
    `;
}

// ========== Address Detail ==========
async function loadAddressDetail(address, page = 1) {
    currentAddress = address;
    addressPage = page;

    const data = await api(`/address/${address}?page=${page}&limit=25`);
    if (!data) {
        document.getElementById('addressStats').innerHTML = '';
        document.getElementById('addressTxsList').innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--muted-foreground);">Error loading address</td></tr>';
        return;
    }

    // Stats
    const balance = BigInt(data.balance || '0');
    const balanceNpy = Number(balance) / 1e18;

    document.getElementById('addressStats').innerHTML = `
        <div class="stat-card">
            <h3>Address</h3>
            <div class="value mono" style="font-size:0.9rem;word-break:break-all;">${address}</div>
        </div>
        <div class="stat-card">
            <h3>Balance</h3>
            <div class="value">${balanceNpy.toFixed(4)}</div>
            <div class="sub">NPY</div>
        </div>
        <div class="stat-card">
            <h3>Transactions</h3>
            <div class="value">${formatNumber(data.transactionCount)}</div>
            <div class="sub">Total txs</div>
        </div>
    `;

    // Transactions
    document.getElementById('addressTxsList').innerHTML = data.transactions.length > 0
        ? data.transactions.map(tx => {
            const isOut = tx.from_addr.toLowerCase() === address.toLowerCase();
            return `
                <tr>
                    <td class="mono"><a href="/tx/${tx.hash}" onclick="navigate('tx', '${tx.hash}'); return false;">${formatHash(tx.hash)}</a></td>
                    <td><a href="/block/${tx.block_number}" onclick="navigate('block', ${tx.block_number}); return false;">${tx.block_number}</a></td>
                    <td class="mono truncate">${isOut ? '<span class="badge badge-warning">OUT</span>' : ''} ${formatAddr(tx.from_addr)}</td>
                    <td class="mono truncate">${!isOut ? '<span class="badge badge-success">IN</span>' : ''} ${formatAddr(tx.to_addr)}</td>
                    <td>${formatValue(tx.value)}</td>
                </tr>
            `;
        }).join('')
        : '<tr><td colspan="5" style="text-align:center;color:var(--muted-foreground);">No transactions found</td></tr>';

    renderPagination('addressPagination', data.page, data.pages, (p) => loadAddressDetail(currentAddress, p));
}

// ========== Pagination ==========
function renderPagination(containerId, currentPage, totalPages, callback) {
    if (totalPages <= 1) {
        document.getElementById(containerId).innerHTML = '';
        return;
    }

    document.getElementById(containerId).innerHTML = `
        <button ${currentPage <= 1 ? 'disabled' : ''} onclick="(${callback})(1)">First</button>
        <button ${currentPage <= 1 ? 'disabled' : ''} onclick="(${callback})(${currentPage - 1})">Prev</button>
        <span>Page ${currentPage} of ${totalPages}</span>
        <button ${currentPage >= totalPages ? 'disabled' : ''} onclick="(${callback})(${currentPage + 1})">Next</button>
        <button ${currentPage >= totalPages ? 'disabled' : ''} onclick="(${callback})(${totalPages})">Last</button>
    `;
}

// ========== Search ==========
async function doSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) return;

    const result = await api(`/search?q=${encodeURIComponent(query)}`);

    if (result && result.type) {
        if (result.type === 'block') navigate('block', result.data.number);
        else if (result.type === 'transaction') navigate('tx', result.data.hash);
        else if (result.type === 'address') navigate('address', result.data.address);
    } else {
        // Try as address if it looks like one
        if (query.startsWith('0x') && query.length === 42) {
            navigate('address', query);
        } else {
            alert('No results found for: ' + query);
        }
    }
}

// ========== Router ==========
function initRouter() {
    const path = window.location.pathname;

    if (path.startsWith('/block/')) {
        navigate('block', path.split('/')[2]);
    } else if (path.startsWith('/tx/')) {
        navigate('tx', path.split('/')[2]);
    } else if (path.startsWith('/address/')) {
        navigate('address', path.split('/')[2]);
    } else if (path === '/blocks') {
        navigate('blocks');
    } else if (path === '/transactions') {
        navigate('transactions');
    } else if (path === '/validators') {
        navigate('validators');
    } else if (path === '/network') {
        navigate('network');
    } else {
        navigate('home');
    }
}

// Handle browser back/forward
window.onpopstate = (e) => {
    if (e.state) {
        navigate(e.state.view, e.state.param);
    } else {
        initRouter();
    }
};

// ========== Init ==========
document.addEventListener('DOMContentLoaded', () => {
    // Enter key for search
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') doSearch();
    });

    // Initialize router
    initRouter();

    // Auto-refresh dashboard every 10 seconds
    setInterval(() => {
        if (currentView === 'home') loadDashboard();
    }, 10000);
});

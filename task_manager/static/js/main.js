// static/js/main.js
(function(){
    /* ======= Config & helpers ======= */
    const apiBase = '/api/tasks/';
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    /* ======= State ======= */
    let currentFilter = 'all';
    let currentQuery = '';
    let currentOrdering = 'newest';
    let tasksCache = [];

    /* ======= Utils ======= */
    function qs(params) {
        const esc = encodeURIComponent;
        const parts = [];
        for (const k in params) {
            if (params[k] === null || params[k] === undefined || params[k] === '') continue;
            parts.push(`${esc(k)}=${esc(params[k])}`);
        }
        return parts.length ? '?' + parts.join('&') : '';
    }
    function escapeHtml(s){ return (s||'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]); }

    function getStatusBadge(status) {
        let color, text, icon;
        switch(status) {
            case 'todo':
                color = 'secondary'; text = 'To Do'; icon = 'bi-list-ul'; break;
            case 'inprogress':
                color = 'warning'; text = 'In Progress'; icon = 'bi-hourglass-split'; break;
            case 'done':
                color = 'success'; text = 'Done'; icon = 'bi-check-circle-fill'; break;
            default:
                color = 'light'; text = 'Unknown'; icon = 'bi-question-circle';
        }
        return `<span class="badge bg-${color} text-uppercase"><i class="bi ${icon} me-1"></i>${text}</span>`;
    }

    /* ======= Fetch & render tasks (respects filters/search/sort) ======= */
    async function fetchTasks() {
        const navInput = document.getElementById('navSearchInput');
        currentQuery = navInput ? navInput.value.trim() : currentQuery;

        const params = {};
        if (currentQuery) params.q = currentQuery;

        if (currentFilter === 'pending') params.status = 'pending';
        else if (currentFilter === 'completed') params.status = 'done';
        else if (currentFilter === 'favorites') params.favorite = '1';

        const orderingMap = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'title_asc': 'title',
            'title_desc': '-title'
        };
        params.ordering = orderingMap[currentOrdering] || orderingMap['newest'];

        const url = apiBase + qs(params);
        try {
            const res = await fetch(url, { credentials: 'same-origin' });
            if (!res.ok) throw new Error('Fetch failed: ' + res.status);
            const data = await res.json();

            // handle paginated and non-paginated responses
            let items = Array.isArray(data) ? data : (Array.isArray(data.results) ? data.results : []);
            // client-side refinement for 'pending'
            if (currentFilter === 'pending') {
                items = items.filter(t => t.status !== 'done');
            }

            tasksCache = items;
            renderTasks(items);
        } catch (err) {
            console.error('fetchTasks', err);
            const container = document.getElementById('tasksList');
            container.innerHTML = '<div class="col-12"><div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Could not load tasks. Try reloading.</div></div>';
        }
    }

    function renderTasks(tasks){
        const container = document.getElementById('tasksList');
        container.innerHTML = '';
        if(!tasks || tasks.length === 0){
            let message = 'No tasks found.';
            if(currentFilter !== 'all' || currentQuery) {
                message = `No ${currentFilter === 'pending' ? 'pending' : currentFilter} tasks found.`;
            }
            container.innerHTML = `<div class="col-12"><div class="alert alert-info border-0 shadow-sm"><i class="bi bi-info-circle me-2"></i>${message}</div></div>`;
            return;
        }

        tasks.forEach(t=>{
            const col = document.createElement('div');
            col.className='col-12 col-sm-6 col-lg-4';

            col.innerHTML = `
                <div class="card shadow-sm h-100">
                    <div class="card-body d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title text-truncate me-3 mb-0 text-dark">
                                ${t.is_favorite ? '<i class="bi bi-star-fill text-warning me-1"></i>' : ''}
                                ${escapeHtml(t.title)}
                            </h5>
                            ${getStatusBadge(t.status)}
                        </div>

                        <p class="card-text text-muted flex-grow-1 small" style="white-space: pre-wrap; word-break: break-word; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                            ${escapeHtml(t.description||'No description.')}
                        </p>

                        <div class="mt-2 pt-2 border-top">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <small class="text-muted"><i class="bi bi-clock me-1"></i>Created: ${new Date(t.created_at).toLocaleDateString()}</small>
                            </div>

                            <div class="d-grid gap-2 d-sm-flex justify-content-md-end">
                                <button class="btn btn-sm btn-outline-primary" onclick="openView(${t.id})">
                                    <i class="bi bi-eye"></i> View
                                </button>

                                <button class="btn btn-sm btn-outline-dark" onclick="openEdit(${t.id})">
                                    <i class="bi bi-pencil-square"></i> Edit
                                </button>

                                <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${t.id})">
                                    <i class="bi bi-trash"></i> Delete
                                </button>

                                <button class="btn btn-sm ${t.is_favorite? 'btn-info' : 'btn-outline-info'}" onclick="toggleFav(${t.id})">
                                    <i class="bi ${t.is_favorite? 'bi-star-fill' : 'bi-star'}"></i> ${t.is_favorite? 'Unfav' : 'Fav'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(col);
        });
    }

    /* ======= Modal Handling (single instances) ======= */
    const taskModalEl = document.getElementById('taskModal');
    const viewModalEl = document.getElementById('viewModal');

    // Use getOrCreateInstance so we only have one instance per modal
    const taskModal = taskModalEl ? bootstrap.Modal.getOrCreateInstance(taskModalEl) : null;
    const viewModal = viewModalEl ? bootstrap.Modal.getOrCreateInstance(viewModalEl) : null;

    // cleanup when modals hide (defensive: remove stray backdrops and reset forms)
    if (taskModalEl) {
        taskModalEl.addEventListener('hidden.bs.modal', () => {
            // Reset form fields
            const form = document.getElementById('taskForm');
            if (form) form.reset();
            const idEl = document.getElementById('taskId');
            if (idEl) idEl.value = '';

            // Defensive cleanup: remove any leftover backdrops and modal-open class
            document.querySelectorAll('.modal-backdrop').forEach(e => e.remove());
            document.body.classList.remove('modal-open');
        });
    }

    if (viewModalEl) {
        viewModalEl.addEventListener('hidden.bs.modal', () => {
            // remove stray backdrops if any
            document.querySelectorAll('.modal-backdrop').forEach(e => e.remove());
            document.body.classList.remove('modal-open');
        });
    }

    /* ======= Modal / form handling ======= */
    const newTaskBtn = document.getElementById('newTaskBtn');
    if (newTaskBtn && taskModal) {
        newTaskBtn.addEventListener('click', ()=>{
            document.getElementById('taskModalTitle').textContent='New Task';
            document.getElementById('taskId').value='';
            document.getElementById('taskTitle').value='';
            document.getElementById('taskDesc').value='';
            document.getElementById('taskStatus').value='todo';
            taskModal.show();
        });
    }

    const taskForm = document.getElementById('taskForm');
    if (taskForm) {
        taskForm.addEventListener('submit', async function(e){
            e.preventDefault();
            const id = document.getElementById('taskId').value;
            const payload = {
                title: document.getElementById('taskTitle').value,
                description: document.getElementById('taskDesc').value,
                status: document.getElementById('taskStatus').value
            };
            try {
                const method = id ? 'PUT' : 'POST';
                const url = id ? apiBase + id + '/' : apiBase;
                const res = await fetch(url, {
                    method: method,
                    headers: {'Content-Type':'application/json', 'X-CSRFToken': csrftoken},
                    credentials:'same-origin',
                    body: JSON.stringify(payload)
                });
                if (!res.ok) {
                    const txt = await res.text();
                    throw new Error('Save failed: ' + res.status + ' ' + txt);
                }
                // Hide and refresh
                if (taskModal) taskModal.hide();
                fetchTasks();
            } catch(err){
                console.error('Task Save Error:', err);
                alert('Error saving task — check console for details.');
            }
        });
    }

    // Edit (load data and open modal)
    window.openEdit = async function(id){
        try {
            const res = await fetch(apiBase + id + '/', { credentials:'same-origin' });
            if (!res.ok) throw new Error('Load failed');
            const data = await res.json();
            document.getElementById('taskModalTitle').textContent=`Edit Task: ${data.title}`;
            document.getElementById('taskId').value = data.id;
            document.getElementById('taskTitle').value = data.title;
            document.getElementById('taskDesc').value = data.description;
            document.getElementById('taskStatus').value = data.status;
            if (taskModal) taskModal.show();
        } catch(err){ console.error(err); alert('Could not load task'); }
    };

    // View-only (new)
    window.openView = async function(id) {
        try {
            const res = await fetch(apiBase + id + '/', { credentials:'same-origin' });
            if (!res.ok) throw new Error('Load failed');
            const t = await res.json();
            document.getElementById('viewModalTitle').textContent = `Task: ${t.title}`;
            document.getElementById('viewTitle').textContent = t.title;
            document.getElementById('viewDescription').textContent = t.description || 'No description.';
            document.getElementById('viewStatus').innerHTML = getStatusBadge(t.status);
            document.getElementById('viewCreated').textContent = `Created: ${new Date(t.created_at).toLocaleString()}`;
            if (viewModal) viewModal.show();
        } catch(err) {
            console.error('openView error', err);
            alert('Could not load task details.');
        }
    };

    // Delete
    window.deleteTask = async function(id){
        if(!confirm('Are you sure you want to permanently delete this task?')) return;
        try {
            const res = await fetch(apiBase + id + '/', { 
                method:'DELETE', 
                headers:{ 'X-CSRFToken': csrftoken }, 
                credentials:'same-origin' 
            });
            if (res.status === 204 || res.ok) {
                 fetchTasks();
            } else {
                const txt = await res.text();
                throw new Error('Delete failed: ' + res.status + ' ' + txt);
            }
        } catch(err){ console.error(err); alert('Delete failed'); }
    };

    // Toggle favorite
    window.toggleFav = async function(id){
        try {
            const res = await fetch(apiBase + id + '/toggle-favorite/', { method:'POST', headers:{ 'X-CSRFToken': csrftoken }, credentials:'same-origin' });
            if (!res.ok) {
                const txt = await res.text();
                throw new Error('Toggle failed: ' + res.status + ' ' + txt);
            }
            if (currentFilter === 'favorites') {
                tasksCache = tasksCache.filter(t => t.id !== id);
                renderTasks(tasksCache);
                return;
            }
            fetchTasks();
        } catch(err){ console.error(err); alert('Could not update favorite'); }
    };

    /* ======= Filter UI ======= */
    const filterGroup = document.getElementById('filterGroup');
    if (filterGroup) {
        filterGroup.addEventListener('click', function(e){
            const btn = e.target.closest('button[data-filter]');
            if (!btn) return;
            const selected = btn.getAttribute('data-filter');
            if (!selected) return;
            [...filterGroup.querySelectorAll('button')].forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = selected;
            fetchTasks();
        });
    }

    /* ======= Sort UI ======= */
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', function(e){
            currentOrdering = e.target.value;
            fetchTasks();
        });
    }

    /* ======= Initial load ======= */
    document.addEventListener('DOMContentLoaded', function(){
        fetchTasks();
    });

})();

// Função de Tema
function toggleTheme() {
    const html = document.documentElement;
    const icon = document.getElementById('theme-icon');
    if (html.getAttribute('data-theme') === 'dark') {
        html.setAttribute('data-theme', 'light');
        icon.classList.replace('ph-moon', 'ph-sun');
    } else {
        html.setAttribute('data-theme', 'dark');
        icon.classList.replace('ph-sun', 'ph-moon');
    }
}

// Função de Pipeline
async function rodarPipeline() {
    const btn = document.getElementById('btn-run');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Processando IA...';
    
    try {
        await fetch('/api/run-pipeline', { method: 'POST' });
        btn.innerHTML = '<i class="ph ph-check"></i> Concluído!';
        btn.classList.replace('btn-tech', 'btn-success');
        
        setTimeout(() => {
            location.reload();
        }, 2000);
        
    } catch (err) {
        alert("Erro ao conectar com o servidor.");
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// --- LÓGICA PRINCIPAL (BUSCA, FILTROS, KPIs) ---
document.addEventListener('DOMContentLoaded', function() {
    console.log("Dashboard JS Carregado 🚀");

    // 1. MAPEAMENTO DE KPIs POR ABA
    const tabButtons = document.querySelectorAll('button[data-bs-toggle="tab"]');
    const mapTabToKpi = {
        '#cards': 'kpi-premios',
        '#eventos': 'kpi-eventos',
        '#timeline': 'kpi-geral',
        '#tabela': 'kpi-geral'
    };

    function updateKpis(targetId) {
        // Esconde todos
        ['kpi-premios', 'kpi-eventos', 'kpi-geral'].forEach(id => {
            const el = document.getElementById(id);
            if(el) el.classList.add('d-none');
        });

        // Mostra o ativo
        const activeKpiId = mapTabToKpi[targetId];
        if (activeKpiId) {
            document.getElementById(activeKpiId).classList.remove('d-none');
        }
    }

    tabButtons.forEach(btn => {
        btn.addEventListener('shown.bs.tab', function (event) {
            const targetId = event.target.getAttribute('data-bs-target');
            updateKpis(targetId);
        });
    });

    // 2. LÓGICA DE BUSCA E FILTROS
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const costFilter = document.getElementById('costFilter');

    function filterItems() {
        const searchTerm = searchInput.value.toLowerCase();
        const statusValue = statusFilter.value;
        const costValue = costFilter.value;

        // Seleciona todos os itens marcados
        const items = document.querySelectorAll('.searchable-item');
        let visibleCount = 0;

        items.forEach(item => {
            // Pega dados do HTML
            const itemSearchData = (item.getAttribute('data-search') || '').toLowerCase();
            const itemStatus = item.getAttribute('data-status');
            const itemCost = item.getAttribute('data-custo');

            // Verifica condições
            const matchesSearch = itemSearchData.includes(searchTerm);
            const matchesStatus = statusValue === 'all' || itemStatus === statusValue;
            const matchesCost = costValue === 'all' || itemCost === costValue;

            // Mostra ou Esconde
            if (matchesSearch && matchesStatus && matchesCost) {
                item.classList.remove('d-none');
                visibleCount++;
                
                // Fix para timeline
                if(item.classList.contains('timeline-item')) {
                    item.style.display = 'block'; 
                }
            } else {
                item.classList.add('d-none');
                
                if(item.classList.contains('timeline-item')) {
                    item.style.display = 'none';
                }
            }
        });

        // FEEDBACK "SEM RESULTADOS"
        const noResultsId = 'no-results-message';
        let noResultsEl = document.getElementById(noResultsId);

        if (visibleCount === 0) {
            if (!noResultsEl) {
                const msg = document.createElement('div');
                msg.id = noResultsId;
                msg.className = 'text-center py-5';
                msg.innerHTML = `
                    <div style="opacity: 0.5;">
                        <i class="ph ph-magnifying-glass" style="font-size: 3rem; margin-bottom: 10px;"></i>
                        <h5 class="fw-normal">Nenhum resultado encontrado</h5>
                        <p class="small">Tente ajustar os filtros ou a busca.</p>
                    </div>
                `;
                document.querySelector('.search-container').after(msg);
            }
        } else {
            if (noResultsEl) noResultsEl.remove();
        }

        // Limpa meses vazios na timeline
        hideEmptyMonths();
    }

    function hideEmptyMonths() {
        const months = document.querySelectorAll('.timeline-month');
        months.forEach(month => {
            let nextEl = month.nextElementSibling;
            let hasVisibleItems = false;
            
            while(nextEl && !nextEl.classList.contains('timeline-month')) {
                if (nextEl.classList.contains('timeline-item') && !nextEl.classList.contains('d-none')) {
                    if(nextEl.style.display !== 'none') {
                        hasVisibleItems = true;
                        break;
                    }
                }
                nextEl = nextEl.nextElementSibling;
            }

            month.style.display = hasVisibleItems ? 'block' : 'none';
        });
    }

    // Adiciona Listeners
    if(searchInput) searchInput.addEventListener('input', filterItems);
    if(statusFilter) statusFilter.addEventListener('change', filterItems);
    if(costFilter) costFilter.addEventListener('change', filterItems);
});
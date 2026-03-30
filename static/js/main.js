$(document).ready(function () {

    let suggestionTimer = null;

    $('#description').on('input', function () {
        const text = $(this).val();

        clearTimeout(suggestionTimer);

        if (text.length < 30) {
            $('#aiSuggestionBox').slideUp(200);
            return;
        }

        suggestionTimer = setTimeout(function () {
            $.ajax({
                url: '/api/ai-suggest',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ text: text }),
                success: function (data) {
                    if (data.suggestion) {
                        $('#aiSuggestionText').text(data.suggestion);
                        $('#aiSuggestionBox').slideDown(300);
                    }
                },
                error: function () {
                    console.log('AI suggestion unavailable');
                }
            });
        }, 1500); 
    });


    $('#btnAiReply').on('click', function () {
        const btn = $(this);
        const complaintId = btn.data('complaint-id');
        const spinner = $('#aiReplySpinner');

        btn.prop('disabled', true);
        spinner.removeClass('d-none');

        $.ajax({
            url: '/api/ai-reply',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ complaint_id: complaintId }),
            success: function (data) {
                if (data.reply) {
                    // Set the reply text in the textarea for admin to review/edit before sending
                    $('#replyText').val(data.reply);
                    $('#replyText').focus();
                }
            },
            error: function (xhr) {
                alert('Failed to generate AI reply. Please try again.');
                console.error('AI Reply Error:', xhr.responseText);
            },
            complete: function () {
                btn.prop('disabled', false);
                spinner.addClass('d-none');
            }
        });
    });


    // AI Weekly Summary (Dashboard — Admin)
    $('#btnWeeklySummary').on('click', function () {
        const btn = $(this);
        const spinner = $('#summarySpinner');

        btn.prop('disabled', true);
        spinner.removeClass('d-none');

        $.ajax({
            url: '/api/ai-summary',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({}),
            success: function (data) {
                if (data.summary) {
                    $('#summaryText').text(data.summary);
                    $('#summaryCard').slideDown(300);
                }
            },
            error: function (xhr) {
                alert('Failed to generate summary. Please try again.');
                console.error('Summary Error:', xhr.responseText);
            },
            complete: function () {
                btn.prop('disabled', false);
                spinner.addClass('d-none');
            }
        });
    });


    // Dashboard: Search & Filter
    function filterTable() {
        const search = $('#searchInput').val().toLowerCase();
        const deptFilter = $('#filterDept').val();
        const statusFilter = $('#filterStatus').val();

        $('.complaint-row').each(function () {
            const row = $(this);
            const matchSearch = !search || row.data('search').includes(search);
            const matchDept = !deptFilter || row.data('dept') === deptFilter;
            const matchStatus = !statusFilter || row.data('status') === statusFilter;

            row.toggle(matchSearch && matchDept && matchStatus);
        });
    }

    $('#searchInput').on('input', filterTable);
    $('#filterDept').on('change', filterTable);
    $('#filterStatus').on('change', filterTable);


    // Dashboard: Chart.js Initialization
    if (typeof deptLabels !== 'undefined' && document.getElementById('deptChart')) {
        // Color palette
        const chartColors = [
            '#6366f1', '#a855f7', '#ec4899', '#f43f5e',
            '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4'
        ];

        // Department Bar Chart
        new Chart(document.getElementById('deptChart'), {
            type: 'bar',
            data: {
                labels: deptLabels,
                datasets: [{
                    label: 'Complaints',
                    data: deptCounts,
                    backgroundColor: chartColors.slice(0, deptLabels.length),
                    borderRadius: 8,
                    borderSkipped: false,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, font: { family: 'Inter' } },
                        grid: { color: 'rgba(0,0,0,0.04)' }
                    },
                    x: {
                        ticks: { font: { family: 'Inter', size: 11 } },
                        grid: { display: false }
                    }
                }
            }
        });

        // Weekly Trend Line Chart
        new Chart(document.getElementById('trendChart'), {
            type: 'line',
            data: {
                labels: trendLabels,
                datasets: [{
                    label: 'Complaints',
                    data: trendCounts,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, font: { family: 'Inter' } },
                        grid: { color: 'rgba(0,0,0,0.04)' }
                    },
                    x: {
                        ticks: { font: { family: 'Inter' } },
                        grid: { display: false }
                    }
                }
            }
        });
    }
    setTimeout(function () {
        $('.alert').alert('close');
    }, 5000);

});

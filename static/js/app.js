// 通用弹窗
function showModal(title, bodyHtml, footerHtml) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = bodyHtml;
    var footer = document.querySelector('.modal-footer');
    if (footerHtml) {
        if (!footer) {
            footer = document.createElement('div');
            footer.className = 'modal-footer';
            document.getElementById('modalBox').appendChild(footer);
        }
        footer.innerHTML = footerHtml;
    } else if (footer) {
        footer.remove();
    }
    document.getElementById('modalOverlay').style.display = 'flex';
}

function hideModal() {
    document.getElementById('modalOverlay').style.display = 'none';
}

// 点击遮罩关闭
document.getElementById('modalOverlay').addEventListener('click', function(e) {
    if (e.target === this) hideModal();
});

// Toast 提示
function showToast(message, type) {
    type = type || 'success';
    var toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast ' + type;
    toast.style.display = 'block';
    setTimeout(function() {
        toast.style.display = 'none';
    }, 2500);
}

// 确认对话框
function confirmDialog(message, onConfirm) {
    showModal('确认操作',
        '<p>' + message + '</p>',
        '<button class="btn btn-secondary" onclick="hideModal()">取消</button>' +
        '<button class="btn btn-danger" id="confirmBtn">确认</button>'
    );
    document.getElementById('confirmBtn').onclick = function() {
        hideModal();
        onConfirm();
    };
}

// AJAX 提交表单
function ajaxSubmit(url, formData, method, onSuccess) {
    method = method || 'POST';
    fetch(url, {
        method: method,
        body: formData,
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            showToast(data.message || '操作成功', 'success');
            if (onSuccess) onSuccess(data);
        } else {
            showToast(data.message || '操作失败', 'error');
        }
    })
    .catch(function() {
        showToast('网络错误，请重试', 'error');
    });
}

// AJAX JSON 请求
function ajaxRequest(url, data, method, onSuccess) {
    method = method || 'POST';
    var options = {
        method: method,
        headers: {'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'}
    };
    if (data) options.body = JSON.stringify(data);
    fetch(url, options)
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            showToast(data.message || '操作成功', 'success');
            if (onSuccess) onSuccess(data);
        } else {
            showToast(data.message || '操作失败', 'error');
        }
    })
    .catch(function() {
        showToast('网络错误，请重试', 'error');
    });
}

// 格式化金额
function fmtMoney(v) {
    if (v === null || v === undefined || v === '') return '0.00';
    return parseFloat(v).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}

// 通用Excel导入
function doImport(url) {
    var fileInput = document.getElementById('importFile');
    if (!fileInput || !fileInput.files[0]) {
        showToast('请选择文件', 'error');
        return;
    }
    var fd = new FormData();
    fd.append('file', fileInput.files[0]);
    fetch(url, {method: 'POST', body: fd})
    .then(function(r){return r.json();})
    .then(function(data){
        if (data.success) {
            showToast(data.message, 'success');
            setTimeout(function(){ location.reload(); }, 1000);
        } else {
            showToast(data.message, 'error');
        }
        fileInput.value = '';
    })
    .catch(function(){
        showToast('导入失败，请检查文件格式', 'error');
        fileInput.value = '';
    });
}

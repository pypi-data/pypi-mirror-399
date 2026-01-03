# ==================== 前端页面 ====================
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

frontend_route = APIRouter()


@frontend_route.get("/", response_class=HTMLResponse)
async def index():
    """
    返回前端 HTML 页面
    """
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Casbin ACL 示例</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            line-height: 1.6;
        }
        
        .user-selector {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        
        .user-selector label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #333;
        }
        
        .user-selector select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .content-full {
            grid-column: 1 / -1;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            border-bottom: 2px solid #ddd;
        }
        
        .tab {
            padding: 10px 20px;
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            font-size: 14px;
            color: #666;
            transition: all 0.3s;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: bold;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .table-container {
            overflow-x: auto;
            margin-top: 15px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background: #f7fafc;
            font-weight: bold;
            color: #333;
        }
        
        tr:hover {
            background: #f7fafc;
        }
        
        .btn-small {
            padding: 5px 10px;
            font-size: 12px;
        }
        
        .section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-success {
            background: #48bb78;
            color: white;
        }
        
        .btn-success:hover {
            background: #38a169;
        }
        
        .btn-danger {
            background: #f56565;
            color: white;
        }
        
        .btn-danger:hover {
            background: #e53e3e;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 8px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #f7fafc;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .result pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 12px;
            color: #333;
        }
        
        .error {
            border-left-color: #f56565;
            background: #fed7d7;
        }
        
        .success {
            border-left-color: #48bb78;
            background: #c6f6d5;
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FastAPI Casbin ACL 示例</h1>
            <p>这是一个完整的示例应用，展示了如何使用 FastAPI、SQLModel、aiosqlite 和 Casbin ACL 构建带权限控制的 Web 应用。</p>
            <p><strong>提示：</strong>切换用户查看不同的权限效果。用户 ID 1 通常是管理员，其他用户是普通用户。权限策略使用用户 ID 进行匹配。</p>
        </div>
        
        <div class="user-selector">
            <label for="userId">当前用户 ID：</label>
            <select id="userId" onchange="updateUserId()">
                <option value="">请选择用户...</option>
            </select>
            <p style="margin-top: 10px; font-size: 12px; color: #666;">
                提示：用户 ID 在用户创建后自动分配。首次使用请先创建用户或等待初始化完成。
            </p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>👥 用户管理</h2>
                <div class="button-group">
                    <button class="btn-primary" onclick="listUsers()">获取用户列表</button>
                    <button class="btn-primary" onclick="showGetUserForm()">获取用户详情</button>
                    <button class="btn-success" onclick="showCreateUserForm()">创建用户</button>
                </div>
                <div id="getUserForm" style="display: none;">
                    <div class="form-group">
                        <label>用户 ID：</label>
                        <input type="number" id="getUserId" placeholder="输入用户 ID">
                    </div>
                    <button class="btn-primary" onclick="getUser()">查询</button>
                    <button onclick="hideGetUserForm()">取消</button>
                </div>
                <div id="createUserForm" style="display: none;">
                    <div class="form-group">
                        <label>用户名：</label>
                        <input type="text" id="newUsername" placeholder="输入用户名">
                    </div>
                    <div class="form-group">
                        <label>邮箱：</label>
                        <input type="email" id="newEmail" placeholder="输入邮箱">
                    </div>
                    <button class="btn-success" onclick="createUser()">创建</button>
                    <button onclick="hideCreateUserForm()">取消</button>
                </div>
                <div id="usersResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="section">
                <h2>📦 订单管理</h2>
                <div class="button-group">
                    <button class="btn-primary" onclick="listOrders()">获取订单列表</button>
                    <button class="btn-primary" onclick="showGetOrderForm()">获取订单详情 (ABAC(未完成))</button>
                    <button class="btn-success" onclick="showCreateOrderForm()">创建订单</button>
                    <button class="btn-success" onclick="showUpdateOrderForm()">更新订单 (ABAC(未完成))</button>
                    <button class="btn-danger" onclick="showDeleteOrderForm()">删除订单 (ABAC(未完成))</button>
                </div>
                <div id="getOrderForm" style="display: none;">
                    <div class="form-group">
                        <label>订单 ID：</label>
                        <input type="number" id="getOrderId" placeholder="输入订单 ID">
                    </div>
                    <button class="btn-primary" onclick="getOrder()">查询</button>
                    <button onclick="hideGetOrderForm()">取消</button>
                </div>
                <div id="createOrderForm" style="display: none;">
                    <div class="form-group">
                        <label>订单标题：</label>
                        <input type="text" id="orderTitle" placeholder="输入订单标题">
                    </div>
                    <div class="form-group">
                        <label>描述：</label>
                        <textarea id="orderDesc" placeholder="输入订单描述"></textarea>
                    </div>
                    <div class="form-group">
                        <label>金额：</label>
                        <input type="number" id="orderAmount" placeholder="输入金额" step="0.01">
                    </div>
                    <button class="btn-success" onclick="createOrder()">创建</button>
                    <button onclick="hideCreateOrderForm()">取消</button>
                </div>
                <div id="updateOrderForm" style="display: none;">
                    <div class="form-group">
                        <label>订单 ID：</label>
                        <input type="number" id="updateOrderId" placeholder="输入订单 ID">
                    </div>
                    <div class="form-group">
                        <label>订单标题：</label>
                        <input type="text" id="updateOrderTitle" placeholder="输入新标题（可选）">
                    </div>
                    <div class="form-group">
                        <label>描述：</label>
                        <textarea id="updateOrderDesc" placeholder="输入新描述（可选）"></textarea>
                    </div>
                    <div class="form-group">
                        <label>金额：</label>
                        <input type="number" id="updateOrderAmount" placeholder="输入新金额（可选）" step="0.01">
                    </div>
                    <div class="form-group">
                        <label>状态：</label>
                        <select id="updateOrderStatus">
                            <option value="">不修改</option>
                            <option value="pending">pending</option>
                            <option value="completed">completed</option>
                            <option value="cancelled">cancelled</option>
                        </select>
                    </div>
                    <button class="btn-success" onclick="updateOrder()">更新</button>
                    <button onclick="hideUpdateOrderForm()">取消</button>
                </div>
                <div id="deleteOrderForm" style="display: none;">
                    <div class="form-group">
                        <label>订单 ID：</label>
                        <input type="number" id="deleteOrderId" placeholder="输入订单 ID">
                    </div>
                    <button class="btn-danger" onclick="deleteOrder()">删除</button>
                    <button onclick="hideDeleteOrderForm()">取消</button>
                </div>
                <div id="ordersResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="section content-full">
                <h2>🔐 权限管理</h2>
                <div class="tabs">
                    <button class="tab active" onclick="switchTab('policies', this)">策略 (Policies)</button>
                    <button class="tab" onclick="switchTab('role-bindings', this)">角色绑定 (Role Bindings)</button>
                    <button class="tab" onclick="switchTab('permissions', this)">权限列表 (Permissions)</button>
                    <button class="tab" onclick="switchTab('api-mappings', this)">API 映射 (API Mappings)</button>
                </div>
                
                <!-- 策略 Tab -->
                <div id="policies-tab" class="tab-content active">
                    <div class="button-group">
                        <button class="btn-primary" onclick="loadPolicies()">刷新策略列表</button>
                        <button class="btn-success" onclick="showCreatePolicyForm()">创建策略</button>
                    </div>
                    <div id="createPolicyForm" style="display: none; margin-top: 15px;">
                        <div class="form-group">
                            <label>角色 (Role):</label>
                            <select id="policyRole" style="width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;">
                                <option value="">请选择或输入角色...</option>
                            </select>
                            <input type="text" id="policyRoleInput" placeholder="或输入新角色" style="width: 100%; margin-top: 5px; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;" onkeyup="searchRoles(this.value, 'policyRole')">
                        </div>
                        <div class="form-group">
                            <label>权限 (Permission):</label>
                            <select id="policyPermission" style="width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;">
                                <option value="">请选择或输入权限...</option>
                            </select>
                            <input type="text" id="policyPermissionInput" placeholder="或输入新权限" style="width: 100%; margin-top: 5px; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;" onkeyup="searchPermissions(this.value, 'policyPermission')">
                        </div>
                        <div class="form-group">
                            <label>操作 (Action):</label>
                            <input type="text" id="policyAction" placeholder="例如: read, write, delete" value="multiple">
                        </div>
                        <button class="btn-success" onclick="createPolicy()">创建</button>
                        <button onclick="hideCreatePolicyForm()">取消</button>
                    </div>
                    <div id="policiesResult" class="table-container"></div>
                </div>
                
                <!-- 角色绑定 Tab -->
                <div id="role-bindings-tab" class="tab-content">
                    <div class="button-group">
                        <button class="btn-primary" onclick="loadRoleBindings()">刷新角色绑定</button>
                        <button class="btn-success" onclick="showCreateRoleBindingForm()">创建角色绑定</button>
                    </div>
                    <div id="createRoleBindingForm" style="display: none; margin-top: 15px;">
                        <div class="form-group">
                            <label>用户 ID (User ID):</label>
                            <input type="text" id="roleBindingUser" placeholder="例如: 1">
                        </div>
                        <div class="form-group">
                            <label>角色 (Role):</label>
                            <select id="roleBindingRole" style="width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;">
                                <option value="">请选择或输入角色...</option>
                            </select>
                            <input type="text" id="roleBindingRoleInput" placeholder="或输入新角色" style="width: 100%; margin-top: 5px; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;" onkeyup="searchRoles(this.value, 'roleBindingRole')">
                        </div>
                        <button class="btn-success" onclick="createRoleBinding()">创建</button>
                        <button onclick="hideCreateRoleBindingForm()">取消</button>
                    </div>
                    <div id="roleBindingsResult" class="table-container"></div>
                </div>
                
                <!-- 权限列表 Tab -->
                <div id="permissions-tab" class="tab-content">
                    <div class="button-group">
                        <button class="btn-primary" onclick="loadPermissions()">刷新权限列表</button>
                        <button class="btn-success" onclick="showCreatePermissionMappingForm()">创建权限映射</button>
                    </div>
                    <div id="createPermissionMappingForm" style="display: none; margin-top: 15px;">
                        <div class="form-group">
                            <label>权限 (Permission):</label>
                            <select id="permissionMappingPermission" style="width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;">
                                <option value="">请选择或输入权限...</option>
                            </select>
                            <input type="text" id="permissionMappingPermissionInput" placeholder="或输入新权限" style="width: 100%; margin-top: 5px; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px;" onkeyup="searchPermissions(this.value, 'permissionMappingPermission')">
                        </div>
                        <div class="form-group">
                            <label>API 名称 (多选):</label>
                            <select id="permissionMappingApiNames" multiple style="width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px; min-height: 150px;">
                            </select>
                            <p style="margin-top: 5px; font-size: 12px; color: #666;">提示：按住 Ctrl (Windows) 或 Cmd (Mac) 键进行多选</p>
                        </div>
                        <button class="btn-success" onclick="createPermissionMapping()">创建</button>
                        <button onclick="hideCreatePermissionMappingForm()">取消</button>
                    </div>
                    <div id="permissionsResult" class="table-container"></div>
                </div>
                
                <!-- API 映射 Tab -->
                <div id="api-mappings-tab" class="tab-content">
                    <div class="button-group">
                        <button class="btn-primary" onclick="loadApiMappings()">刷新 API 映射</button>
                    </div>
                    <div id="apiMappingsResult" class="table-container"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentUserId = '';
        
        // 页面加载时获取用户列表并填充选择器
        async function loadUsers() {
            try {
                // 使用一个临时用户来获取用户列表（这里简化处理，实际应该有一个公开的接口）
                // 或者我们可以硬编码初始用户 ID（1, 2, 3）
                // 为了演示，我们先尝试获取用户列表
                const response = await fetch('/api/users', {
                    headers: {
                        'X-User-ID': '1',  // 使用管理员 ID 获取列表
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const users = await response.json();
                    const select = document.getElementById('userId');
                    select.innerHTML = '<option value="">请选择用户...</option>';
                    
                    users.forEach(user => {
                        const option = document.createElement('option');
                        option.value = user.id.toString();
                        option.textContent = `${user.username} (ID: ${user.id})${user.id === 1 ? ' - 管理员' : ' - 普通用户'}`;
                        select.appendChild(option);
                    });
                    
                    // 默认选择第一个用户
                    if (users.length > 0) {
                        select.value = users[0].id.toString();
                        currentUserId = users[0].id.toString();
                    }
                } else {
                    // 如果获取失败，使用硬编码的初始用户 ID
                    const select = document.getElementById('userId');
                    select.innerHTML = `
                        <option value="">请选择用户...</option>
                        <option value="1">Alice (ID: 1) - 管理员</option>
                        <option value="2">Bob (ID: 2) - 普通用户</option>
                        <option value="3">Charlie (ID: 3) - 普通用户</option>
                    `;
                }
            } catch (error) {
                // 如果出错，使用硬编码的初始用户 ID
                const select = document.getElementById('userId');
                select.innerHTML = `
                    <option value="">请选择用户...</option>
                    <option value="1">Alice (ID: 1) - 管理员</option>
                    <option value="2">Bob (ID: 2) - 普通用户</option>
                    <option value="3">Charlie (ID: 3) - 普通用户</option>
                `;
            }
        }
        
        function updateUserId() {
            currentUserId = document.getElementById('userId').value;
            console.log('当前用户 ID:', currentUserId);
            // 重新加载路由列表
            if (currentUserId) {
                loadRoutes();
            }
        }
        
        // 页面加载时初始化
        window.addEventListener('DOMContentLoaded', () => {
            loadUsers();
            // 预加载路由列表，供权限映射使用
            if (currentUserId) {
                loadRoutes();
            }
        });
        
        function getHeaders() {
            return {
                'X-User-ID': currentUserId,
                'Content-Type': 'application/json'
            };
        }
        
        function showResult(elementId, data, isError = false) {
            const element = document.getElementById(elementId);
            element.style.display = 'block';
            element.className = 'result ' + (isError ? 'error' : 'success');
            element.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        
        // 用户管理
        async function listUsers() {
            try {
                const response = await fetch('/api/users', {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    showResult('usersResult', data);
                } else {
                    showResult('usersResult', data, true);
                }
            } catch (error) {
                showResult('usersResult', {error: error.message}, true);
            }
        }
        
        function showGetUserForm() {
            document.getElementById('getUserForm').style.display = 'block';
            document.getElementById('createUserForm').style.display = 'none';
        }
        
        function hideGetUserForm() {
            document.getElementById('getUserForm').style.display = 'none';
        }
        
        async function getUser() {
            const userId = document.getElementById('getUserId').value;
            
            if (!userId) {
                alert('请输入用户 ID');
                return;
            }
            
            try {
                const response = await fetch(`/api/users/${userId}`, {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    showResult('usersResult', data);
                    hideGetUserForm();
                    document.getElementById('getUserId').value = '';
                } else {
                    showResult('usersResult', data, true);
                }
            } catch (error) {
                showResult('usersResult', {error: error.message}, true);
            }
        }
        
        function showCreateUserForm() {
            document.getElementById('createUserForm').style.display = 'block';
            document.getElementById('getUserForm').style.display = 'none';
        }
        
        function hideCreateUserForm() {
            document.getElementById('createUserForm').style.display = 'none';
        }
        
        async function createUser() {
            const username = document.getElementById('newUsername').value;
            const email = document.getElementById('newEmail').value;
            
            if (!username || !email) {
                alert('请填写所有字段');
                return;
            }
            
            try {
                const response = await fetch('/api/users', {
                    method: 'POST',
                    headers: getHeaders(),
                    body: JSON.stringify({username, email})
                });
                const data = await response.json();
                if (response.ok) {
                    showResult('usersResult', data);
                    hideCreateUserForm();
                    document.getElementById('newUsername').value = '';
                    document.getElementById('newEmail').value = '';
                } else {
                    showResult('usersResult', data, true);
                }
            } catch (error) {
                showResult('usersResult', {error: error.message}, true);
            }
        }
        
        // 订单管理
        async function listOrders() {
            try {
                const response = await fetch('/api/orders', {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    showResult('ordersResult', data);
                } else {
                    showResult('ordersResult', data, true);
                }
            } catch (error) {
                showResult('ordersResult', {error: error.message}, true);
            }
        }
        
        function showGetOrderForm() {
            document.getElementById('getOrderForm').style.display = 'block';
            document.getElementById('createOrderForm').style.display = 'none';
            document.getElementById('updateOrderForm').style.display = 'none';
            document.getElementById('deleteOrderForm').style.display = 'none';
        }
        
        function hideGetOrderForm() {
            document.getElementById('getOrderForm').style.display = 'none';
        }
        
        async function getOrder() {
            const orderId = document.getElementById('getOrderId').value;
            
            if (!orderId) {
                alert('请输入订单 ID');
                return;
            }
            
            try {
                const response = await fetch(`/api/orders/${orderId}`, {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    showResult('ordersResult', data);
                    hideGetOrderForm();
                    document.getElementById('getOrderId').value = '';
                } else {
                    showResult('ordersResult', data, true);
                }
            } catch (error) {
                showResult('ordersResult', {error: error.message}, true);
            }
        }
        
        function showCreateOrderForm() {
            document.getElementById('createOrderForm').style.display = 'block';
            document.getElementById('getOrderForm').style.display = 'none';
            document.getElementById('updateOrderForm').style.display = 'none';
            document.getElementById('deleteOrderForm').style.display = 'none';
        }
        
        function hideCreateOrderForm() {
            document.getElementById('createOrderForm').style.display = 'none';
        }
        
        async function createOrder() {
            const title = document.getElementById('orderTitle').value;
            const description = document.getElementById('orderDesc').value;
            const amount = parseFloat(document.getElementById('orderAmount').value);
            
            if (!title || !amount) {
                alert('请填写标题和金额');
                return;
            }
            
            try {
                const response = await fetch('/api/orders', {
                    method: 'POST',
                    headers: getHeaders(),
                    body: JSON.stringify({title, description, amount})
                });
                const data = await response.json();
                if (response.ok) {
                    showResult('ordersResult', data);
                    hideCreateOrderForm();
                    document.getElementById('orderTitle').value = '';
                    document.getElementById('orderDesc').value = '';
                    document.getElementById('orderAmount').value = '';
                } else {
                    showResult('ordersResult', data, true);
                }
            } catch (error) {
                showResult('ordersResult', {error: error.message}, true);
            }
        }
        
        function showUpdateOrderForm() {
            document.getElementById('updateOrderForm').style.display = 'block';
            document.getElementById('getOrderForm').style.display = 'none';
            document.getElementById('createOrderForm').style.display = 'none';
            document.getElementById('deleteOrderForm').style.display = 'none';
        }
        
        function hideUpdateOrderForm() {
            document.getElementById('updateOrderForm').style.display = 'none';
        }
        
        async function updateOrder() {
            const orderId = document.getElementById('updateOrderId').value;
            const title = document.getElementById('updateOrderTitle').value;
            const description = document.getElementById('updateOrderDesc').value;
            const amount = document.getElementById('updateOrderAmount').value;
            const status = document.getElementById('updateOrderStatus').value;
            
            if (!orderId) {
                alert('请输入订单 ID');
                return;
            }
            
            const updateData = {};
            if (title) updateData.title = title;
            if (description) updateData.description = description;
            if (amount) updateData.amount = parseFloat(amount);
            if (status) updateData.status = status;
            
            if (Object.keys(updateData).length === 0) {
                alert('请至少填写一个要更新的字段');
                return;
            }
            
            try {
                const response = await fetch(`/api/orders/${orderId}`, {
                    method: 'PUT',
                    headers: getHeaders(),
                    body: JSON.stringify(updateData)
                });
                const data = await response.json();
                if (response.ok) {
                    showResult('ordersResult', data);
                    hideUpdateOrderForm();
                    document.getElementById('updateOrderId').value = '';
                    document.getElementById('updateOrderTitle').value = '';
                    document.getElementById('updateOrderDesc').value = '';
                    document.getElementById('updateOrderAmount').value = '';
                    document.getElementById('updateOrderStatus').value = '';
                } else {
                    showResult('ordersResult', data, true);
                }
            } catch (error) {
                showResult('ordersResult', {error: error.message}, true);
            }
        }
        
        function showDeleteOrderForm() {
            document.getElementById('deleteOrderForm').style.display = 'block';
            document.getElementById('getOrderForm').style.display = 'none';
            document.getElementById('createOrderForm').style.display = 'none';
            document.getElementById('updateOrderForm').style.display = 'none';
        }
        
        function hideDeleteOrderForm() {
            document.getElementById('deleteOrderForm').style.display = 'none';
        }
        
        async function deleteOrder() {
            const orderId = document.getElementById('deleteOrderId').value;
            
            if (!orderId) {
                alert('请输入订单 ID');
                return;
            }
            
            if (!confirm(`确定要删除订单 ${orderId} 吗？`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/orders/${orderId}`, {
                    method: 'DELETE',
                    headers: getHeaders()
                });
                
                if (response.ok || response.status === 204) {
                    showResult('ordersResult', {message: `订单 ${orderId} 已成功删除`});
                    hideDeleteOrderForm();
                    document.getElementById('deleteOrderId').value = '';
                } else {
                    const data = await response.json();
                    showResult('ordersResult', data, true);
                }
            } catch (error) {
                showResult('ordersResult', {error: error.message}, true);
            }
        }
        
        // 权限管理功能
        function switchTab(tabName, buttonElement) {
            // 隐藏所有 tab 内容
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            // 移除所有 tab 的 active 状态
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            // 显示选中的 tab
            document.getElementById(tabName + '-tab').classList.add('active');
            // 设置当前按钮为 active
            if (buttonElement) {
                buttonElement.classList.add('active');
            }
            
            // 自动加载对应数据
            if (tabName === 'policies') {
                loadPolicies();
            } else if (tabName === 'role-bindings') {
                loadRoleBindings();
            } else if (tabName === 'permissions') {
                loadPermissions();
                loadRoutes(); // 预加载路由列表
            } else if (tabName === 'api-mappings') {
                loadApiMappings();
            }
        }
        
        // 策略管理
        async function loadPolicies() {
            try {
                const response = await fetch('/api/policies/policy', {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    displayPoliciesTable(data.policies);
                } else {
                    showTableError('policiesResult', data);
                }
            } catch (error) {
                showTableError('policiesResult', {error: error.message});
            }
        }
        
        function displayPoliciesTable(policies) {
            const container = document.getElementById('policiesResult');
            if (policies.length === 0) {
                container.innerHTML = '<p>暂无策略</p>';
                return;
            }
            
            let html = '<table><thead><tr><th>角色 (Role)</th><th>权限 (Permission)</th><th>操作 (Action)</th><th>操作</th></tr></thead><tbody>';
            policies.forEach(policy => {
                html += `<tr>
                    <td>${policy.sub}</td>
                    <td>${policy.obj}</td>
                    <td>${policy.act}</td>
                    <td>
                        <button class="btn-danger btn-small" onclick="deletePolicy('${policy.sub}', '${policy.obj}', '${policy.act}')">删除</button>
                    </td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }
        
        // 搜索角色
        async function searchRoles(query, selectId) {
            try {
                const url = query ? `/api/policies/roles/search?q=${encodeURIComponent(query)}` : '/api/policies/roles/search';
                const response = await fetch(url, {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    const select = document.getElementById(selectId);
                    const currentValue = select.value;
                    select.innerHTML = '<option value="">请选择或输入角色...</option>';
                    if (data.roles && data.roles.length > 0) {
                        data.roles.forEach(role => {
                            const option = document.createElement('option');
                            option.value = role;
                            option.textContent = role;
                            select.appendChild(option);
                        });
                    }
                    // 如果输入框有值，尝试设置为选中
                    const input = document.getElementById(selectId + 'Input');
                    if (input && input.value && data.roles && data.roles.includes(input.value)) {
                        select.value = input.value;
                    } else if (currentValue) {
                        select.value = currentValue;
                    }
                }
            } catch (error) {
                console.error('搜索角色失败:', error);
            }
        }
        
        // 搜索权限
        async function searchPermissions(query, selectId) {
            try {
                const url = query ? `/api/policies/permissions/search?q=${encodeURIComponent(query)}` : '/api/policies/permissions/search';
                const response = await fetch(url, {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    const select = document.getElementById(selectId);
                    const currentValue = select.value;
                    select.innerHTML = '<option value="">请选择或输入权限...</option>';
                    if (data.permissions && data.permissions.length > 0) {
                        data.permissions.forEach(perm => {
                            const option = document.createElement('option');
                            option.value = perm.name;
                            option.textContent = `${perm.name} (${perm.level})`;
                            select.appendChild(option);
                        });
                    }
                    // 如果输入框有值，尝试设置为选中
                    const input = document.getElementById(selectId + 'Input');
                    if (input && input.value) {
                        // 检查是否在权限列表中
                        const found = data.permissions && data.permissions.find(p => p.name === input.value);
                        if (found) {
                            select.value = input.value;
                        }
                    } else if (currentValue) {
                        select.value = currentValue;
                    }
                }
            } catch (error) {
                console.error('搜索权限失败:', error);
            }
        }
        
        async function showCreatePolicyForm() {
            document.getElementById('createPolicyForm').style.display = 'block';
            // 加载角色和权限选项
            await searchRoles('', 'policyRole');
            await searchPermissions('', 'policyPermission');
        }
        
        function hideCreatePolicyForm() {
            document.getElementById('createPolicyForm').style.display = 'none';
            document.getElementById('policyRole').value = '';
            document.getElementById('policyPermission').value = '';
            document.getElementById('policyAction').value = 'multiple';
            document.getElementById('policyRoleInput').value = '';
            document.getElementById('policyPermissionInput').value = '';
        }
        
        async function createPolicy() {
            const roleSelect = document.getElementById('policyRole');
            const roleInput = document.getElementById('policyRoleInput');
            const role = roleSelect.value || roleInput.value;
            
            const permissionSelect = document.getElementById('policyPermission');
            const permissionInput = document.getElementById('policyPermissionInput');
            const permission = permissionSelect.value || permissionInput.value;
            
            const action = document.getElementById('policyAction').value || 'multiple';
            
            if (!role || !permission) {
                alert('请填写角色和权限');
                return;
            }
            
            try {
                const response = await fetch('/api/policies/policy', {
                    method: 'POST',
                    headers: getHeaders(),
                    body: JSON.stringify({sub: role, obj: permission, act: action})
                });
                const data = await response.json();
                if (response.ok) {
                    hideCreatePolicyForm();
                    loadPolicies();
                } else {
                    alert('创建失败: ' + (data.detail || JSON.stringify(data)));
                }
            } catch (error) {
                alert('创建失败: ' + error.message);
            }
        }
        
        async function deletePolicy(role, permission, action) {
            if (!confirm(`确定要删除策略: ${role} -> ${permission} -> ${action}?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/policies/policy', {
                    method: 'DELETE',
                    headers: getHeaders(),
                    body: JSON.stringify({sub: role, obj: permission, act: action})
                });
                if (response.ok || response.status === 204) {
                    loadPolicies();
                } else {
                    const data = await response.json();
                    alert('删除失败: ' + (data.detail || JSON.stringify(data)));
                }
            } catch (error) {
                alert('删除失败: ' + error.message);
            }
        }
        
        // 角色绑定管理
        async function loadRoleBindings() {
            try {
                const response = await fetch('/api/policies/role_bindings', {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    displayRoleBindingsTable(data.list);
                } else {
                    showTableError('roleBindingsResult', data);
                }
            } catch (error) {
                showTableError('roleBindingsResult', {error: error.message});
            }
        }
        
        function displayRoleBindingsTable(bindings) {
            const container = document.getElementById('roleBindingsResult');
            if (bindings.length === 0) {
                container.innerHTML = '<p>暂无角色绑定</p>';
                return;
            }
            
            let html = '<table><thead><tr><th>用户 ID (User ID)</th><th>角色 (Role)</th><th>操作</th></tr></thead><tbody>';
            bindings.forEach(binding => {
                html += `<tr>
                    <td>${binding.user}</td>
                    <td>${binding.role}</td>
                    <td>
                        <button class="btn-danger btn-small" onclick="deleteRoleBinding('${binding.user}', '${binding.role}')">删除</button>
                    </td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }
        
        async function showCreateRoleBindingForm() {
            document.getElementById('createRoleBindingForm').style.display = 'block';
            // 加载角色选项
            await searchRoles('', 'roleBindingRole');
        }
        
        function hideCreateRoleBindingForm() {
            document.getElementById('createRoleBindingForm').style.display = 'none';
            document.getElementById('roleBindingUser').value = '';
            document.getElementById('roleBindingRole').value = '';
            document.getElementById('roleBindingRoleInput').value = '';
        }
        
        async function createRoleBinding() {
            const user = document.getElementById('roleBindingUser').value;
            const roleSelect = document.getElementById('roleBindingRole');
            const roleInput = document.getElementById('roleBindingRoleInput');
            const role = roleSelect.value || roleInput.value;
            
            if (!user || !role) {
                alert('请填写所有字段');
                return;
            }
            
            try {
                const response = await fetch('/api/policies/roles', {
                    method: 'POST',
                    headers: getHeaders(),
                    body: JSON.stringify({user: user, role: role})
                });
                const data = await response.json();
                if (response.ok) {
                    hideCreateRoleBindingForm();
                    loadRoleBindings();
                } else {
                    alert('创建失败: ' + (data.detail || JSON.stringify(data)));
                }
            } catch (error) {
                alert('创建失败: ' + error.message);
            }
        }
        
        async function deleteRoleBinding(user, role) {
            if (!confirm(`确定要删除角色绑定: 用户 ${user} -> 角色 ${role}?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/policies/roles', {
                    method: 'DELETE',
                    headers: getHeaders(),
                    body: JSON.stringify({user: user, role: role})
                });
                if (response.ok || response.status === 204) {
                    loadRoleBindings();
                } else {
                    const data = await response.json();
                    alert('删除失败: ' + (data.detail || JSON.stringify(data)));
                }
            } catch (error) {
                alert('删除失败: ' + error.message);
            }
        }
        
        // 权限列表
        async function loadPermissions() {
            try {
                const response = await fetch('/api/policies/permissions', {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    displayPermissionsTable(data.permissions);
                } else {
                    showTableError('permissionsResult', data);
                }
            } catch (error) {
                showTableError('permissionsResult', {error: error.message});
            }
        }
        
        function displayPermissionsTable(permissions) {
            const container = document.getElementById('permissionsResult');
            if (permissions.length === 0) {
                container.innerHTML = '<p>暂无权限</p>';
                return;
            }
            
            let html = '<table><thead><tr><th>权限名称 (Permission Name)</th><th>级别 (Level)</th></tr></thead><tbody>';
            permissions.forEach(perm => {
                html += `<tr><td>${perm.name}</td><td>${perm.level || '-'}</td></tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }
        
        // 加载路由列表
        let routesList = [];
        async function loadRoutes() {
            try {
                const response = await fetch('/api/policies/routes', {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok && data.routes) {
                    routesList = data.routes;
                    // 更新权限映射表单中的路由选择
                    const select = document.getElementById('permissionMappingApiNames');
                    if (select) {
                        select.innerHTML = '';
                        routesList.forEach(route => {
                            const option = document.createElement('option');
                            option.value = route;
                            option.textContent = route;
                            select.appendChild(option);
                        });
                    }
                }
            } catch (error) {
                console.error('加载路由列表失败:', error);
            }
        }
        
        async function showCreatePermissionMappingForm() {
            document.getElementById('createPermissionMappingForm').style.display = 'block';
            // 加载权限选项和路由列表
            await searchPermissions('', 'permissionMappingPermission');
            await loadRoutes();
        }
        
        function hideCreatePermissionMappingForm() {
            document.getElementById('createPermissionMappingForm').style.display = 'none';
            document.getElementById('permissionMappingPermission').value = '';
            document.getElementById('permissionMappingPermissionInput').value = '';
            const select = document.getElementById('permissionMappingApiNames');
            if (select) {
                Array.from(select.options).forEach(option => {
                    option.selected = false;
                });
            }
        }
        
        async function createPermissionMapping() {
            const permissionSelect = document.getElementById('permissionMappingPermission');
            const permissionInput = document.getElementById('permissionMappingPermissionInput');
            const permission = permissionSelect.value || permissionInput.value;
            
            const select = document.getElementById('permissionMappingApiNames');
            const selectedApiNames = Array.from(select.selectedOptions).map(option => option.value);
            
            if (!permission || selectedApiNames.length === 0) {
                alert('请选择权限和至少一个 API 名称');
                return;
            }
            
            try {
                const response = await fetch(`/api/policies/permission_groups/${encodeURIComponent(permission)}`, {
                    method: 'PUT',
                    headers: getHeaders(),
                    body: JSON.stringify({api_names: selectedApiNames})
                });
                const data = await response.json();
                if (response.ok) {
                    hideCreatePermissionMappingForm();
                    loadPermissions();
                    loadApiMappings();
                } else {
                    alert('创建失败: ' + (data.detail || JSON.stringify(data)));
                }
            } catch (error) {
                alert('创建失败: ' + error.message);
            }
        }
        
        // API 映射管理（只读）
        async function loadApiMappings() {
            try {
                const response = await fetch('/api/policies/permission_mappings', {
                    headers: getHeaders()
                });
                const data = await response.json();
                if (response.ok) {
                    displayApiMappingsTable(data.mappings);
                } else {
                    showTableError('apiMappingsResult', data);
                }
            } catch (error) {
                showTableError('apiMappingsResult', {error: error.message});
            }
        }
        
        function displayApiMappingsTable(mappings) {
            const container = document.getElementById('apiMappingsResult');
            if (mappings.length === 0) {
                container.innerHTML = '<p>暂无 API 映射</p>';
                return;
            }
            
            let html = '<table><thead><tr><th>API 名称 (API Name)</th><th>权限 (Permission)</th></tr></thead><tbody>';
            mappings.forEach(mapping => {
                html += `<tr>
                    <td>${mapping.api_name}</td>
                    <td>${mapping.permission || '-'}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }
        
        function showTableError(elementId, data) {
            const container = document.getElementById(elementId);
            container.innerHTML = '<div class="error" style="padding: 15px;"><pre>' + JSON.stringify(data, null, 2) + '</pre></div>';
        }
        
    </script>
</body>
</html>
    """

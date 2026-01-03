"""
FastAPI + SQLModel + aiosqlite + Casbin ACL 示例应用

这个示例展示了如何使用 fastapi-casbin-acl 构建一个带有权限控制的 Web 应用。
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from examples.frontend_route import frontend_route
from fastapi_casbin_acl.enforcer import acl
from fastapi_casbin_acl.router import casbin_router
from fastapi_casbin_acl.config import ACLConfig
from fastapi_casbin_acl.adapter import SQLModelAdapter
from fastapi_casbin_acl.exceptions import Unauthorized, Forbidden

try:
    # 作为模块导入时使用相对导入
    from .database import init_db, close_db, AsyncSessionLocal
    from .routes import router
except ImportError:
    # 直接运行时使用绝对导入
    from database import init_db, close_db, AsyncSessionLocal
    from routes import router


async def get_user(request: Request):
    user_id_str = request.headers.get("x-user-id")
    return str(user_id_str)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时初始化
    # 1. 初始化数据库
    await init_db()

    # 2. 初始化 Casbin ACL
    # 使用 SQLModelAdapter 连接数据库
    adapter = SQLModelAdapter(AsyncSessionLocal)
    # 使用 Permission RBAC 模型，支持 user-group & permission 的 RBAC 能力
    # 配置 Redis URL 以启用多 Worker 策略同步（适用于 gunicorn 等多进程部署）
    # 如果不使用多 Worker 或不需要实时同步，可以省略 redis_url
    config = ACLConfig(
        policy_router_enable=True,
        get_subject=get_user,
        # redis_url="redis://localhost:6379/0",  # 取消注释以启用多 Worker 同步
    )
    await acl.init(adapter=adapter, config=config, app=app)

    # 3. 初始化示例用户数据
    await init_users()

    # 4. 初始化权限策略（示例数据）
    await init_policies()

    yield

    # 关闭时清理
    # 停止 ACL 管理器（包括 Redis watcher）
    await acl.shutdown()
    await close_db()


# 创建 FastAPI 应用
app = FastAPI(
    title="FastAPI Casbin ACL 示例",
    description="一个使用 FastAPI、SQLModel、aiosqlite 和 Casbin ACL 的完整示例",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/docs",
)

# 注册路由
app.include_router(router, prefix="/api")
app.include_router(casbin_router, prefix="/api/policies")
app.include_router(frontend_route)


# ==================== 用户数据初始化 ====================


async def init_users():
    """
    初始化示例用户数据
    """
    try:
        from examples.models import User
        from examples.database import AsyncSessionLocal
    except ImportError:
        from models import User
        from database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        # 检查用户是否已存在
        from sqlmodel import select as sqlmodel_select

        users_to_create = [
            {"username": "alice", "email": "alice@example.com"},
            {"username": "bob", "email": "bob@example.com"},
            {"username": "charlie", "email": "charlie@example.com"},
        ]

        for user_data in users_to_create:
            statement = sqlmodel_select(User).where(
                User.username == user_data["username"]
            )
            result = await session.execute(statement)
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                user = User(**user_data)
                session.add(user)

        await session.commit()
        print("✅ 示例用户初始化完成")


# ==================== 权限策略初始化 ====================


async def init_policies():
    """
    初始化权限策略（使用 Permission RBAC 模型）
    在实际应用中，这些策略应该从配置文件或管理界面加载

    注意：策略中使用用户 ID（字符串）而非 username，原因如下：
    1. get_subject_from_user 返回的是 str(user.id)（字符串）
    2. 因此策略中的 subject 使用用户 ID 格式（字符串）

    Permission RBAC 架构：
    1. g (user -> role): 用户角色绑定
    2. g2 (api -> permission): API 路径到权限的映射
    3. p (role, permission, act): 角色-权限-操作策略
    """
    try:
        from examples.models import User
        from examples.database import AsyncSessionLocal
    except ImportError:
        from models import User
        from database import AsyncSessionLocal

    # 获取 Permission RBAC 模型的 enforcer
    enforcer = acl.get_enforcer("permission_rbac")

    # 首先查询用户获取 ID
    async with AsyncSessionLocal() as session:
        from sqlmodel import select as sqlmodel_select

        # 查询用户并获取 ID
        alice_stmt = sqlmodel_select(User).where(User.username == "alice")
        bob_stmt = sqlmodel_select(User).where(User.username == "bob")
        charlie_stmt = sqlmodel_select(User).where(User.username == "charlie")

        alice_result = await session.execute(alice_stmt)
        bob_result = await session.execute(bob_stmt)
        charlie_result = await session.execute(charlie_stmt)

        alice = alice_result.scalar_one_or_none()
        bob = bob_result.scalar_one_or_none()
        charlie = charlie_result.scalar_one_or_none()

        if not alice or not bob or not charlie:
            print("⚠️  警告：部分用户未找到，请先运行 init_users()")
            return

        # 定义角色（使用用户 ID）- g 策略
        # g, 1, admin  -> 用户 ID 1 是 admin 角色
        # g, 2, user   -> 用户 ID 2 是 user 角色
        await enforcer.add_grouping_policy(str(alice.id), "admin")
        await enforcer.add_grouping_policy(str(bob.id), "user")
        await enforcer.add_grouping_policy(str(charlie.id), "user")

    # 定义 API 到 Permission 的映射 - g2 策略
    # 格式: "METHOD:api_path" -> permission
    await enforcer.add_named_grouping_policy("g2", "get_user", "user_management")
    await enforcer.add_named_grouping_policy("g2", "create_user", "user_management")
    await enforcer.add_named_grouping_policy("g2", "list_users", "user_management")
    await enforcer.add_named_grouping_policy("g2", "list_orders", "order_management")
    await enforcer.add_named_grouping_policy("g2", "create_order", "order_management")
    await enforcer.add_named_grouping_policy("g2", "get_order", "order_management")
    await enforcer.add_named_grouping_policy("g2", "update_order", "order_management")
    await enforcer.add_named_grouping_policy("g2", "delete_order", "order_management")

    # 定义策略（Permission RBAC）- p 策略
    await enforcer.add_policy("admin", "user_management", "read")
    await enforcer.add_policy("admin", "user_management", "write")
    await enforcer.add_policy("admin", "order_management", "read")
    await enforcer.add_policy("admin", "order_management", "write")
    await enforcer.add_policy("admin", "order_management", "delete")
    await enforcer.add_policy("user", "order_management", "read")
    await enforcer.add_policy("user", "order_management", "write")
    await enforcer.add_policy("user", "order_management", "delete")

    # 定义策略（Permission RBAC）- p 策略
    await enforcer.add_policy("admin", "policy_management", "write")

    # 保存策略到数据库
    await acl.save_policy()

    print("✅ 权限策略初始化完成（Permission RBAC 模型）")
    print(f"   - 用户 ID {alice.id} ({alice.username}, admin): 可以访问所有用户和订单")
    print(f"   - 用户 ID {bob.id} ({bob.username}, user): 可以访问订单")
    print(f"   - 用户 ID {charlie.id} ({charlie.username}, user): 可以访问订单")
    print(f"   - Permission 映射:")
    print(f"     /api/users/* -> user_management")
    print(f"     /api/orders/* -> order_management")


# ==================== 异常处理 ====================


@app.exception_handler(Unauthorized)
async def unauthorized_handler(request: Request, exc: Unauthorized):
    """
    处理未授权异常
    """
    return JSONResponse(
        status_code=401,
        content={"message": "未授权：请提供有效的用户 ID (X-User-ID 请求头)"},
    )


@app.exception_handler(Forbidden)
async def forbidden_handler(request: Request, exc: Forbidden):
    """
    处理禁止访问异常
    """
    return JSONResponse(
        status_code=403, content={"message": "禁止访问：您没有执行此操作的权限"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

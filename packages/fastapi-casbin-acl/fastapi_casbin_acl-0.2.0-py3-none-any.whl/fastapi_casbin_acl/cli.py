"""
命令行工具模块，用于初始化权限策略。

提供 `fastapi-casbin-acl init_permission` 命令，用于为指定用户授予管理员角色。
"""

import asyncio
import importlib
from typing import Any

import typer
from fastapi import FastAPI

from .enforcer import acl
from .exceptions import ACLNotInitialized

app = typer.Typer(help="FastAPI Casbin ACL 命令行工具")


def _load_fastapi_app(app_path: str) -> FastAPI:
    """
    动态加载 FastAPI 应用。

    Args:
        app_path: FastAPI 应用路径，格式为 "module:app"，例如 "main:app"

    Returns:
        FastAPI 应用实例

    Raises:
        typer.Exit: 如果应用路径格式错误或应用加载失败
    """
    try:
        module_path, app_name = app_path.split(":")
    except ValueError:
        typer.echo(
            f"❌ 错误：应用路径格式不正确，应为 'module:app'，例如 'main:app'", err=True
        )
        raise typer.Exit(1)

    try:
        module = importlib.import_module(module_path)
        fastapi_app = getattr(module, app_name)
        if not isinstance(fastapi_app, FastAPI):
            typer.echo(f"❌ 错误：'{app_name}' 不是 FastAPI 应用实例", err=True)
            raise typer.Exit(1)
        return fastapi_app
    except ImportError as e:
        typer.echo(f"❌ 错误：无法导入模块 '{module_path}': {e}", err=True)
        raise typer.Exit(1)
    except AttributeError:
        typer.echo(f"❌ 错误：模块 '{module_path}' 中没有找到 '{app_name}'", err=True)
        raise typer.Exit(1)


async def _init_permission_async(subject_id: str, app_path: str) -> None:
    """
    异步初始化权限策略。

    工作流程：
    1. 动态加载 FastAPI 应用
    2. 执行 lifespan 启动流程以初始化 acl
    3. 从 acl 获取 config 和 enforcer
    4. 添加策略和角色分配
    5. 保存策略到数据库
    6. 如果配置了 Redis，通知所有 Worker 重新加载策略
    7. 执行 lifespan 关闭流程

    Args:
        subject_id: 管理员用户的 subject ID
        app_path: FastAPI 应用路径，格式: "module:app"
    """
    # 1. 动态加载 FastAPI 应用
    typer.echo(f"📦 正在加载 FastAPI 应用: {app_path}")
    fastapi_app = _load_fastapi_app(app_path)

    # 2. 检查是否有 lifespan
    if (
        not hasattr(fastapi_app.router, "lifespan")
        or fastapi_app.router.lifespan is None
    ):
        typer.echo(
            "❌ 错误：FastAPI 应用没有配置 lifespan。请确保在创建 FastAPI 应用时传入了 lifespan 参数。",
            err=True,
        )
        raise typer.Exit(1)

    # 3. 执行 lifespan 启动流程
    # 使用 ASGI 协议来执行 lifespan
    typer.echo("🚀 正在执行应用启动流程...")

    # 创建 ASGI lifespan 事件的消息队列
    lifespan_queue: asyncio.Queue = asyncio.Queue()
    startup_complete = asyncio.Event()
    shutdown_complete = asyncio.Event()

    async def receive() -> dict:
        """ASGI receive 函数，用于接收 lifespan 事件消息"""
        return await lifespan_queue.get()

    async def send(message: dict) -> None:
        """ASGI send 函数，用于发送 lifespan 事件响应"""
        if message["type"] == "lifespan.startup.complete":
            startup_complete.set()
        elif message["type"] == "lifespan.shutdown.complete":
            shutdown_complete.set()
        elif message["type"] == "lifespan.startup.failed":
            error = message.get("message", "Unknown error")
            raise RuntimeError(f"Lifespan startup failed: {error}")
        elif message["type"] == "lifespan.shutdown.failed":
            error = message.get("message", "Unknown error")
            raise RuntimeError(f"Lifespan shutdown failed: {error}")

    # 创建 lifespan scope
    lifespan_scope = {
        "type": "lifespan",
        "asgi": {"version": "3.0", "spec_version": "2.0"},
    }

    # 执行 lifespan 启动
    async def run_lifespan():
        """执行 lifespan 的启动和关闭流程"""
        lifespan_app = fastapi_app.router.lifespan
        await lifespan_app(lifespan_scope, receive, send)

    # 发送启动事件
    await lifespan_queue.put({"type": "lifespan.startup"})

    # 在后台运行 lifespan
    lifespan_task = asyncio.create_task(run_lifespan())

    # 等待启动完成
    try:
        # 等待启动完成事件
        await asyncio.wait_for(startup_complete.wait(), timeout=30.0)

        # 4. 检查 acl 是否已初始化
        if not acl._initialized:
            typer.echo(
                "❌ 错误：acl 未初始化。请确保在 lifespan 中调用了 await acl.init()。",
                err=True,
            )
            raise typer.Exit(1)

        # 5. 获取 config 和 enforcer
        try:
            config = acl.config
            default_enforcer = acl.enforcer
        except ACLNotInitialized as e:
            typer.echo(f"❌ 错误：{e}", err=True)
            raise typer.Exit(1)

        typer.echo(
            f"✅ ACL 配置已加载 (管理员角色: {config.admin_role})"
        )

        # 6. 添加策略
        typer.echo("📝 正在添加权限策略...")

        # 为管理员角色添加策略管理权限
        policy_added = await default_enforcer.add_policy(
            config.admin_role, "policy_management", "write"
        )
        if policy_added:
            typer.echo(
                f"   ✅ 已添加策略: {config.admin_role} -> policy_management -> write"
            )
        else:
            typer.echo(
                f"   ⚠️  策略已存在: {config.admin_role} -> policy_management -> write"
            )

        # 为指定用户分配管理员角色
        grouping_added = await default_enforcer.add_grouping_policy(
            subject_id, config.admin_role
        )
        if grouping_added:
            typer.echo(f"   ✅ 已分配角色: {subject_id} -> {config.admin_role}")
        else:
            typer.echo(f"   ⚠️  角色分配已存在: {subject_id} -> {config.admin_role}")

        # 7. 保存策略到数据库
        typer.echo("💾 正在保存策略到数据库...")
        await acl.save_policy()
        typer.echo("✅ 策略已保存")

        # 8. 如果配置了 Redis，通知所有 Worker 重新加载策略
        if config.redis_url:
            typer.echo("📢 正在通知所有 Worker 重新加载策略...")
            try:
                await acl.notify_policy_update()
                typer.echo("✅ 已发送策略更新通知")
            except Exception as e:
                typer.echo(f"⚠️  警告：发送策略更新通知失败: {e}", err=True)

        typer.echo("\n🎉 权限初始化完成！")
        typer.echo(f"   用户 ID: {subject_id}")
        typer.echo(f"   角色: {config.admin_role}")
        typer.echo(f"   权限: policy_management -> write")

    finally:
        # 显式停止 ACL 管理器（包括 Redis watcher）
        try:
            if acl._initialized:
                await acl.shutdown()
        except Exception as e:
            typer.echo(f"⚠️  警告：停止 ACL 管理器时出错: {e}", err=True)

        # 发送关闭事件并等待关闭完成
        if not lifespan_task.done():
            await lifespan_queue.put({"type": "lifespan.shutdown"})
            try:
                await asyncio.wait_for(shutdown_complete.wait(), timeout=10.0)
            except asyncio.TimeoutError:
                typer.echo("⚠️  警告：lifespan 关闭超时", err=True)
            except Exception as e:
                typer.echo(f"⚠️  警告：lifespan 关闭时出错: {e}", err=True)

        # 确保任务完成
        if not lifespan_task.done():
            lifespan_task.cancel()
            try:
                await lifespan_task
            except asyncio.CancelledError:
                pass


@app.command()
def init_permission(
    subject_id: str = typer.Argument(..., help="管理员用户的 subject ID"),
    app_path: str = typer.Argument(
        ..., help="FastAPI 应用路径，格式: module:app，例如: main:app"
    ),
) -> None:
    """
    初始化权限策略，为指定用户授予管理员角色。

    此命令会：
    1. 加载指定的 FastAPI 应用
    2. 执行应用的 lifespan 启动流程以初始化 ACL
    3. 为管理员角色添加策略管理权限
    4. 为指定用户分配管理员角色
    5. 保存策略到数据库
    6. 如果配置了 Redis，通知所有 Worker 重新加载策略（适用于多 Worker 部署）

    示例:
        uv run fastapi-casbin init_permission "user123" "main:app"
    """
    asyncio.run(_init_permission_async(subject_id, app_path))


async def _explain_async(
    uri: str, subject: str, app_path: str, method: str = None
) -> None:
    """
    异步解释策略规则。

    工作流程：
    1. 动态加载 FastAPI 应用
    2. 执行 lifespan 启动流程以初始化 acl
    3. 查询 URI 和 method 对应的 Permission
    4. 解析 subject 的角色链
    5. 查找命中的 policy 规则
    6. 输出结果
    7. 执行 lifespan 关闭流程

    Args:
        uri: API URI 路径，例如 "/api/users/1"
        subject: Subject ID，例如 "user123"
        app_path: FastAPI 应用路径，格式: "module:app"
        method: HTTP 方法，例如 "GET", "POST"（可选，如果不提供则匹配所有方法）
    """
    # 1. 动态加载 FastAPI 应用
    typer.echo(f"📦 正在加载 FastAPI 应用: {app_path}")
    fastapi_app = _load_fastapi_app(app_path)

    # 2. 检查是否有 lifespan
    if (
        not hasattr(fastapi_app.router, "lifespan")
        or fastapi_app.router.lifespan is None
    ):
        typer.echo(
            "❌ 错误：FastAPI 应用没有配置 lifespan。请确保在创建 FastAPI 应用时传入了 lifespan 参数。",
            err=True,
        )
        raise typer.Exit(1)

    # 3. 执行 lifespan 启动流程
    typer.echo("🚀 正在执行应用启动流程...")

    lifespan_queue: asyncio.Queue = asyncio.Queue()
    startup_complete = asyncio.Event()
    shutdown_complete = asyncio.Event()

    async def receive() -> dict:
        return await lifespan_queue.get()

    async def send(message: dict) -> None:
        if message["type"] == "lifespan.startup.complete":
            startup_complete.set()
        elif message["type"] == "lifespan.shutdown.complete":
            shutdown_complete.set()
        elif message["type"] == "lifespan.startup.failed":
            error = message.get("message", "Unknown error")
            raise RuntimeError(f"Lifespan startup failed: {error}")
        elif message["type"] == "lifespan.shutdown.failed":
            error = message.get("message", "Unknown error")
            raise RuntimeError(f"Lifespan shutdown failed: {error}")

    lifespan_scope = {
        "type": "lifespan",
        "asgi": {"version": "3.0", "spec_version": "2.0"},
    }

    async def run_lifespan():
        lifespan_app = fastapi_app.router.lifespan
        await lifespan_app(lifespan_scope, receive, send)

    await lifespan_queue.put({"type": "lifespan.startup"})
    lifespan_task = asyncio.create_task(run_lifespan())

    try:
        await asyncio.wait_for(startup_complete.wait(), timeout=30.0)

        # 4. 检查 acl 是否已初始化
        if not acl._initialized:
            typer.echo(
                "❌ 错误：acl 未初始化。请确保在 lifespan 中调用了 await acl.init()。",
                err=True,
            )
            raise typer.Exit(1)

        # 5. 获取 enforcer
        try:
            default_enforcer = acl.enforcer
        except ACLNotInitialized as e:
            typer.echo(f"❌ 错误：{e}", err=True)
            raise typer.Exit(1)

        # 6. 从 URI 和 method 找到对应的路由和 api_name
        typer.echo(f"\n📋 策略解释结果")
        typer.echo(f"Subject: {subject}")
        if method:
            typer.echo(f"Method: {method}")
        typer.echo(f"URI: {uri}\n")

        # 查找匹配的路由
        from fastapi.routing import APIRoute
        from starlette.routing import Match

        matched_route = None
        api_name = None

        # 如果提供了 method，转换为大写
        if method:
            method = method.upper()

        # 遍历所有路由，找到匹配的路由
        for route in fastapi_app.routes:
            if isinstance(route, APIRoute):
                # 检查路径和方法是否匹配
                match, _ = route.matches(
                    {"type": "http", "method": method or "GET", "path": uri}
                )
                if match == Match.FULL:
                    # 如果指定了 method，检查方法是否匹配
                    if method is None or method in route.methods:
                        matched_route = route
                        api_name = route.name
                        break

        if not api_name or not matched_route:
            typer.echo(f"Route Matching: 未找到匹配的路由\n")
            typer.echo(f"Permission Mapping: 无法确定\n")
        else:
            typer.echo(f"Route Matching:")
            typer.echo(f"  URI: {uri}")
            typer.echo(f"  Method: {method or 'ANY'}")
            typer.echo(f"  Route Path: {matched_route.path}")
            typer.echo(f"  API Name: {api_name}\n")

            # 获取所有 g2 映射
            mappings = default_enforcer.get_named_grouping_policy("g2")
            permission = None

            # 直接查找 api_name 对应的 permission
            for mapping in mappings:
                api_key = mapping[0]  # api_name
                perm = mapping[1]

                if api_key == api_name:
                    permission = perm
                    break

            if permission:
                typer.echo(f"Permission Mapping:")
                typer.echo(f"  {api_name} -> {permission}\n")
            else:
                typer.echo(f"Permission Mapping: 未找到匹配的 Permission\n")

        # 7. 解析 subject 的角色链
        roles = await default_enforcer.get_roles_for_user(subject)
        typer.echo(f"Role Chain:")
        if roles:
            for role in roles:
                typer.echo(f"  {subject} -> {role}")
        else:
            typer.echo(f"  {subject} -> (无角色)")
        typer.echo()

        # 8. 查找命中的 policy 规则
        typer.echo(f"Matched Policies:")
        if permission and roles:
            policies = default_enforcer.get_policy()
            matched_policies = []
            for policy in policies:
                # policy 格式: (role, permission, act)
                if len(policy) >= 3:
                    policy_role = policy[0]
                    policy_permission = policy[1]
                    policy_act = policy[2]
                    # 检查角色和权限是否匹配
                    if policy_role in roles and policy_permission == permission:
                        matched_policies.append(policy)
                        typer.echo(
                            f"  p, {policy_role}, {policy_permission}, {policy_act}  [ALLOW]"
                        )

            if not matched_policies:
                typer.echo("  (无匹配的策略)")
        else:
            typer.echo("  (无法匹配：缺少 Permission 或角色)")

    finally:
        # 清理
        try:
            if acl._initialized:
                await acl.shutdown()
        except Exception as e:
            typer.echo(f"⚠️  警告：停止 ACL 管理器时出错: {e}", err=True)

        if not lifespan_task.done():
            await lifespan_queue.put({"type": "lifespan.shutdown"})
            try:
                await asyncio.wait_for(shutdown_complete.wait(), timeout=10.0)
            except asyncio.TimeoutError:
                typer.echo("⚠️  警告：lifespan 关闭超时", err=True)
            except Exception as e:
                typer.echo(f"⚠️  警告：lifespan 关闭时出错: {e}", err=True)

        if not lifespan_task.done():
            lifespan_task.cancel()
            try:
                await lifespan_task
            except asyncio.CancelledError:
                pass


@app.command()
def explain(
    uri: str = typer.Option(..., "--uri", help="API URI 路径，例如: /api/users/1"),
    subject: str = typer.Option(..., "--subject", help="Subject ID，例如: user123"),
    method: str = typer.Option(
        None, "--method", help="HTTP 方法，例如: GET, POST, PUT, DELETE（可选）"
    ),
    app_path: str = typer.Argument(
        ..., help="FastAPI 应用路径，格式: module:app，例如: main:app"
    ),
) -> None:
    """
    解释策略规则，显示 URI、method 和 subject 命中的策略。

    此命令会：
    1. 查询 URI 和 method 对应的 Permission
    2. 解析 subject 的角色链
    3. 输出命中的 policy 规则

    示例:
        uv run fastapi-casbin explain --uri "/api/users/1" --subject "user123" --method "GET" "main:app"
        uv run fastapi-casbin explain --uri "/api/users/1" --subject "user123" "main:app"
    """
    asyncio.run(_explain_async(uri, subject, app_path, method))


if __name__ == "__main__":
    app()

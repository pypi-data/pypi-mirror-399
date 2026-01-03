"""
NexAgent CLI - 命令行工具
"""
import click
import os
import json
from ._version import __version__


@click.group()
@click.version_option(version=__version__, prog_name="nex")
def cli():
    """NexAgent 命令行工具"""
    pass


@cli.command()
@click.option('--port', '-p', default=8000, help='服务端口')
@click.option('--host', '-h', default='0.0.0.0', help='监听地址')
@click.option('--dir', '-d', default='.', help='工作目录')
def serve(port, host, dir):
    """启动 WebServer (API + 前端)"""
    os.chdir(os.path.abspath(dir))
    import uvicorn
    from .webserver import app
    click.echo(f"🚀 启动 NexAgent WebServer")
    click.echo(f"🌐 访问地址: http://{host}:{port}")
    click.echo(f"📁 工作目录: {os.getcwd()}")
    uvicorn.run(app, host=host, port=port)


@cli.command()
@click.option('--dir', '-d', default='.', help='项目目录')
def init(dir):
    """初始化工作目录"""
    dir = os.path.abspath(dir)
    os.makedirs(dir, exist_ok=True)
    
    # 创建 tools 目录
    tools_dir = os.path.join(dir, 'tools')
    os.makedirs(tools_dir, exist_ok=True)
    click.echo(f"✅ 创建 tools/ 目录")
    
    # 创建提示词
    prompt_file = os.path.join(dir, 'prompt_config.txt')
    if not os.path.exists(prompt_file):
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write("You are a helpful assistant.")
        click.echo(f"✅ 创建 prompt_config.txt")
    else:
        click.echo(f"⏭️  跳过 prompt_config.txt (已存在)")
    
    click.echo(f"\n🎉 初始化完成！目录: {dir}")
    click.echo("\n🚀 下一步:")
    click.echo("   1. 运行 nex serve 启动服务")
    click.echo("   2. 打开 http://localhost:8000")
    click.echo("   3. 在设置中添加服务商和模型")
    click.echo("\n📖 自定义工具和更多用法请查看:")
    click.echo("   https://gitee.com/candy_xt/NexAgent")


@cli.command()
@click.option('--dir', '-d', default='.', help='工作目录')
def tools(dir):
    """列出所有可用工具"""
    dir = os.path.abspath(dir)
    tools_dir = os.path.join(dir, 'tools')
    
    click.echo("📦 内置工具:")
    click.echo("   • execute_shell - 执行shell命令")
    click.echo("   • http_request - 发送HTTP请求")
    
    if not os.path.exists(tools_dir):
        click.echo("\n⚠️  tools/ 目录不存在，运行 nex init 创建")
        return
    
    click.echo("\n🔧 自定义工具:")
    
    loaded = set()
    # JSON 定义的工具
    for f in os.listdir(tools_dir):
        if f.endswith('.json'):
            name = f[:-5]
            json_path = os.path.join(tools_dir, f)
            py_path = os.path.join(tools_dir, f"{name}.py")
            try:
                with open(json_path, 'r', encoding='utf-8') as file:
                    tool_def = json.load(file)
                tool_name = tool_def.get("name", name)
                desc = tool_def.get("description", "无描述")
                has_py = "✓" if os.path.exists(py_path) else "✗"
                click.echo(f"   • {tool_name} [{has_py}] - {desc}")
                loaded.add(name)
            except Exception as e:
                click.echo(f"   • {name} [错误] - {e}")
    
    # 纯 Python 工具
    for f in os.listdir(tools_dir):
        if f.endswith('.py') and f[:-3] not in loaded:
            py_path = os.path.join(tools_dir, f)
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(f[:-3], py_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'TOOL_DEF') and hasattr(module, 'execute'):
                    tool_def = module.TOOL_DEF
                    click.echo(f"   • {tool_def['name']} [✓] - {tool_def.get('description', '无描述')}")
                else:
                    click.echo(f"   • {f[:-3]} [?] - 缺少 TOOL_DEF 或 execute")
            except Exception as e:
                click.echo(f"   • {f[:-3]} [错误] - {e}")
    
    click.echo("\n[✓]=有执行脚本  [✗]=仅定义无执行  [?]=格式不完整")


@cli.command()
@click.option('--dir', '-d', default='.', help='工作目录')
@click.option('--yes', '-y', is_flag=True, help='跳过确认')
def cleanup(dir, yes):
    """清理数据库中的残留数据（已删除的会话和孤立消息）"""
    dir = os.path.abspath(dir)
    db_path = os.path.join(dir, 'nex_data.db')
    
    if not os.path.exists(db_path):
        click.echo(f"❌ 数据库文件不存在: {db_path}")
        return
    
    from .database import Database
    db = Database(db_path)
    
    # 统计残留数据
    stats = db.get_cleanup_stats()
    
    if stats['inactive_sessions'] == 0 and stats['orphan_messages'] == 0:
        click.echo("✨ 数据库很干净，没有需要清理的数据")
        return
    
    click.echo("📊 发现以下残留数据:")
    if stats['inactive_sessions'] > 0:
        click.echo(f"   • {stats['inactive_sessions']} 个已删除的会话")
    if stats['orphan_messages'] > 0:
        click.echo(f"   • {stats['orphan_messages']} 条孤立的消息")
    
    if not yes:
        if not click.confirm('\n确定要清理这些数据吗？'):
            click.echo("已取消")
            return
    
    # 执行清理
    result = db.cleanup()
    click.echo(f"\n🧹 清理完成:")
    click.echo(f"   • 删除了 {result['sessions_deleted']} 个会话")
    click.echo(f"   • 删除了 {result['messages_deleted']} 条消息")


def main():
    cli()


if __name__ == '__main__':
    main()

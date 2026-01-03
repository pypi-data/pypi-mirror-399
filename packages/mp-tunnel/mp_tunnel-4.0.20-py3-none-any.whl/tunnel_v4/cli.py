#!/usr/bin/env python3
import click
import asyncio
import sys
import os
import logging
import warnings
import ssl
from .config import get_worker_url, VERSION, GIT_HASH
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)
ssl._create_default_https_context = ssl._create_unverified_context
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
def global_exception_handler(loop, context):
    exception = context.get('exception')
    if isinstance(exception, (OSError, ConnectionError, ssl.SSLError)):
        return
    loop.default_exception_handler(context)
def setup_asyncio():
    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(global_exception_handler)
    except:
        pass
if GIT_HASH:
    __version__ = f"{VERSION} (git: {GIT_HASH})"
else:
    __version__ = VERSION
def get_http_worker_url(worker_url=None):
    if not worker_url:
        worker_url = get_worker_url()
    return worker_url.replace('wss://', 'https://').replace('ws://', 'http://').replace('/agent/connect', '')
@click.group()
@click.version_option(version=__version__)
def cli():
    setup_asyncio()
@cli.command('agent')
@click.option('--id', 'node_id',
              help='设置节点 ID（默认：主机名）')
@click.option('--worker', '-w',
              default=None,
              help=f'Worker URL（默认：内置 URL）')
@click.option('--token',
              help='启用服务认证（Client 需提供 token）')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='配置文件')
@click.option('--tags', '-t',
              help='节点标签（key=value,key=value）')
@click.option('--heartbeat', type=int, default=600,
              help='心跳间隔（秒），默认600秒（10分钟），0表示禁用心跳')
@click.option('--debug', is_flag=True,
              help='启用调试日志（输出详细信息）')
@click.option('--log-file', type=str, default=None,
              help='日志文件路径（默认：tunnel-agent-{node_id}.log）')
@click.option('--bg', '--background', is_flag=True,
              help='后台运行（默认前台运行）')
@click.option('-y', '--yes', is_flag=True,
              help='跳过确认')
@click.argument('services', nargs=-1, required=False)
def agent_cmd(node_id, worker, token, config, tags, heartbeat, debug, log_file, bg, yes, services):
    if not services:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        sys.exit(0)
    _start_agent(node_id, worker, token, config, tags, heartbeat, debug, log_file, bg, yes, services)
@cli.group('agent-mgmt')
def agent_mgmt():
    pass
@agent_mgmt.command('list')
def agent_list():
    from tunnel_v4.client.cli_service import run_list_local_services
    exit_code = asyncio.run(run_list_local_services())
    sys.exit(exit_code)
@agent_mgmt.command('add')
@click.argument('services', nargs=-1, required=True)
def agent_add(services):
    from tunnel_v4.client.cli_service import run_add_local_service
    exit_code = asyncio.run(run_add_local_service(services))
    sys.exit(exit_code)
@agent_mgmt.command('remove')
@click.argument('services', nargs=-1, required=True)
def agent_remove(services):
    from tunnel_v4.client.cli_service import run_remove_local_service
    exit_code = asyncio.run(run_remove_local_service(services))
    sys.exit(exit_code)
def _start_agent(node_id, worker, token, config, tags, heartbeat, debug, log_file, bg, yes, services):
    import psutil
    import socket
    if not node_id:
        node_id = socket.gethostname()
    if not worker:
        worker = get_worker_url()
    existing_agent = None
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if (cmdline and len(cmdline) > 2 and 
                    'agent' in cmdline and 
                    '--foreground' in cmdline and
                    f'--id {node_id}' in ' '.join(cmdline)):
                    existing_agent = {
                        'pid': proc.info['pid'],
                        'cmdline': cmdline
                    }
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if existing_agent and not foreground:
        print(f"✅ 检测到已运行的 Agent (节点 ID: {node_id})")
        print(f"   PID: {existing_agent['pid']}")
        existing_cmdline = ' '.join(existing_agent['cmdline'])
        existing_services = []
        if '@all' in existing_cmdline:
            existing_services = ['@exec', '@term', '@socks5']
        else:
            if '@exec' in existing_cmdline:
                existing_services.append('@exec')
            if '@term' in existing_cmdline:
                existing_services.append('@term')  
            if '@socks5' in existing_cmdline:
                existing_services.append('@socks5')
            import re
            port_services = re.findall(r'(\w+):(\d+)(?::(\w+))?', existing_cmdline)
            for name, port, protocol in port_services:
                existing_services.append(f"{name}:{port}:{protocol or 'http'}")
        new_services_list = list(services)
        if '@all' in new_services_list:
            new_services_list.remove('@all')
            new_services_list.extend(['@exec', '@term', '@socks5'])
        services_to_add = [s for s in new_services_list if s not in existing_services]
        if not services_to_add:
            print(f"   现有服务: {', '.join(existing_services) if existing_services else '无'}")
            print(f"   ⚠️  所有请求的服务都已在运行")
            return
        print(f"   现有服务: {', '.join(existing_services) if existing_services else '无'}")
        print(f"   将添加服务: {', '.join(services_to_add)}")
        print()
        try:
            from tunnel_v4.client.cli_service import add_services_to_running_agent
            import asyncio
            success = asyncio.run(add_services_to_running_agent(node_id, services_to_add, worker))
            if success:
                print("✅ 服务添加成功")
            else:
                print("❌ 服务添加失败")
        except Exception as e:
            print(f"❌ 动态添加服务失败: {e}")
            print("   建议重启 Agent 包含所有服务")
        return
    else:
        services_list = list(services)
        if '@all' in services_list:
            services_list.remove('@all')
            services_list.extend(['@exec', '@term', '@socks5'])
    from tunnel_v4.agent.cli_agent import run_agent
    import asyncio
    from tunnel_v4.agent.cli_agent import parse_tags
    tag_dict = parse_tags([tags] if tags else None)
    if not bg:
        asyncio.run(run_agent(
            services=tuple(services_list),
            node_id=node_id,
            worker_url=worker,
            config_file=config,
            tags=tag_dict,
            token=token,
            heartbeat_interval=heartbeat,
            debug=debug,
            log_file=log_file,
            skip_confirm=yes
        ))
    else:
        import subprocess
        import sys
        cmd = [sys.executable, sys.argv[0], 'agent']
        if node_id:
            cmd.extend(['--id', node_id])
        if worker != get_worker_url():
            cmd.extend(['--worker', worker])
        if token:
            cmd.extend(['--token', token])
        if config:
            cmd.extend(['--config', config])
        if tags:
            cmd.extend(['--tags', tags])
        if yes:
            cmd.append('--yes')
        cmd.append('--foreground')
        cmd.extend(services_list)
        print(f"🚀 启动后台 Agent (节点 ID: {node_id})")
        print(f"   服务: {', '.join(services_list)}")
        print(f"   使用 'ps aux | grep agent' 查看进程")
        print(f"   使用 'pkill -f \"agent.*{node_id}\"' 停止")
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
@cli.command('start-agent')
@click.option('--id', 'node_id',
              help='设置节点 ID（默认：主机名）')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL（默认：内置 URL）')
@click.option('--token',
              help='启用服务认证（Client 需提供 token）')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='配置文件')
@click.option('--tags', '-t',
              help='节点标签（key=value,key=value）')
@click.option('--foreground', '-f', is_flag=True,
              help='前台运行（调试模式，默认后台运行）')
@click.option('-y', '--yes', is_flag=True,
              help='跳过确认')
@click.argument('services', nargs=-1, required=True)
def start_agent_cmd(node_id, worker, token, config, tags, foreground, yes, services):
    if not worker:
        worker = get_worker_url()
    _start_agent(node_id, worker, token, config, tags, foreground, yes, services)
@cli.group()
def manage():
    pass
@manage.command('add')
@click.argument('services', nargs=-1, required=True)
@click.option('--node', '-n', required=True,
              help='目标节点')
@click.option('--nodes',
              help='多节点批量（逗号分隔）')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL')
def manage_add(services, node, nodes, worker):
    from tunnel_v4.client.cli_service import run_add_service
    services_list = list(services)
    if '@all' in services_list:
        services_list.remove('@all')
        services_list.extend(['@exec', '@term', '@socks5'])
    exit_code = asyncio.run(run_add_service(
        services=tuple(services_list),
        node_id=node,
        nodes=nodes,
        worker_url=worker
    ))
    sys.exit(exit_code)
@manage.command('remove')
@click.argument('services', nargs=-1, required=True)
@click.option('--node', '-n', required=True,
              help='目标节点')
@click.option('--nodes',
              help='多节点批量（逗号分隔）')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL')
def manage_remove(services, node, nodes, worker):
    from tunnel_v4.client.cli_service import run_remove_service
    exit_code = asyncio.run(run_remove_service(
        services=services,
        node_id=node,
        nodes=nodes,
        worker_url=worker
    ))
    sys.exit(exit_code)
@manage.command('set')
@click.argument('key')
@click.argument('value')
def manage_set(key, value):
    from tunnel_v4.client.cli_config import set_config
    exit_code = set_config(key, value)
    sys.exit(exit_code)
@manage.command('show')
def manage_show():
    from tunnel_v4.client.cli_config import show_config
    exit_code = show_config()
    sys.exit(exit_code)
@cli.group(name='list', invoke_without_command=True)
@click.pass_context
def list_group(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(list_nodes)
@cli.group(name='ls')
def ls_group():
    pass
@list_group.command('nodes')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL')
@click.option('--show-offline', is_flag=True,
              help='显示离线节点')
def list_nodes(worker, show_offline):
    import requests
    if not worker:
        worker = get_http_worker_url()
    try:
        resp = requests.get(f'{worker}/api/v1/nodes', timeout=10)
        if resp.status_code != 200:
            click.echo(f"✗ Error: HTTP {resp.status_code}", err=True)
            sys.exit(1)
        nodes = resp.json().get('nodes', [])
        if not show_offline:
            nodes = [n for n in nodes if n.get('status') == 'online']
        if not nodes:
            click.echo("No nodes found")
            sys.exit(0)
        for node in nodes:
            status_icon = '🟢' if node.get('status') == 'online' else '🔴'
            tags = ','.join(node.get('tags', [])[:3])
            services = ','.join([s['name'] for s in node.get('services', [])])
            click.echo(f"{status_icon} {node['node_id']:20s} [{tags}] {services}")
        sys.exit(0)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)
@list_group.command('services')
@click.option('--node', '-n',
              help='指定节点（默认：第一个在线节点）')
@click.option('--all', 'all_nodes', is_flag=True,
              help='所有节点')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL')
def list_services(node, all_nodes, worker):
    from tunnel_v4.client.cli_service import run_list_services_query
    exit_code = asyncio.run(run_list_services_query(
        node_id=node,
        all_nodes=all_nodes,
        worker_url=worker
    ))
    sys.exit(exit_code)
@ls_group.command('nodes')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL')
def ls_nodes(worker):
    from tunnel_v4.client.cli_service import run_list_nodes
    exit_code = asyncio.run(run_list_nodes(worker_url=worker))
    sys.exit(exit_code)
@ls_group.command('services')
@click.option('--node', '-n', help='指定节点')
@click.option('--all', 'all_nodes', is_flag=True, help='所有节点')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL')
def ls_services(node, all_nodes, worker):
    from tunnel_v4.client.cli_service import run_list_services_query
    exit_code = asyncio.run(run_list_services_query(
        node_id=node,
        all_nodes=all_nodes,
        worker_url=worker
    ))
    sys.exit(exit_code)
@cli.command('term')
@click.option('--node', '-n', help='目标节点')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL（默认：内置 URL）')
@click.option('--token',
              envvar='TUNNEL_TOKEN',
              default='test-secret-token',
              help='认证 Token')
@click.option('--debug', is_flag=True, help='启用调试输出')
def term(node, worker, token, debug):
    from tunnel_v4.client.cli_terminal import run_terminal_client, set_debug
    from tunnel_v4.client.cli_service import select_node_interactive
    set_debug(debug or os.environ.get('TUNNEL_DEBUG', '').lower() in ('1', 'true', 'yes'))
    if not worker:
        worker = get_worker_url()
    if not node:
        http_worker = worker.replace('wss://', 'https://').replace('/agent/connect', '')
        node = asyncio.run(select_node_interactive(http_worker))
        if not node:
            click.echo('❌ 未选择节点')
            sys.exit(1)
    exit_code = asyncio.run(run_terminal_client(
        node_id=node,
        worker_url=worker,
        token=token
    ))
@cli.command('exec')
@click.option('--node', '-n', help='目标节点')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL（默认：内置 URL）')
@click.option('--token',
              default='test-secret-token',
              envvar='TUNNEL_TOKEN',
              help='认证 Token')
@click.option('-i', '--interactive', is_flag=True,
              help='交互模式')
@click.argument('command', nargs=-1, required=True)
def exec_cmd(node, worker, token, interactive, command):
    from tunnel_v4.client.cli_exec import run_exec_client
    from tunnel_v4.client.cli_service import select_node_interactive
    if not worker:
        worker = get_worker_url()
    if not node:
        http_worker = worker.replace('wss://', 'https://').replace('/agent/connect', '')
        node = asyncio.run(select_node_interactive(http_worker))
        if not node:
            click.echo('❌ 未选择节点')
            sys.exit(1)
    if interactive:
        cmd = None
    else:
        cmd_str = ' '.join(command).strip() if command else ''
        cmd = cmd_str if cmd_str else None
    exit_code = asyncio.run(run_exec_client(
        node_id=node,
        worker_url=worker,
        token=token,
        command=cmd
    ))
    sys.exit(exit_code)
@cli.command('socks5')
@click.argument('port', type=int, required=False, default=1080)
@click.option('--node', '-n', help='目标节点')
@click.option('--worker', '-w',
              default=None,
              help='Worker URL（默认：内置 URL）')
@click.option('--token',
              default='test-secret-token',
              envvar='TUNNEL_TOKEN',
              help='认证 Token')
def socks5(port, node, worker, token):
    from tunnel_v4.client.cli_socks5 import run_socks5_client
    from tunnel_v4.client.cli_service import select_node_interactive
    if not worker:
        worker = get_worker_url()
    if not node:
        http_worker = worker.replace('wss://', 'https://').replace('/agent/connect', '')
        node = asyncio.run(select_node_interactive(http_worker))
        if not node:
            click.echo('❌ 未选择节点')
            sys.exit(1)
    exit_code = asyncio.run(run_socks5_client(
        node_id=node,
        worker_url=worker,
        token=token,
        local_port=port
    ))
    sys.exit(exit_code)
if __name__ == '__main__':
    cli()
def agent_entry():
    agent()
if __name__ == '__main__':
    cli()
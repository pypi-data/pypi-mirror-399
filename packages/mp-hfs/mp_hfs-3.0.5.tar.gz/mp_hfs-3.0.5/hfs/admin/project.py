"""Project management commands"""
import click
import json
import time
from tabulate import tabulate


@click.group()
def project():
    """Project management commands"""
    pass


@project.command('list')
@click.pass_context
def list_projects(ctx):
    """List all projects"""
    r = ctx.obj['redis']
    
    # 先收集所有项目 ID
    project_ids = []
    for key in r.scan_iter('hfs:project:*', count=100):
        key_str = key.decode() if isinstance(key, bytes) else key
        if ':stats' in key_str or ':accounts' in key_str or ':spaces:' in key_str:
            continue
        project_id = key_str.replace('hfs:project:', '')
        project_ids.append(project_id)
    
    if not project_ids:
        click.echo("No projects found")
        return
    
    # 预先统计所有 running spaces（按项目分组）
    running_spaces = {}  # {project_id: count}
    for skey in r.scan_iter('hfs:space:*', count=500):
        sdata = r.get(skey)
        if sdata:
            s = json.loads(sdata)
            if s.get('status') == 'running':
                pid = s.get('project_id', '')
                if pid:
                    running_spaces[pid] = running_spaces.get(pid, 0) + 1
    
    # 批量获取项目数据
    projects = []
    for project_id in project_ids:
        proj_data = r.get(f'hfs:project:{project_id}')
        if not proj_data:
            continue
        
        proj = json.loads(proj_data)
        
        # 使用 keys 而不是 scan_iter（更快）
        node_keys = r.keys(f'hfs:node:{project_id}:*')
        node_count = len(node_keys) if node_keys else 0
        
        # 从预统计数据获取 running space 数量
        space_count = running_spaces.get(project_id, 0)
        
        projects.append([
            project_id,
            proj.get('scene', 'production'),
            node_count,
            space_count,
            time.strftime('%Y-%m-%d', time.localtime(proj.get('created_at', 0))) if proj.get('created_at') else '-'
        ])
    
    if projects:
        click.echo(tabulate(projects, headers=['Project ID', 'Scene', 'Nodes', 'Running', 'Created']))
    else:
        click.echo("No projects found")


@project.command('show')
@click.argument('project_id')
@click.pass_context
def show_project(ctx, project_id):
    """Show project details"""
    r = ctx.obj['redis']
    
    key = f'hfs:project:{project_id}'
    data = r.get(key)
    
    if not data:
        click.echo(f"Project not found: {project_id}", err=True)
        ctx.exit(1)
    
    proj = json.loads(data)
    
    click.echo(f"\n📋 Project: {project_id}\n")
    click.echo(f"Scene: {proj.get('scene', 'production')}")
    
    if proj.get('required_nodes'):
        click.echo(f"Required Nodes: {proj.get('required_nodes')}")
    
    # Show config
    config = proj.get('config', {})
    if config:
        click.echo(f"\n⚙️  Configuration:")
        for key, value in config.items():
            click.echo(f"   {key}: {value}")
    
    # Show start script
    start_script = proj.get('start_script', {})
    if start_script:
        click.echo(f"\n🚀 Start Script:")
        if start_script.get('type') == 'inline':
            click.echo(f"   {start_script.get('inline', '')}")
    
    # List nodes
    nodes = []
    for node_key in r.scan_iter(f'hfs:node:{project_id}:*'):
        node_data = r.get(node_key)
        if node_data:
            node = json.loads(node_data)
            space_id = node.get('space_id') or node.get('space', '')
            nodes.append([
                node.get('id', ''),
                node.get('status', ''),
                space_id[:30] if space_id else '-'
            ])
    
    if nodes:
        click.echo(f"\n📦 Nodes ({len(nodes)}):")
        click.echo(tabulate(nodes, headers=['Node ID', 'Status', 'Space']))
    
    # Show stats
    stats_key = f'hfs:project:{project_id}:stats'
    stats_data = r.get(stats_key)
    if stats_data:
        stats = json.loads(stats_data)
        
        click.echo(f"\n📊 Statistics:")
        
        if stats.get('last_space_created'):
            elapsed = int(time.time() - stats['last_space_created'])
            click.echo(f"   Last space created: {elapsed}s ago")
        
        today = stats.get('today', {})
        if today:
            click.echo(f"   Today: created={today.get('spaces_created', 0)}, failed={today.get('spaces_failed', 0)}, reused={today.get('spaces_reused', 0)}")


@project.command('add-node')
@click.argument('project_id')
@click.argument('node_id')
@click.pass_context
def add_node(ctx, project_id, node_id):
    """Add node to project"""
    r = ctx.obj['redis']
    
    # Check project exists
    proj_key = f'hfs:project:{project_id}'
    if not r.exists(proj_key):
        click.echo(f"Project not found: {project_id}", err=True)
        ctx.exit(1)
    
    # Check node doesn't exist
    node_key = f'hfs:node:{project_id}:{node_id}'
    if r.exists(node_key):
        click.echo(f"Node already exists: {node_id}", err=True)
        ctx.exit(1)
    
    # Create node
    node_data = {
        'id': node_id,
        'project': project_id,
        'status': 'idle',
        'space': '',
        'created_at': int(time.time()),
        'updated_at': int(time.time())
    }
    
    r.set(node_key, json.dumps(node_data))
    
    click.echo(f"✅ Added node: {node_id} to {project_id}")


@project.command('remove-node')
@click.argument('project_id')
@click.argument('node_id')
@click.option('--force', is_flag=True, help='Force remove even if node has space')
@click.pass_context
def remove_node(ctx, project_id, node_id, force):
    """Remove node from project"""
    r = ctx.obj['redis']
    
    node_key = f'hfs:node:{project_id}:{node_id}'
    data = r.get(node_key)
    
    if not data:
        click.echo(f"Node not found: {node_id}", err=True)
        ctx.exit(1)
    
    node = json.loads(data)
    
    # Check if node has space
    space_id = node.get('space_id') or node.get('space', '')
    if space_id and not force:
        click.echo(f"Node has space bound: {space_id}", err=True)
        click.echo("Use --force to remove anyway", err=True)
        ctx.exit(1)
    
    r.delete(node_key)
    
    click.echo(f"✅ Removed node: {node_id} from {project_id}")
    
    if space_id:
        click.echo(f"⚠️  Warning: Space {space_id} was bound to this node")


@project.command('init')
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Preview without creating')
@click.pass_context
def init_project(ctx, config_file, dry_run):
    """Initialize project from YAML config"""
    r = ctx.obj['redis']
    
    import yaml
    with open(config_file) as f:
        cfg = yaml.safe_load(f)
    
    proj = cfg.get('project', {})
    if not proj.get('id'):
        click.echo("Error: project.id required in config", err=True)
        ctx.exit(1)
    
    project_id = proj['id']
    
    # Merge nodes from top-level if not in project
    if 'nodes' not in proj and 'nodes' in cfg:
        proj['nodes'] = cfg['nodes']
    
    if dry_run:
        click.echo(f"\n[DRY-RUN] Would create project: {project_id}")
        click.echo(f"  Scene: {proj.get('scene', 'production')}")
        
        nodes_config = proj.get('nodes', {})
        node_ids = nodes_config.get('ids', [])
        
        if nodes_config.get('pattern') and nodes_config.get('count'):
            pattern = nodes_config['pattern']
            count = nodes_config['count']
            node_ids = [pattern.replace('{num}', str(i)) for i in range(1, count + 1)]
        
        click.echo(f"  Nodes: {len(node_ids)}")
        for node_id in node_ids[:5]:
            click.echo(f"    - {node_id}")
        if len(node_ids) > 5:
            click.echo(f"    ... and {len(node_ids) - 5} more")
        
        return
    
    # Create project
    from .bootstrap import _create_project
    _create_project(r, proj)
    
    click.echo(f"\n✅ Project initialized: {project_id}")


@project.command('update')
@click.argument('project_id')
@click.option('--scene', help='Update scene (e.g., production, long_task)')
@click.option('--description', help='Update description')
@click.option('--required-nodes', type=int, help='Update required nodes count')
@click.option('--start-script', help='Update start script (inline command)')
@click.option('--stop-script', help='Update stop script (inline command)')
@click.option('--timeout-min', type=int, help='Update min timeout in seconds')
@click.option('--timeout-max', type=int, help='Update max timeout in seconds')
@click.option('--config-file', type=click.Path(exists=True), help='Update from YAML file (partial)')
@click.pass_context
def update_project(ctx, project_id, scene, description, required_nodes, start_script, stop_script, timeout_min, timeout_max, config_file):
    """Update project (partial update)"""
    r = ctx.obj['redis']
    
    proj_key = f'hfs:project:{project_id}'
    old_data = r.get(proj_key)
    
    if not old_data:
        click.echo(f"Project not found: {project_id}", err=True)
        click.echo("Use 'project init' to create new project", err=True)
        ctx.exit(1)
    
    # Load existing data
    project_data = json.loads(old_data)
    project_data['updated_at'] = int(time.time())
    
    updated_fields = []
    
    # Update from command line options
    if scene:
        project_data['scene'] = scene
        updated_fields.append(f"scene={scene}")
    
    if description:
        project_data['description'] = description
        updated_fields.append("description")
    
    if required_nodes is not None:
        project_data['required_nodes'] = required_nodes
        updated_fields.append(f"required_nodes={required_nodes}")
    
    if start_script:
        project_data['start_script'] = {
            'type': 'inline',
            'inline': start_script
        }
        updated_fields.append("start_script")
    
    if stop_script:
        project_data['stop_script'] = {
            'type': 'inline',
            'inline': stop_script
        }
        updated_fields.append("stop_script")
    
    if timeout_min is not None or timeout_max is not None:
        if 'timeout' not in project_data:
            project_data['timeout'] = {}
        if timeout_min is not None:
            project_data['timeout']['min_seconds'] = timeout_min
            updated_fields.append(f"timeout.min={timeout_min}s")
        if timeout_max is not None:
            project_data['timeout']['max_seconds'] = timeout_max
            updated_fields.append(f"timeout.max={timeout_max}s")
    
    # Update from YAML file (partial)
    if config_file:
        import yaml
        with open(config_file) as f:
            cfg = yaml.safe_load(f)
        
        proj = cfg.get('project', {})
        
        # Only update fields present in YAML
        if 'scene' in proj:
            project_data['scene'] = proj['scene']
            updated_fields.append(f"scene={proj['scene']}")
        
        if 'description' in proj:
            project_data['description'] = proj['description']
            updated_fields.append("description")
        
        if 'required_nodes' in proj:
            project_data['required_nodes'] = proj['required_nodes']
            updated_fields.append(f"required_nodes={proj['required_nodes']}")
        
        if 'start_script' in proj:
            project_data['start_script'] = proj['start_script']
            updated_fields.append("start_script")
        
        if 'stop_script' in proj:
            project_data['stop_script'] = proj['stop_script']
            updated_fields.append("stop_script")
        
        if 'timeout' in proj:
            project_data['timeout'] = proj['timeout']
            updated_fields.append("timeout")
        
        if 'config' in proj:
            project_data['config'] = proj['config']
            updated_fields.append("config")
    
    if not updated_fields:
        click.echo("No fields to update. Use --help to see available options.", err=True)
        ctx.exit(1)
    
    r.set(proj_key, json.dumps(project_data))
    
    # 同步创建缺失的节点
    if required_nodes is not None:
        existing_nodes = set()
        for key in r.scan_iter(f'hfs:node:{project_id}:*'):
            node_data = r.get(key)
            if node_data:
                node = json.loads(node_data)
                existing_nodes.add(node.get('id'))
        
        for i in range(1, required_nodes + 1):
            node_id = f'{project_id}-{i}'
            if node_id not in existing_nodes:
                node_key = f'hfs:node:{project_id}:{node_id}'
                node_data = {
                    'id': node_id,
                    'project_id': project_id,
                    'status': 'idle',
                    'created_at': int(time.time())
                }
                r.set(node_key, json.dumps(node_data))
                click.echo(f"   ✓ Created node: {node_id}")
    
    click.echo(f"✅ Updated project: {project_id}")
    click.echo(f"   Fields: {', '.join(updated_fields)}")


@project.command('export')
@click.argument('project_id')
@click.argument('output_file', type=click.Path())
@click.pass_context
def export_project(ctx, project_id, output_file):
    """Export project to YAML config"""
    r = ctx.obj['redis']
    
    proj_key = f'hfs:project:{project_id}'
    data = r.get(proj_key)
    
    if not data:
        click.echo(f"Project not found: {project_id}", err=True)
        ctx.exit(1)
    
    proj = json.loads(data)
    
    # Get nodes
    node_ids = []
    for key in r.scan_iter(f'hfs:node:{project_id}:*'):
        node_data = r.get(key)
        if node_data:
            node = json.loads(node_data)
            node_ids.append(node.get('id'))
    
    # Build config
    config = {
        'project': {
            'id': project_id,
            'scene': proj.get('scene', 'production'),
        },
        'nodes': {
            'ids': sorted(node_ids)
        }
    }
    
    if proj.get('description'):
        config['project']['description'] = proj['description']
    if proj.get('required_nodes'):
        config['project']['required_nodes'] = proj['required_nodes']
    if proj.get('config'):
        config['project']['config'] = proj['config']
    if proj.get('start_script'):
        config['project']['start_script'] = proj['start_script']
    if proj.get('stop_script'):
        config['project']['stop_script'] = proj['stop_script']
    
    # Write to file
    import yaml
    with open(output_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    click.echo(f"✅ Exported to: {output_file}")


def _get_all_project_ids(r):
    """获取所有项目 ID"""
    project_ids = []
    for key in r.scan_iter('hfs:project:*'):
        key_str = key.decode() if isinstance(key, bytes) else key
        if ':stats' in key_str or ':accounts' in key_str or ':spaces:' in key_str:
            continue
        project_ids.append(key_str.replace('hfs:project:', ''))
    return project_ids


def _stop_project(r, project_id, node_id=None, pause_hf=True):
    """停止项目或指定节点"""
    from huggingface_hub import HfApi
    
    nodes = []
    spaces_to_stop = []
    
    for key in r.scan_iter(f'hfs:node:{project_id}:*'):
        data = r.get(key)
        if data:
            node = json.loads(data)
            if node_id and node['id'] != node_id:
                continue
            nodes.append(node)
            space_id = node.get('space_id') or node.get('space', '')
            if space_id:
                spaces_to_stop.append(space_id)
    
    # 停止节点
    stopped_nodes = 0
    for node in nodes:
        node_key = f"hfs:node:{project_id}:{node['id']}"
        node['status'] = 'idle'
        node['space_id'] = ''
        node['space'] = ''
        node['updated_at'] = int(time.time())
        r.set(node_key, json.dumps(node))
        stopped_nodes += 1
    
    # 标记 Space 为 stopped + 暂停 HF Space
    stopped_spaces = 0
    for space_id in spaces_to_stop:
        space_key = f'hfs:space:{space_id}'
        space_data = r.get(space_key)
        if space_data:
            space = json.loads(space_data)
            if space.get('project_id') == project_id:
                # 暂停 HF Space
                if pause_hf:
                    username = space_id.split('/')[0]
                    acc_data = r.get(f'hfs:account:{username}')
                    if acc_data:
                        acc = json.loads(acc_data)
                        try:
                            api = HfApi(token=acc.get('token'))
                            api.pause_space(space_id)
                        except:
                            pass
                
                space['status'] = 'stopped'
                space['node_id'] = ''
                space['updated_at'] = int(time.time())
                r.set(space_key, json.dumps(space))
                stopped_spaces += 1
    
    return stopped_nodes, stopped_spaces


def _start_project(ctx, r, project_id, node_id=None, force=False):
    """点火项目或指定节点"""
    from hfs.scheduler import Scheduler
    
    # 找目标节点
    target_node = None
    for key in r.scan_iter(f'hfs:node:{project_id}:*'):
        data = r.get(key)
        if data:
            node = json.loads(data)
            if node_id:
                if node['id'] == node_id:
                    target_node = node
                    break
            else:
                # 找第一个空闲节点
                if node.get('status') == 'idle':
                    target_node = node
                    break
    
    if not target_node:
        return None, "No idle node found" if not node_id else f"Node {node_id} not found"
    
    # 检查是否已运行
    if target_node.get('status') == 'running' and not force:
        return None, f"Node {target_node['id']} already running (use --force)"
    
    # 如果 force，先停止
    if target_node.get('status') == 'running' and force:
        _stop_project(r, project_id, target_node['id'])
    
    # 点火
    redis_url = ctx.obj['redis_url']
    scheduler = Scheduler(redis_url)
    
    try:
        space_id, account = scheduler.create_and_deploy_space(
            project_id=project_id,
            node_id=target_node['id'],
            reuse=True,
            urgent=True
        )
        return space_id, account
    except Exception as e:
        return None, str(e)


@project.command('stop')
@click.argument('project_id', required=False)
@click.option('--node', help='Stop specific node only')
@click.option('--all', 'all_projects', is_flag=True, help='Stop all projects')
@click.pass_context
def stop_project(ctx, project_id, node, all_projects):
    """Stop project nodes and unbind spaces"""
    r = ctx.obj['redis']
    
    if all_projects:
        project_ids = _get_all_project_ids(r)
        if not project_ids:
            click.echo("No projects found")
            return
        click.echo(f"🛑 Stopping {len(project_ids)} projects...")
        for pid in project_ids:
            stopped_nodes, stopped_spaces = _stop_project(r, pid)
            click.echo(f"   {pid}: {stopped_nodes} nodes, {stopped_spaces} spaces")
            time.sleep(1)  # 间隔避免冲击
        click.echo("✅ All projects stopped")
    elif project_id:
        if not r.exists(f'hfs:project:{project_id}'):
            click.echo(f"Project not found: {project_id}", err=True)
            ctx.exit(1)
        stopped_nodes, stopped_spaces = _stop_project(r, project_id, node)
        target = f"{project_id}/{node}" if node else project_id
        click.echo(f"✅ Stopped {target}: {stopped_nodes} nodes, {stopped_spaces} spaces")
    else:
        click.echo("Error: specify PROJECT_ID or --all", err=True)
        ctx.exit(1)


@project.command('start')
@click.argument('project_id', required=False)
@click.option('--node', help='Start specific node only')
@click.option('--all', 'all_projects', is_flag=True, help='Start all projects')
@click.option('--force', is_flag=True, help='Force restart if already running')
@click.pass_context
def start_project(ctx, project_id, node, all_projects, force):
    """Start (bootstrap) project - ignite one idle node"""
    r = ctx.obj['redis']
    
    if all_projects:
        project_ids = _get_all_project_ids(r)
        if not project_ids:
            click.echo("No projects found")
            return
        click.echo(f"🚀 Starting {len(project_ids)} projects...")
        for pid in project_ids:
            space_id, result = _start_project(ctx, r, pid, force=force)
            if space_id:
                click.echo(f"   {pid}: {space_id}")
            else:
                click.echo(f"   {pid}: {result}")
            time.sleep(5)  # 间隔避免 HF 限流
        click.echo("✅ All projects started")
    elif project_id:
        if not r.exists(f'hfs:project:{project_id}'):
            click.echo(f"Project not found: {project_id}", err=True)
            ctx.exit(1)
        click.echo(f"🚀 Starting {project_id}{'/' + node if node else ''}...")
        space_id, result = _start_project(ctx, r, project_id, node, force)
        if space_id:
            click.echo(f"✅ Space: {space_id}")
            if isinstance(result, dict):
                click.echo(f"   Account: {result.get('username')}")
        else:
            click.echo(f"❌ Failed: {result}")
    else:
        click.echo("Error: specify PROJECT_ID or --all", err=True)
        ctx.exit(1)


@project.command('restart')
@click.argument('project_id', required=False)
@click.option('--node', help='Restart specific node only')
@click.option('--all', 'all_projects', is_flag=True, help='Restart all projects')
@click.option('--no-start', is_flag=True, help='Only stop, do not start')
@click.pass_context
def restart_project(ctx, project_id, node, all_projects, no_start):
    """Restart project: stop then start"""
    r = ctx.obj['redis']
    
    if all_projects:
        project_ids = _get_all_project_ids(r)
        if not project_ids:
            click.echo("No projects found")
            return
        click.echo(f"🔄 Restarting {len(project_ids)} projects...")
        for pid in project_ids:
            _stop_project(r, pid)
            click.echo(f"   {pid}: stopped")
            if not no_start:
                time.sleep(3)
                space_id, result = _start_project(ctx, r, pid)
                if space_id:
                    click.echo(f"   {pid}: started -> {space_id}")
                else:
                    click.echo(f"   {pid}: start failed - {result}")
            time.sleep(5)
        click.echo("✅ All projects restarted")
    elif project_id:
        if not r.exists(f'hfs:project:{project_id}'):
            click.echo(f"Project not found: {project_id}", err=True)
            ctx.exit(1)
        target = f"{project_id}/{node}" if node else project_id
        click.echo(f"🔄 Restarting {target}...")
        stopped_nodes, stopped_spaces = _stop_project(r, project_id, node)
        click.echo(f"   Stopped: {stopped_nodes} nodes, {stopped_spaces} spaces")
        if not no_start:
            space_id, result = _start_project(ctx, r, project_id, node)
            if space_id:
                click.echo(f"✅ Started: {space_id}")
            else:
                click.echo(f"❌ Start failed: {result}")
        else:
            click.echo("✅ Stopped (--no-start)")
    else:
        click.echo("Error: specify PROJECT_ID or --all", err=True)
        ctx.exit(1)


@project.command('delete')
@click.argument('project_id')
@click.option('--force', is_flag=True, help='Force delete even with running spaces')
@click.pass_context
def delete_project(ctx, project_id, force):
    """Delete project and all its nodes"""
    r = ctx.obj['redis']
    
    proj_key = f'hfs:project:{project_id}'
    if not r.exists(proj_key):
        click.echo(f"Project not found: {project_id}", err=True)
        ctx.exit(1)
    
    # Check for running spaces
    running_count = 0
    for key in r.scan_iter('hfs:space:*'):
        data = r.get(key)
        if data:
            space = json.loads(data)
            if space.get('project_id') == project_id and space.get('status') in ('running', 'starting'):
                running_count += 1
    
    if running_count > 0 and not force:
        click.echo(f"Project has {running_count} running space(s)", err=True)
        click.echo("Use --force to delete anyway", err=True)
        ctx.exit(1)
    
    # Delete nodes
    node_count = 0
    for key in r.scan_iter(f'hfs:node:{project_id}:*'):
        r.delete(key)
        node_count += 1
    
    # Delete project
    r.delete(proj_key)
    
    # Delete stats
    r.delete(f'hfs:project:{project_id}:stats')
    r.delete(f'hfs:project:{project_id}:accounts')
    
    click.echo(f"✅ Deleted project: {project_id}")
    click.echo(f"   Deleted {node_count} nodes")
    
    if running_count > 0:
        click.echo(f"   ⚠️  Warning: {running_count} space(s) were running")

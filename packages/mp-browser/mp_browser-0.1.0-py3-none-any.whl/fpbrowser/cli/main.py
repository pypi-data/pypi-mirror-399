"""CLI implementation."""

import click
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .. import Browser, Profile, ProfileManager, get_config, __version__


def _parse_proxy_string(proxy: str) -> Optional[Dict[str, Any]]:
    """Parse proxy string.
    
    Args:
        proxy: Proxy string (e.g., "socks5://host:port" or "socks5://user:pass@host:port")
        
    Returns:
        Proxy config dict or None
    """
    if not proxy or "://" not in proxy:
        return None
    
    mode, rest = proxy.split("://", 1)
    
    # Parse username:password@host:port or host:port
    username, password = "", ""
    if "@" in rest:
        auth, host_port = rest.rsplit("@", 1)
        if ":" in auth:
            username, password = auth.split(":", 1)
    else:
        host_port = rest
    
    # Parse host:port
    if ":" in host_port:
        host, port_str = host_port.rsplit(":", 1)
        return {
            "mode": mode,
            "host": host,
            "port": int(port_str),
            "username": username,
            "password": password
        }
    
    return None


@click.group()
@click.version_option(version=__version__)
def cli():
    """fpbrowser - Lightweight fingerprint browser."""
    pass


# ===== Browser Commands =====

@cli.command()
@click.argument('profile', required=False)
@click.option('--temp', is_flag=True, help='Start temporary browser')
@click.option('--init', 'auto_create', is_flag=True, help='Auto-create profile if not found')
@click.option('--auto-download', is_flag=True, help='Auto-download from cloud if not found')
@click.option('--os', type=click.Choice(['windows', 'macos', 'linux']), help='OS for new profile')
@click.option('--language', help='Language for new profile')
@click.option('--proxy', 'use_proxy', is_flag=False, flag_value='USE_PROFILE', default=None, help='Proxy: --proxy (use profile default) or --proxy URL')
@click.option('--browser', 'browser_path', default=None, help='Use Chromium: "chromium" (auto-match version) or path')
@click.option('--headless', is_flag=True, help='Headless mode')
@click.option('--extension', 'extensions', multiple=True, help='Extension path')
@click.option('--daemon', is_flag=True, help='Run in background')
def start(profile, temp, auto_create, auto_download, os, language, use_proxy, browser_path, headless, extensions, daemon):
    """Start browser.
    
    Browser modes:
    - Default: Orbita with fingerprint injection
    - --browser chromium: Use Chromium (auto-match Orbita version)
    - --browser /path/to/chromium: Use specified Chromium
    
    Proxy modes:
    - No --proxy: Don't use proxy
    - --proxy: Use profile's default proxy
    - --proxy socks5://host:port: Use specified proxy
    """
    try:
        mode = "temp" if temp or not profile else "persistent"
        
        # Parse proxy parameter
        proxy_arg = None
        if use_proxy is not None:
            if use_proxy == 'USE_PROFILE':
                # --proxy without value → use profile default
                proxy_arg = True
            else:
                # --proxy <value> → use specified
                proxy_arg = use_proxy
        
        browser = Browser.start(
            profile=profile,
            mode=mode,
            auto_download=auto_download,
            auto_create=auto_create,
            os=os,
            language=language,
            use_proxy=proxy_arg,
            browser_path=browser_path,
            headless=headless,
            extensions=list(extensions) if extensions else None,
        )
        
        click.echo(f"Browser started: {browser.debugger_url}")
        
        if not daemon:
            click.echo("Press Ctrl+C to stop...")
            try:
                browser.wait()
            except KeyboardInterrupt:
                browser.stop()
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('profile', required=False)
@click.option('--all', 'stop_all', is_flag=True, help='Stop all browsers')
def stop(profile, stop_all):
    """Stop browser."""
    if stop_all:
        Browser.stop_all()
        click.echo("All browsers stopped")
    elif profile:
        # TODO: Implement profile-specific stop
        click.echo(f"Stopping profile: {profile}")
    else:
        click.echo("Please specify profile name or use --all")


# ===== Profile Commands =====

@cli.command('install')
@click.argument('component', required=False, type=click.Choice(['orbita', 'chromium', 'fonts']))
def install_browser(component):
    """Install browser components.
    
    Examples:
      fpbrowser install           # Install Orbita (default)
      fpbrowser install orbita    # Install Orbita browser
      fpbrowser install chromium  # Install Chromium browser
      fpbrowser install fonts     # Install fonts (for Docker/Linux)
    """
    try:
        # Default: install orbita
        if not component:
            component = 'orbita'
        
        if component == 'orbita':
            from ..utils.orbita_installer import OrbitaInstaller
            click.echo("📦 Installing Orbita browser (v141)...")
            installer = OrbitaInstaller()
            success = installer.install()
            if success:
                click.echo("✅ Orbita installed!")
                click.echo("Usage: fpbrowser start <profile>")
            else:
                click.echo("❌ Installation failed", err=True)
                sys.exit(1)
        
        elif component == 'chromium':
            from ..utils.chromium_installer import ChromiumInstaller
            click.echo("📦 Installing Chromium (v141)...")
            installer = ChromiumInstaller()
            success = installer.install()
            if success:
                click.echo("✅ Chromium installed!")
                click.echo("Usage: fpbrowser start <profile> --browser chromium")
            else:
                click.echo("❌ Installation failed", err=True)
                sys.exit(1)
        
        elif component == 'fonts':
            from ..utils.fonts_installer import FontsInstaller
            click.echo("📦 Installing fonts...")
            installer = FontsInstaller()
            success = installer.install()
            if success:
                click.echo("✅ Fonts installed!")
            else:
                click.echo("❌ Installation failed", err=True)
                sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def profile():
    """Profile management."""
    pass


@profile.command('create')
@click.argument('name')
@click.option('--os', type=click.Choice(['windows', 'macos', 'linux']), help='Operating system')
@click.option('--language', default='en-US', help='Language')
@click.option('--proxy', is_flag=False, flag_value='USE_DEFAULT', default=None, help='Proxy: --proxy (use default) or --proxy URL')
@click.option('--library', help='Import from S3 library (e.g., "id=5" or "os=macos" or empty for random)')
def profile_create(name, os, language, proxy, library):
    """Create new profile (generate or import from library).
    
    Proxy modes:
    - No --proxy: No proxy
    - --proxy: Use default proxy from config
    - --proxy socks5://xxx: Use specified proxy
    """
    try:
        config = get_config()
        
        # ===== 从 S3 指纹库导入 =====
        if library is not None:
            from fpbrowser.storage.s3_library import S3ProfileLibrary
            
            # 检查 S3 配置
            if not config.s3_config or not config.s3_config.get('bucket'):
                click.echo("❌ S3 未配置", err=True)
                sys.exit(1)
            
            lib = S3ProfileLibrary(
                bucket=config.s3_config['bucket'],
                prefix=config.s3_config.get('fingerprint_library_prefix', 'fingerprint-library')
            )
            
            if not lib.check_library_exists():
                click.echo("❌ 指纹库不存在", err=True)
                sys.exit(1)
            
            # 解析参数（支持复合条件，如 "os=macos,lang=en-US" 或 "id=5"）
            index = None
            os_filter = None
            lang_filter = None
            
            if library:  # 有参数
                # 解析多个条件（逗号分隔）
                conditions = [c.strip() for c in library.split(',')]
                for cond in conditions:
                    if '=' in cond:
                        key, val = cond.split('=', 1)
                        key = key.strip()
                        val = val.strip()
                        
                        if key == 'id':
                            index = int(val)
                            break  # id 优先，忽略其他条件
                        elif key == 'os':
                            os_filter = val
                        elif key == 'lang':
                            lang_filter = val
            
            # 确定 index
            if index is None:
                index = lib.get_random_index(os_filter=os_filter, lang_filter=lang_filter)
                if index is None:
                    click.echo("❌ 没有找到符合条件的 profile", err=True)
                    sys.exit(1)
            
            # 获取元数据
            metadata = lib.get_profile_metadata(index)
            if not metadata:
                click.echo(f"❌ Profile {index} 不存在", err=True)
                sys.exit(1)
            
            click.echo(f"📥 导入 profile-{index:03d}: {metadata.get('os')} / {metadata.get('language')}")
            
            # 导入
            if lib.import_profile(index, config.profiles_dir, name):
                click.echo(f"✅ 已导入为: {name}")
            else:
                click.echo(f"❌ 导入失败", err=True)
                sys.exit(1)
        
        # ===== 生成新指纹 =====
        else:
            # Determine proxy
            proxy_config = None
            if proxy is not None:
                if proxy == 'USE_DEFAULT':
                    # --proxy (no value) → use default
                    default_proxy = config.config_data.get('default_proxy')
                    if default_proxy:
                        proxy_config = _parse_proxy_string(default_proxy)
                    else:
                        click.echo("⚠️  No default proxy configured in ~/.fpbrowser/config.json")
                else:
                    # --proxy <value> → use specified
                    proxy_config = _parse_proxy_string(proxy)
            
            prof = Profile.create(
                name=name,
                os=os,
                language=language,
                proxy=proxy_config
            )
            prof.save(config.profiles_dir)
            
            click.echo(f"✅ Created profile: {name}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@profile.command('list')
@click.option('--remote', is_flag=True, help='List remote profiles')
@click.option('--temp', is_flag=True, help='Include temporary profiles')
@click.option('--library', is_flag=True, help='List S3 fingerprint library')
def profile_list(remote, temp, library):
    """List profiles."""
    try:
        # ===== S3 指纹库 =====
        if library:
            from fpbrowser.storage.s3_library import S3ProfileLibrary
            config = get_config()
            
            if not config.s3_config or not config.s3_config.get('bucket'):
                click.echo("❌ S3 未配置", err=True)
                sys.exit(1)
            
            lib = S3ProfileLibrary(
                bucket=config.s3_config['bucket'],
                prefix=config.s3_config.get('fingerprint_library_prefix', 'fingerprint-library')
            )
            
            if not lib.check_library_exists():
                click.echo("❌ 指纹库不存在", err=True)
                sys.exit(1)
            
            profiles = lib.list_profiles()
            manifest = lib.get_manifest()
            
            click.echo(f"\n📚 指纹库 ({manifest['total']} profiles)")
            click.echo(f"   s3://{lib.bucket}/{lib.prefix}/\n")
            
            for prof in profiles[:20]:
                idx = prof['index']
                os = prof.get('os', 'unknown')[:7]
                lang = prof.get('language', 'unknown')
                webgl = prof.get('webgl_vendor', 'unknown')[:25]
                
                click.echo(f"  [{idx:03d}] {os:7} | {lang:8} | {webgl}")
            
            if len(profiles) > 20:
                click.echo(f"\n  ... 还有 {len(profiles) - 20} 个")
            
            click.echo(f"\n使用: fpbrowser profile create <name> --library id={profiles[0]['index']}")
            return
        
        # ===== 远程 profiles =====
        if remote:
            manager = ProfileManager()
            profiles = manager.list_remote()
            click.echo("Remote profiles:")
            for prof in profiles:
                click.echo(f"  - {prof['name']}")
        
        # ===== 本地 profiles =====
        else:
            manager = ProfileManager()
            profiles = manager.list(include_temp=temp)
            click.echo(f"Local profiles ({len(profiles)}):")
            for prof in profiles:
                click.echo(f"  - {prof.name}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@profile.command('show')
@click.argument('name')
def profile_show(name):
    """Show profile details."""
    try:
        manager = ProfileManager()
        prof = manager.get(name)
        
        if not prof:
            click.echo(f"Profile '{name}' not found")
            sys.exit(1)
        
        import json
        click.echo(json.dumps(prof.to_dict(), indent=2))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@profile.command('update')
@click.argument('name')
@click.option('--proxy', 'proxy_url', is_flag=False, flag_value='USE_DEFAULT', default=None, help='Update proxy: --proxy (use default), --proxy URL, or --proxy none')
def profile_update(name, proxy_url):
    """Update profile configuration."""
    try:
        config = get_config()
        manager = ProfileManager()
        
        prof = manager.get(name)
        if not prof:
            click.echo(f"❌ Profile '{name}' not found", err=True)
            sys.exit(1)
        
        # Update proxy
        if proxy_url is not None:
            if proxy_url.lower() == 'none':
                # Remove proxy
                prof.config['proxy'] = {"mode": "none"}
                click.echo(f"✅ Removed proxy from profile: {name}")
            elif proxy_url == 'USE_DEFAULT':
                # Use default proxy
                default_proxy = config.config_data.get('default_proxy')
                if default_proxy:
                    proxy_config = _parse_proxy_string(default_proxy)
                    if proxy_config:
                        prof.config['proxy'] = proxy_config
                        click.echo(f"✅ Set proxy to default: {proxy_config['mode']}://{proxy_config['host']}:{proxy_config['port']}")
                else:
                    click.echo("⚠️  No default proxy configured in ~/.fpbrowser/config.json")
            else:
                # Use specified proxy
                proxy_config = _parse_proxy_string(proxy_url)
                if proxy_config:
                    prof.config['proxy'] = proxy_config
                    click.echo(f"✅ Updated proxy: {proxy_config['mode']}://{proxy_config['host']}:{proxy_config['port']}")
                else:
                    click.echo(f"❌ Invalid proxy format", err=True)
                    sys.exit(1)
            
            # Save
            prof.save(config.profiles_dir)
        else:
            click.echo("⚠️  No updates specified")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@profile.command('delete')
@click.argument('name')
@click.confirmation_option(prompt='Are you sure?')
def profile_delete(name):
    """Delete profile."""
    try:
        manager = ProfileManager()
        manager.delete(name)
        click.echo(f"✅ Deleted profile: {name}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@profile.command('upload')
@click.argument('name')
@click.option('--no-session', is_flag=True, help='Exclude session data')
def profile_upload(name, no_session):
    """Upload profile to cloud (includes session data by default)."""
    try:
        manager = ProfileManager()
        manager.upload(name, include_session=not no_session)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@profile.command('download')
@click.argument('name')
@click.option('--no-session', is_flag=True, help='Exclude session data')
@click.option('--force', is_flag=True, help='Force overwrite')
def profile_download(name, no_session, force):
    """Download profile from cloud (includes session data by default)."""
    try:
        manager = ProfileManager()
        manager.download(name, include_session=not no_session, force=force)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@profile.command('export')
@click.argument('name')
@click.argument('output')
def profile_export(name, output):
    """Export profile to file."""
    try:
        manager = ProfileManager()
        manager.export(name, output)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@profile.command('import')
@click.argument('input')
@click.option('--name', help='New profile name')
def profile_import(input, name):
    """Import profile from file."""
    try:
        manager = ProfileManager()
        manager.import_from(input, name)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ===== Config Commands =====

@cli.group()
def config():
    """Configuration management."""
    pass


@config.command('show')
def config_show():
    """Show configuration."""
    import json
    conf = get_config()
    click.echo(json.dumps(conf.to_dict(), indent=2))


@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set configuration value."""
    try:
        conf = get_config()
        
        # Try to parse as JSON (for nested values)
        try:
            import json
            value_parsed = json.loads(value)
        except:
            value_parsed = value
        
        conf.set(key, value_parsed)
        click.echo(f"✅ Set {key} = {value}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command('reset')
@click.confirmation_option(prompt='Reset configuration to default?')
def config_reset():
    """Reset configuration to default."""
    try:
        conf = get_config()
        conf.reset()
        click.echo("✅ Configuration reset")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ===== Cleanup Commands =====

@cli.command()
@click.option('--temp', is_flag=True, help='Cleanup temporary profiles')
@click.option('--older-than', default=7, help='Days old to cleanup')
def cleanup(temp, older_than):
    """Cleanup temporary profiles."""
    try:
        if temp:
            manager = ProfileManager()
            count = manager.cleanup_temp(older_than_days=older_than)
            click.echo(f"✅ Cleaned up {count} temporary profile(s)")
        else:
            click.echo("Please specify --temp")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()

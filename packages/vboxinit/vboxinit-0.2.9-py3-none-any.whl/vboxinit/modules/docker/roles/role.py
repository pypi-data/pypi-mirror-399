
from ..docker import * 


def setup_docker(
    conn: Connection,
    mirror: str = DEFAULT_MIRROR,
    version: str | None = None,
    username: str | None = None,
    daemon_config: dict | None = None,
) -> None:
    """一键安装和配置 Docker

    依次执行以下步骤:
    1. 卸载旧版本 Docker
    2. 安装依赖包
    3. 配置 GPG 密钥
    4. 配置 APT 源
    5. 安装 Docker CE
    6. 安装 Docker Compose
    7. 配置 daemon
    8. 启动并启用 Docker 服务
    9. 配置用户组

    Args:
        conn: Fabric 连接对象
        mirror: 镜像源名称 (official/cernet/tuna/aliyun/ustc) 或完整 URL
        version: Docker 版本号 (可选)，为空时安装最新版
        username: 添加到 docker 组的用户名，默认使用当前连接用户
        daemon_config: daemon.json 配置字典，默认使用 DEFAULT_DAEMON_CONFIG
    """
    print("=" * 60)
    print("Docker Installation - Starting")
    print("=" * 60)

    # region Step 1: 卸载旧版本
    print("\n[Step 1/9] Uninstalling old Docker packages...")
    uninstall_old_docker(conn)
    # endregion

    # region Step 2: 安装依赖
    print("\n[Step 2/9] Installing dependencies...")
    install_dependencies(conn)
    # endregion

    # region Step 3: 配置 GPG 密钥
    print("\n[Step 3/9] Setting up GPG key...")
    gpg_verified = setup_gpg_key(conn)
    # endregion

    # region Step 4: 配置 APT 源
    print("\n[Step 4/9] Setting up Docker repository...")
    setup_docker_repo(conn, mirror=mirror)
    # endregion

    # region Step 5: 安装 Docker
    print("\n[Step 5/9] Installing Docker CE...")
    install_docker(conn, version=version)
    # endregion

    # region Step 6: 安装 Docker Compose
    print("\n[Step 6/9] Installing Docker Compose...")
    install_docker_compose(conn)
    # endregion

    # region Step 7: 配置 daemon
    print("\n[Step 7/9] Configuring Docker daemon...")
    configure_daemon(conn, config=daemon_config)
    # endregion

    # region Step 8: 启动并启用服务
    print("\n[Step 8/9] Starting and enabling Docker service...")
    restart_docker(conn)
    enable_docker(conn)
    # endregion

    # region Step 9: 配置用户组
    print("\n[Step 9/9] Configuring Docker user group...")
    configure_docker_user(conn, username=username)
    # endregion

    # region 输出安装摘要
    print("\n" + "=" * 60)
    print("Docker Installation - Summary")
    print("=" * 60)
    print(f"  Mirror:       {DOCKER_MIRRORS.get(mirror, mirror)}")
    print(f"  Version:      {version or 'latest'}")
    print(f"  GPG Verified: {'Yes' if gpg_verified else 'No (warning)'}")
    print(f"  User:         {username or conn.user}")
    print("=" * 60)
    print("[OK] Docker installation completed successfully!")
    print("\nNote: You may need to log out and back in for group changes to take effect.")
    # endregion

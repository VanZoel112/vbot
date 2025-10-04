"""
VZ ASSISTANT v0.0.0.69
Docker Manager - Autonomous Container Deployment

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import aiodocker
from aiodocker.exceptions import DockerError
import os
import config

class DockerManager:
    """Manage Docker containers for sudoers."""

    def __init__(self):
        """Initialize Docker manager."""
        self.docker = None

    async def connect(self):
        """Connect to Docker daemon."""
        try:
            self.docker = aiodocker.Docker()
            # Test connection
            await self.docker.version()
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Docker: {e}")
            return False

    async def close(self):
        """Close Docker connection."""
        if self.docker:
            await self.docker.close()

    async def build_image(self):
        """Build VZ Assistant base image if not exists."""
        try:
            # Check if image exists
            try:
                await self.docker.images.inspect("vz-assistant:latest")
                print("✅ VZ Assistant image already exists")
                return True
            except DockerError:
                pass

            # Build image
            print("🔨 Building VZ Assistant Docker image...")

            # Create tar archive for build context
            import tarfile
            import io

            # Files to include in build
            files_to_include = [
                "Dockerfile.sudoer",
                "requirements.txt",
                "main.py",
                "client.py",
                "config.py",
                "plugins/",
                "helpers/",
                "database/",
                "utils/",
                "emojiprime.json"
            ]

            # Create tar in memory
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                for item in files_to_include:
                    if os.path.exists(item):
                        tar.add(item, arcname=item)
                # Add Dockerfile as "Dockerfile" (required name)
                tar.add("Dockerfile.sudoer", arcname="Dockerfile")

            tar_stream.seek(0)

            # Build image
            build_log = []
            async for line in self.docker.images.build(
                fileobj=tar_stream,
                encoding="application/x-tar",
                tag="vz-assistant:latest"
            ):
                if 'stream' in line:
                    print(line['stream'].strip())
                    build_log.append(line['stream'])

            print("✅ Docker image built successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to build image: {e}")
            return False

    async def create_sudoer_container(
        self,
        user_id: int,
        session_string: str,
        username: str = None,
        first_name: str = None
    ):
        """
        Create and start a Docker container for sudoer.

        Args:
            user_id: Telegram user ID
            session_string: Telethon session string
            username: User's username
            first_name: User's first name

        Returns:
            tuple: (success: bool, message: str, container_id: str)
        """
        try:
            container_name = f"vz-sudoer-{user_id}"

            # Check if container already exists
            try:
                existing = await self.docker.containers.get(container_name)
                # Stop and remove existing
                await existing.stop()
                await existing.delete()
                print(f"🗑️  Removed existing container: {container_name}")
            except DockerError:
                pass

            # Container configuration
            config_dict = {
                "Image": "vz-assistant:latest",
                "name": container_name,
                "Env": [
                    f"SESSION_STRING={session_string}",
                    f"USER_ID={user_id}",
                    f"API_ID={config.API_ID}",
                    f"API_HASH={config.API_HASH}",
                    f"USERNAME={username or 'None'}",
                    f"FIRST_NAME={first_name or 'User'}"
                ],
                "HostConfig": {
                    "RestartPolicy": {"Name": "unless-stopped"},
                    "NetworkMode": "bridge",
                    # Mount volumes for persistent data
                    "Binds": [
                        f"{os.path.abspath('database/sudoers')}:/app/database/sudoers",
                        f"{os.path.abspath('sessions')}:/app/sessions"
                    ]
                },
                "Labels": {
                    "vz.assistant.sudoer": "true",
                    "vz.assistant.user_id": str(user_id),
                    "vz.assistant.username": username or "unknown"
                }
            }

            # Create container
            print(f"🐳 Creating container: {container_name}")
            container = await self.docker.containers.create(config=config_dict)

            # Start container
            print(f"▶️  Starting container: {container_name}")
            await container.start()

            # Get container info
            info = await container.show()
            container_id = info['Id'][:12]

            print(f"✅ Container started: {container_name} ({container_id})")

            return True, f"Container deployed successfully", container_id

        except DockerError as e:
            error_msg = f"Docker error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Deployment error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg, None

    async def get_container_status(self, user_id: int):
        """Get status of sudoer container."""
        try:
            container_name = f"vz-sudoer-{user_id}"
            container = await self.docker.containers.get(container_name)
            info = await container.show()

            return {
                "exists": True,
                "running": info['State']['Running'],
                "status": info['State']['Status'],
                "id": info['Id'][:12],
                "started_at": info['State']['StartedAt']
            }
        except DockerError:
            return {"exists": False}
        except Exception as e:
            print(f"⚠️  Error checking container status: {e}")
            return {"exists": False, "error": str(e)}

    async def stop_container(self, user_id: int):
        """Stop sudoer container."""
        try:
            container_name = f"vz-sudoer-{user_id}"
            container = await self.docker.containers.get(container_name)
            await container.stop()
            return True, "Container stopped"
        except Exception as e:
            return False, f"Failed to stop: {str(e)}"

    async def remove_container(self, user_id: int, force: bool = False):
        """Remove sudoer container."""
        try:
            container_name = f"vz-sudoer-{user_id}"
            container = await self.docker.containers.get(container_name)
            await container.delete(force=force)
            return True, "Container removed"
        except Exception as e:
            return False, f"Failed to remove: {str(e)}"

    async def list_sudoer_containers(self):
        """List all VZ Assistant sudoer containers."""
        try:
            filters = {"label": "vz.assistant.sudoer=true"}
            containers = await self.docker.containers.list(filters=filters)

            result = []
            for container in containers:
                info = await container.show()
                result.append({
                    "id": info['Id'][:12],
                    "name": info['Name'].lstrip('/'),
                    "user_id": info['Config']['Labels'].get('vz.assistant.user_id'),
                    "username": info['Config']['Labels'].get('vz.assistant.username'),
                    "status": info['State']['Status'],
                    "running": info['State']['Running']
                })

            return result
        except Exception as e:
            print(f"⚠️  Error listing containers: {e}")
            return []

# Global instance
docker_manager = DockerManager()

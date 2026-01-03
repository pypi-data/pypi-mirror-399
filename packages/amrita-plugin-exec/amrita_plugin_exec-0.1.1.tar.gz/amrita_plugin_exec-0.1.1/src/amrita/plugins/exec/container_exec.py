import docker
from docker.errors import DockerException, ImageNotFound
from nonebot import logger


async def pull_image(image_name: str):
    try:
        client = docker.from_env()
        client.images.pull(image_name)
        return True
    except DockerException as e:
        print(f"Failed to pull image: {e}")
        return False

async def execute_in_docker(*cmd_parts):
    image_name = "alpine:latest"
    try:
        client = docker.from_env()
        # 将命令部分组合成完整的命令字符串
        cmd_text = " ".join(cmd_parts)
        container = client.containers.run(
            image_name,
            f"sh -c '{cmd_text}'",
            detach=True,
            remove=False,
            network_mode="none",
            mem_limit="128m",
            cpu_period=100000,
            cpu_quota=50000,
            pids_limit=100,
            read_only=True,
            security_opt=["no-new-privileges:true"],
        )

        try:
            result = container.wait(timeout=10)
            logs = container.logs().decode("utf-8")
            exit_code = result.get("StatusCode", 0)
            container.remove(force=True)
            return logs, exit_code
        except DockerException as e:
            print(f"Failed to get container logs: {e}")
            container.remove(force=True)
            return "", 1
    except ImageNotFound:
        logger.warning(f"Image {image_name} not found. Pulling...")
        await pull_image(image_name)
        return await execute_in_docker(*cmd_parts)
    except DockerException as e:
        logger.error(f"Failed to run container: {e}")
        return f"Docker执行失败: {e}", 1
"""CLI entrypoint for the Picture Display Skill."""

import asyncio
import pathlib
from typing import Annotated

import jinja2
import typer
from private_assistant_commons import mqtt_connection_handler, skill_config, skill_logger
from private_assistant_commons.database import PostgresConfig
from sqlalchemy.ext.asyncio import create_async_engine

from private_assistant_picture_display_skill.config import PictureSkillConfig
from private_assistant_picture_display_skill.models.device import DeviceDisplayState
from private_assistant_picture_display_skill.models.image import Image
from private_assistant_picture_display_skill.picture_skill import PictureSkill

app = typer.Typer(help="Picture Display Skill for Inky e-ink devices")


@app.command()
def main(config_path: Annotated[pathlib.Path, typer.Argument(envvar="PRIVATE_ASSISTANT_CONFIG_PATH")]) -> None:
    """Run the Picture Display Skill.

    Args:
        config_path: Path to YAML configuration file or directory
    """
    asyncio.run(start_skill(config_path))


async def start_skill(config_path: pathlib.Path) -> None:
    """Start the Picture Display Skill with all required services.

    Args:
        config_path: Path to YAML configuration file or directory
    """
    # Set up logger early on
    logger = skill_logger.SkillLogger.get_logger("Private Assistant PictureSkill")

    # Load configuration from YAML
    config_obj = skill_config.load_config(config_path, PictureSkillConfig)

    # Create async database engine
    # AIDEV-NOTE: PostgresConfig uses environment variables (POSTGRES_*)
    db_config = PostgresConfig()
    db_engine_async = create_async_engine(db_config.connection_string_async)

    # Create only skill-specific tables, not all SQLModel metadata
    # AIDEV-NOTE: Global device registry tables are managed by BaseSkill and commons
    async with db_engine_async.begin() as conn:
        # __table__ is a SQLAlchemy runtime attribute that mypy doesn't recognize
        for table in [Image.__table__, DeviceDisplayState.__table__]:  # type: ignore[attr-defined]
            await conn.run_sync(table.create, checkfirst=True)

    logger.info("Database tables initialized for Picture Display Skill")

    # Set up Jinja2 template environment
    template_env = jinja2.Environment(
        loader=jinja2.PackageLoader("private_assistant_picture_display_skill", "templates"),
        autoescape=True,
    )

    # Start the skill using the async MQTT connection handler
    # AIDEV-NOTE: mqtt_connection_handler manages MQTT lifecycle with auto-reconnect
    await mqtt_connection_handler.mqtt_connection_handler(
        PictureSkill,
        config_obj,
        retry_interval=5,
        logger=logger,
        template_env=template_env,
        engine=db_engine_async,
    )


if __name__ == "__main__":
    app()

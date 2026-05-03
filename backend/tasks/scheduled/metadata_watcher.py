from config import (
    ENABLE_SCHEDULED_METADATA_WATCHER,
    SCHEDULED_METADATA_WATCHER_CRON,
)
from handler.database import db_rom_handler
from handler.metadata import meta_igdb_handler
from logger.logger import log
from tasks.tasks import PeriodicTask, TaskType
from utils.context import initialize_context


class MetadataWatcherTask(PeriodicTask):
    def __init__(self):
        super().__init__(
            title="Scheduled metadata watcher",
            description="Enriches ROMs missing all metadata IDs via IGDB",
            task_type=TaskType.WATCHER,
            enabled=ENABLE_SCHEDULED_METADATA_WATCHER,
            manual_run=False,
            cron_string=SCHEDULED_METADATA_WATCHER_CRON,
            func="tasks.scheduled.metadata_watcher.metadata_watcher_task.run",
        )

    @initialize_context()
    async def run(self) -> None:
        if not ENABLE_SCHEDULED_METADATA_WATCHER:
            self.unschedule()
            return

        if not meta_igdb_handler.is_enabled():
            return

        roms = db_rom_handler.get_roms_without_metadata()
        if not roms:
            return

        log.info(f"Metadata watcher: found {len(roms)} ROM(s) without metadata")

        matched = 0
        for rom in roms:
            platform_igdb_id = getattr(rom.platform, "igdb_id", None)
            if not platform_igdb_id:
                db_rom_handler.mark_metadata_checked(rom.id)
                continue

            try:
                igdb_rom = await meta_igdb_handler.get_rom(rom.fs_name, platform_igdb_id)
            except Exception:
                log.error(
                    f"Metadata watcher: error fetching IGDB data for {rom.fs_name}",
                    exc_info=True,
                )
                continue

            if igdb_rom.get("igdb_id"):
                update_data = {
                    k: v
                    for k, v in igdb_rom.items()
                    if v is not None and v != [] and v != {}
                }
                db_rom_handler.update_rom(rom.id, update_data)
                matched += 1
            else:
                db_rom_handler.mark_metadata_checked(rom.id)

        log.info(
            f"Metadata watcher: processed {len(roms)} ROM(s), matched {matched}"
        )


metadata_watcher_task = MetadataWatcherTask()

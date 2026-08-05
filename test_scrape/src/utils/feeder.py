from pathlib import Path

def build_feed(
    export_dir,
    spider_name,
    export_format,
    batch_size,
    delimiter       # for csv
):
    feed = {
        str(Path(export_dir) / f"{spider_name}_%(batch_id)03d.{export_format}"): {
            "format": export_format,
            "batch_item_count": batch_size,
        }
    }

    if export_format == "csv":
        feed[next(iter(feed))]["item_export_kwargs"] = {
            "delimiter": delimiter,
        }

    return feed
""" import traceback

from scrapy.exceptions import DropItem


class DuplicatePipeline:

    def open_spider(self, spider):

        self.upcs = set()

        spider.logger.info(
            "DuplicatePipeline initialized."
        )

    def process_item(self, item, spider):

        try:

            upc = getattr(item, "upc", None)

            if upc is None:
                raise DropItem(
                    "UPC is required for duplicate checking."
                )

            if upc in self.upcs:

                raise DropItem(
                    f"Duplicate UPC detected: {upc}"
                )

            self.upcs.add(upc)

            spider.logger.info(
                f"Duplicate check passed: {item.title}"
            )

            return item

        except DropItem as e:

            spider.logger.warning(
                str(e)
            )

            raise

        except Exception as e:

            spider.logger.error(
                f"Unexpected error in DuplicatePipeline: {e}"
            )

            spider.logger.error(
                traceback.format_exc()
            )

            raise

    def close_spider(self, spider):

        spider.logger.info(
            f"DuplicatePipeline closed. "
            f"Total unique UPC: {len(self.upcs)}"
        )


class IncrementalPipeline:
    pass


class ChangeDetectionPipeline: 
    pass


class AnomalyDetectionPipeline:
    pass """
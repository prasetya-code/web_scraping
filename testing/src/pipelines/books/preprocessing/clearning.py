from .base import BasePipe

from dataclasses import fields

class CleaningPipe(BasePipe):
    """
    - Bertugas membersihkan seluruh field string agar tidak memiliki whitespace di awal maupun akhir.
    - Cleaning dilakukan terlebih dahulu karena pipeline setelahnya mengasumsikan data sudah bersih.
    """

    def process_item(self, item, spider):

        try:

            # Menggunakan dataclasses.fields() membuat pipeline ini otomatis bekerja walaupun nanti jumlah field bertambah.
            for field in fields(item):

                value = self.get_value(item, field.name,)

                # Hanya string yang perlu dibersihkan.
                if not isinstance(value, str):
                    continue

                self.set_value(item, field.name, value.strip())

            self.log_success(spider, item)

            return item

        except Exception:

            self.log_exception(spider)
            raise
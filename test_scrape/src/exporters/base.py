from abc import ABC, abstractmethod


class BaseExporter(ABC):

    @abstractmethod
    def open(self, spider):
        """
        Bertugas menyiapkan resource yang diperlukan sebelum proses export dimulai, misalnya:

            - Membuat direktori.
            - Membuka file.
            - Membuat koneksi database.
            - Menyiapkan writer atau serializer.
        """
        pass

    @abstractmethod
    def export_item(self, item):
        """
        Method ini bertugas menulis satu item ke media tujuan, misalnya:

            - Menambah satu baris pada file CSV.
            - Menambahkan object ke file JSON.
            - Menulis node XML.
            - Melakukan INSERT ke database.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Bertugas menutup seluruh resource yang sebelumnya dibuka, misalnya:

            - Menutup file.
            - Menyimpan buffer terakhir.
            - Commit transaksi database.
            - Menutup koneksi database.

        Tujuannya agar seluruh data tersimpan dengan benar dan resource sistem dilepaskan.
        """
        pass
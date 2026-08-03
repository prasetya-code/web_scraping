from .format.csv import CsvExporter
from .format.json import JsonExporter


class ExporterFactory:
    """
    - Factory yang bertugas membuat object exporter berdasarkan format export yang dipilih pada custom_settings spider.
    - Adanya Factory, ExportPipeline tidak perlu melakukan banyak percabangan (if / elif) setiap kali ingin memilih exporter.
    """

    # Key HARUS sama dengan nilai EXPORT_FORMAT pada custom_settings spider.
    EXPORTERS = {
        "csv": CsvExporter,
        "json": JsonExporter,
    }

    @classmethod
    def create(cls, export_format, export_dir,):
        """
        Membuat instance exporter sesuai format yang dipilih.

        Parameters
        ----------
        export_format
            Format export yang berasal dari custom_settings spider.

        export_dir
            Direktori tujuan penyimpanan hasil export.
        """

        try:

            # Mengambil class exporter dari dictionary.
            exporter = cls.EXPORTERS[
                export_format.lower()
            ]

        except KeyError:

            # Apabila format tidak ditemukan di dictionary, berarti exporter tersebut belum tersedia.
            raise ValueError(
                f"Format export '{export_format}' belum didukung."
            )

        return exporter(export_dir)
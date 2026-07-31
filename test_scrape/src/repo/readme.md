untuk mengatasi multi export `(.csv, .json, .db, database)` agar bisa menerapkan:
```bash
├── detection.py
│     ├── DuplicatePipeline
│     ├── IncrementalPipeline
│     ├── ChangeDetectionPipeline
│     └── AnomalyDetectionPipeline
```

maka diperlukan dir khusus repo yang nantinya akan disimpan di `storage/data/nama_export.ext`
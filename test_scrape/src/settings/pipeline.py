ITEM_PIPELINES = {

    # Preparation Process
    "src.pipelines.preprocessing.ValidationPipe": 100,

    "src.pipelines.preprocessing.CleaningPipe": 110,

    "src.pipelines.preprocessing.DataTypePipe": 120,

    "src.pipelines.preprocessing.NormalizationPipe": 130,

    "src.pipelines.preprocessing.QualityCheckPipe": 140,


    # Detection Process

    # "src.pipelines.duplicate.DuplicatePipeline":200,


    # Asset Process
    "src.pipelines.assets.BookImagesPipe":300,


    # ETL Process

    # "src.pipelines.transform.TransformationPipeline":600,


    # Export Process
    "src.pipelines.export.ExportPipe": 800,
}

# IMAGES_THUMBS = {
#     "small": (50, 50),
#     "medium": (200, 200),
# }
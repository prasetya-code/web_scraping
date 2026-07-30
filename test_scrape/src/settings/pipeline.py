ITEM_PIPELINES = {

    # Preparation Process
    "src.pipelines.preprocessing.ValidationPipe": 100,

    "src.pipelines.preprocessing.CleaningPipe": 110,

    "src.pipelines.preprocessing.TypePipe": 120,

    "src.pipelines.preprocessing.NormalizationPipe": 130,


    # Detection Process

    # "src.pipelines.duplicate.DuplicatePipeline":400,


    # Asset Process

    # "src.pipelines.assets.BookImagesPipeline":500,


    # ETL Process

    # "src.pipelines.transform.TransformationPipeline":600,
}

# IMAGES_THUMBS = {
#     "small": (50, 50),
#     "medium": (200, 200),
# }
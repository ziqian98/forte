# Copyright 2019 The Forte Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
The reader that reads QA-SRL Bank 2.0 data into data pack.
Data Overview:
https://www.kaggle.com/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
Data Format:
https://www.kaggle.com/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews
"""
import logging
import os
from typing import Iterator
from forte.common.exception import ProcessorConfigError
from forte.common.configuration import Config
from forte.common.resources import Resources
from forte.data.data_utils_io import dataset_path_iterator
from forte.data.data_pack import DataPack
from forte.data.readers.base_reader import PackReader
from ft.onto.base_ontology import Sentence, Document


__all__ = [
    "IMDBReader"
]


class IMDBReader(PackReader):
    r""":class:`IMDBReader` is designed to read
        in the imdb review dataset used
        by sentiment classification task.
        The Original data format:
        "movie comment, positive"
        "movie comment, negative"
    """

    def initialize(self, resources: Resources, configs: Config):
        super().initialize(resources, configs)

        if configs.imdb_file_extension is None:
            raise ProcessorConfigError(
                "Configuration qa_file_extension not provided.")

    def _collect(self, *args, **kwargs) -> Iterator[str]:
        # pylint: disable = unused-argument
        r"""Iterator over text files in the data_source

        Args:
            args: args[0] is the directory to the .imdb files.
            kwargs:

        Returns: Iterator over files in the path with imdb extensions.
        """

        imdb_directory: str = args[0]

        imdb_file_extension: str = self.configs.imdb_file_extension

        logging.info("Reading dataset from %s with extension %s",
                     imdb_directory, imdb_file_extension)
        return dataset_path_iterator(imdb_directory, imdb_file_extension)

    def _cache_key_function(self, imdb_file: str) -> str:
        return os.path.basename(imdb_file)

    def _parse_pack(self, file_path: str) -> Iterator[DataPack]:
        pack: DataPack = self.new_pack()
        text: str = ""
        offset: int = 0

        with open(file_path, "r", encoding="utf8") as f:
            for line in f:
                line = line.strip()
                if line != "":
                    line_list = line.split("\",")
                    sentence = line_list[0].strip("\"")
                    sentiment = line_list[1]
                    # Add sentence.

                    #only for binary sentiment classification
                    sentiment_score  = -1.0
                    if sentiment == "positive":
                        sentiment_score = 1.0

                    senobj = Sentence(pack, offset, offset + len(sentence))

                    senobj.sentiment[sentence] = sentiment_score

                    # For \n
                    offset += len(line) + 1
                    text += line + " "

        pack.set_text(text, replace_func=self.text_replace_operation)

        Document(pack, 0, len(text))

        pack.pack_name = file_path

        yield pack

    @classmethod
    def default_configs(cls):
        config: dict = super().default_configs()
        # Add imdb dataset file extension. The default is '.imdb'
        config.update({'imdb_file_extension': 'imdb'})
        return config

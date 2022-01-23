import json
from pathlib import Path
from typing import Union

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """Generate chat statistics from a telegram chat json file
    """
    def __init__(self, chat_json: Union[str, Path]):
        """
        :param chat_json: [path to telegram export json file]
        """

        # load chat data
        logger.info(f"Loading chat data from{chat_json}")
        with open(chat_json) as f:
            self.chat_data = json.load(f)

        self.normalizer = Normalizer()

        # load stop words
        logger.info(f"Loading stopwords from {DATA_DIR / 'stopwords.txt'}")
        stop_words = open(DATA_DIR / 'stopwords.txt').readlines()
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = list(map(self.normalizer.normalize, stop_words))

    def generate_word_cloud(
        self,
        output_dir: Union[str, Path],
        width: int = 800, height: int = 600,
        max_font_size: int = 60,
    ):

        """Generate a word cloud from the chat data

        :param output_dir: path to output directory for word cloud image
        """
        logger.info("Loadind text content...")
        text_content = ''

        for msg in self.chat_data['messages']:
            if type(msg['text']) is str:
                tokens = word_tokenize(msg['text'])
                tokens = list(filter(lambda item: item not in self.stop_words, tokens))
                text_content += f" {' '.join(tokens)}"

        # normalize, reshape for final word cloud
        text_content = self.normalizer.normalize(text_content)
        text_content = arabic_reshaper.reshape(text_content)
        text_content = get_display(text_content)

        logger.info("Generating word cloud...")
        # generate word cloud
        wordcloud = WordCloud(
            font_path=str(DATA_DIR / './BHoma.ttf'),
            background_color='white',
            max_font_size=60, width=450,
            height=250,
        ).generate(text_content)

        logger.info(f"Saving word cloud to {output_dir}")
        wordcloud.to_file(Path(output_dir) / 'wordcloud.png')


if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=DATA_DIR / 'Python_OG.json')
    chat_stats.generate_word_cloud(output_dir=DATA_DIR)

print('Done!')

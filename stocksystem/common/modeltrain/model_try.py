from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import warnings


def test() :
    semantic_cls = pipeline(Tasks.text_classification, 'damo/nlp_structbert_sentiment-classification_chinese-base')
    # semantic_cls(input='启动的时候很大声音，然后就会听到1.2秒的卡察的声音，类似齿轮摩擦的声音')
    # print(semantic_cls(input='启动的时候很大声音，然后就会听到1.2秒的卡察的声音，类似齿轮摩擦的声音'))
    print(semantic_cls(input='预测今年的股票会涨'))


if __name__ == '__main__':
    warnings.filterwarnings("ignore", category=FutureWarning)
    test()

import yake

def extract_keywords(text, top_n=5, lan="en"):
    """
    Extracts keywords using YAKE.
    :param text: input string
    :param top_n: number of keywords to extract
    :param lan: language
    :return: list of keywords
    """
    kw_extractor = yake.KeywordExtractor(lan=lan, n=1, top=top_n)
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, _ in keywords]

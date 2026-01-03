############################################################
## Functions for constructional diversity metrics
############################################################

import sys
import numpy as np
import more_itertools
from collections import Counter
from scipy.stats import hypergeom

def type_token_ratio(tokens):
    return len(set(tokens)) / len(tokens) if tokens else 0.0


def moving_window_ttr(tokens, window_size=10):
    if len(tokens) < window_size:
        return "NA"  # better than "NA" for numeric analysis
    windows = list(more_itertools.windowed(tokens, n=window_size, step=1))
    scores = [type_token_ratio(list(filter(None, window))) for window in windows]
    return sum(scores) / len(scores)


def measure_of_textual_lexical_diversity_original(tokens, threshold=0.72):
    terms = set()
    token_count = 0
    factor_count = 0

    for word in tokens:
        token_count += 1
        terms.add(word)
        ttr = len(terms) / token_count

        if ttr <= threshold:
            factor_count += 1
            terms = set()
            token_count = 0

    if token_count > 0:
        partial_factor = (1 - ttr) / (1 - threshold)
        factor_count += partial_factor

    return len(tokens) / factor_count if factor_count != 0 else "NA"


def measure_of_textual_lexical_diversity_bidirectional(tokens, threshold=0.72):

    def sub_mtld(tokens, threshold, reverse=False):
        word_iterator = iter(reversed(tokens)) if reverse else iter(tokens)
        terms = set()
        word_counter = 0
        factor_count = 0

        for word in word_iterator:
            word_counter += 1
            terms.add(word)
            ttr = len(terms) / word_counter

            if ttr <= threshold:
                word_counter = 0
                terms = set()
                factor_count += 1

        if word_counter > 0:
            factor_count += (1 - ttr) / (1 - threshold)

        if factor_count == 0:
            ttr = len(terms) / len(tokens)
            factor_count += 1 if ttr == 1 else (1 - ttr) / (1 - threshold)

        return len(tokens) / factor_count

    forward_measure = sub_mtld(tokens, threshold, reverse=False)
    reverse_measure = sub_mtld(tokens, threshold, reverse=True)

    return np.mean((forward_measure, reverse_measure))


def measure_of_textual_lexical_diversity_ma_wrap(tokens, threshold=0.72):
    terms = set()
    token_count = 0
    factor_count = 0
    i = 0
    text_length = len(tokens)

    while i < text_length * 2:  # wrap around once
        word = tokens[i % text_length]
        token_count += 1
        terms.add(word)
        ttr = len(terms) / token_count

        if ttr <= threshold:
            factor_count += 1
            token_count = 0
            terms = set()

        i += 1

    return (text_length * 2) / factor_count if factor_count != 0 else "NA"


def Hypergeometric_distribution_diversity(tokens, draws=10):
    token_frequency = len(tokens)
    type_frequency = len(set(tokens))

    suggestion = token_frequency // 2 if type_frequency < 10 else 10

    if token_frequency < draws:
        return "NA"

    if draws < 1 or isinstance(draws, float):
        raise ValueError(
            f"Number of draws must be a positive integer. E.g. hdd(draws={suggestion})"
        )

    term_freq = Counter(tokens)

    term_contributions = [
        (1 - hypergeom.pmf(0, token_frequency, freq, draws)) / draws
        for _, freq in term_freq.items()
    ]

    return sum(term_contributions)

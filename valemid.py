# MTLD, HDD, MSTTR arvutamine
import sys
from cmath import nan
import numpy as np
import math

def mtld_calc(word_array, ttr_threshold):
    current_ttr = 1.0
    token_count = 0
    type_count = 0
    types = set()
    factors = 0.0
    
    for token in word_array:
        token = token.text.lower() 
        token_count = token_count + 1
        if token not in types:
            type_count = type_count + 1
            types.add(token)
        current_ttr = type_count / token_count
        if current_ttr <= ttr_threshold:
            factors = factors + 1
            token_count = 0
            type_count = 0
            types = set()
            current_ttr = 1.0
    
    excess = 1.0 - current_ttr
    excess_val = 1.0 - ttr_threshold
    factors += excess / excess_val
    if factors != 0:
        return len(word_array) / factors
    return -1

# combination of n by r:  nCr = n! / r!(n - r)!
def combination(n, r):
    return math.comb(int(n), int(r))
   

# hypergeometric probability: the probability that an n-trial hypergeometric experiment results 
#  in exactly x successes, when the population consists of N items, k of which are classified as successes.
#  (here, population = N, population_successes = k, sample = n, sample_successes = x)
#  h(x; N, n, k) = [ kCx ] * [ N-kCn-x ] / [ NCn ]
def hypergeometric(population, population_successes, sample, sample_successes):
    x = combination(population_successes, sample_successes)
    y = combination(population - population_successes, sample - sample_successes)
    z = combination(population, sample)

    try:
        return (x * y) / z
    except:
        raise ValueError("Error while computing hypergeometric probability")
    
    
# HD-D implementation
def hdd(word_array, sample_size = 42):
    if isinstance(word_array, str):
        raise ValueError("Input should be a list of strings, rather than a string. Try using string.split()")
    if len(word_array) < 50:
        raise ValueError("Input word list should be at least 50 in length")

    # Create a dictionary of counts for each type
    type_counts = {}
    for token in word_array:
        token = token.text.lower() #make lowercase
        if token in type_counts:
            type_counts[token] = type_counts[token] + 1
        else:
            type_counts[token] = 1

    # Sum the contribution of each token - "If the sample size is 42, the mean contribution of any given
    #  type is 1/42 multiplied by the percentage of combinations in which the type would be found." (McCarthy & Jarvis 2010)
    
    hdd_value = 0
    for token_type in type_counts.keys():
        contribution = (1 - hypergeometric(len(word_array), sample_size, type_counts[token_type], 0)) / sample_size
        hdd_value = hdd_value + contribution

    return hdd_value

def safe_divide(numerator, denominator):
	if denominator == 0 or denominator == 0.0:
		index = 0
	else: index = numerator/denominator
	return index

def msttr(text, window_length = 50):

	if len(text) < (window_length + 1):
		ms_ttr = safe_divide(len(set(text)), len(text))

	else:
		sum_ttr = 0
		denom = 0

		n_segments = int(safe_divide(len(text), window_length))
		seed = 0
		for x in range(n_segments):
			sub_text = text[seed:seed+window_length]
			#print sub_text
			sum_ttr = sum_ttr + safe_divide(len(set(sub_text)), len(sub_text))
			denom = denom + 1
			seed = seed + window_length

		ms_ttr = safe_divide(sum_ttr, denom)

	return ms_ttr
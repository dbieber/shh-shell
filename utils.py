def sayable_datetime(dt):
    return dt.strftime('%A, %B %e %l:%M%p')

def fuzzy_distance(typed, target):
    return 0 if typed == target else 1

def fuzzy_select(needle, haystack):

    def distance_to_needle(item):
        return fuzzy_distance(needle, item)

    scores = map(distance_to_needle, haystack)
    ranked = sorted(zip(scores, haystack), key=lambda pair: pair[0])

    # TODO(Bieber): Do some sort of thresholding and maybe return multiple results
    return ranked[0][1]

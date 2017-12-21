from flask_unchained.clips_pattern import pluralize, singularize, ADJECTIVE


class TestPluralize:
    def test_custom(self):
        assert pluralize('foobar', custom={'foobar': 'foos'}) == 'foos'

    def test_basic(self):
        assert pluralize('bird') == 'birds'
        assert pluralize('man') == 'men'
        assert pluralize('woman') == 'women'

    def test_trailing_apostrophe(self):
        assert pluralize("dave's") == "daves'"
        assert pluralize("woman's") == "women's"

    def test_recursive_compound_words(self):
        assert pluralize('mother-in-law') == 'mothers-in-law'
        assert pluralize('postmaster general') == 'postmasters general'
        assert pluralize('hour-clock') == 'hour-clocks'

    def test_pluralization_rules(self):
        assert pluralize('my', pos=ADJECTIVE) == 'our'
        assert pluralize('thy', pos=ADJECTIVE) == 'your'
        assert pluralize('matrix') == 'matrices'
        assert pluralize('matrix', classical=False) == 'matrixes'
        assert pluralize('datum') == 'data'
        assert pluralize('datum', classical=False) == 'data'


class TestSingularize:
    def test_custom(self):
        assert singularize('foobar', custom={'foobar': 'foo'}) == 'foo'

    def test_basic(self):
        assert singularize('birds') == 'bird'
        assert singularize('women') == 'woman'

    def test_trailing_apostrophe(self):
        assert singularize("dogs'") == "dog's"

    def test_compound(self):
        assert singularize('mothers-in-law') == 'mother-in-law'
        assert singularize('hour-clocks') == 'hour-clock'

    def test_uninflected(self):
        assert singularize('bison') == 'bison'

    def test_uncountable(self):
        assert singularize('advice') == 'advice'

    def test_ie(self):
        assert singularize('alergies') == 'alergie'
        assert singularize('cookies') == 'cookie'

    def test_irregular(self):
        assert singularize('children', 'child')

    def test_inflection(self):
        assert singularize('oxen') == 'ox'
        assert singularize('larvae') == 'larva'
        assert singularize('analyses') == 'analysis'
        assert singularize('wolves') == 'wolf'
